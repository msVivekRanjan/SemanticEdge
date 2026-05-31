import os
import sys
import shutil
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

import cv2
import json
import time
import httpx
import asyncio
import sqlite3
import threading
import queue
from datetime import datetime, timezone
import numpy as np
from dotenv import load_dotenv
import supervision as sv

from ultralytics import YOLO
import base64
from PIL import Image
import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "local_buffer.db")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/events")
FRAMES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frames"))
os.makedirs(FRAMES_DIR, exist_ok=True)

def reset_storage():
    print("Resetting local storage for demo...")
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Deleted old local_buffer.db")
        except Exception as e:
            print(f"Failed to delete DB: {e}")
    if os.path.exists(FRAMES_DIR):
        try:
            shutil.rmtree(FRAMES_DIR)
            print("Deleted old frames directory")
        except Exception as e:
            print(f"Failed to delete frames: {e}")
    os.makedirs(FRAMES_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload TEXT,
            sent INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_event_locally(event_dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (payload, sent) VALUES (?, 0)", (json.dumps(event_dict),))
    conn.commit()
    conn.close()
    print("[EVENT] Saved locally")
    print(f"[LOCAL] Saved to buffer for Tracker ID: {event_dict.get('track_id', 'unknown')}")

def retry_worker():
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, payload FROM events WHERE sent = 0 LIMIT 10")
            rows = cursor.fetchall()
            
            for row_id, payload_str in rows:
                event = json.loads(payload_str)
                try:
                    resp = httpx.post(BACKEND_URL, json=event, timeout=5.0)
                    if resp.status_code == 200:
                        cursor.execute("UPDATE events SET sent = 1 WHERE id = ?", (row_id,))
                        conn.commit()
                except Exception as e:
                    pass
            conn.close()
        except Exception as e:
            print(f"Retry worker error: {e}")
        
        time.sleep(30)

async def send_event(event_dict):
    import traceback
    try:
        print("[EVENT] Sending")
        async with httpx.AsyncClient() as client:
            resp = await client.post(BACKEND_URL, json=event_dict, timeout=5.0)
            if resp.status_code != 200:
                print(f"[EVENT] Backend failed with status {resp.status_code}. Saving locally.")
                save_event_locally(event_dict)
            else:
                print("[EVENT] Sent")
                print(f"[EVENT] Sent remotely for Tracker ID: {event_dict['track_id']}")
    except Exception as e:
        print(f"[EVENT] Backend failed with error: {e}. Saving locally.")
        traceback.print_exc()
        save_event_locally(event_dict)

track_memory = {}
pending_descriptions = set()
logged_track_ids = set()

qwen_processor = None
qwen_model = None

def init_qwen():
    global qwen_processor, qwen_model
    try:
        print("Loading local Qwen2.5-VL model... (this may take a moment)")
        model_id = "Qwen/Qwen2.5-VL-3B-Instruct"
        qwen_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_id, 
            torch_dtype=torch.bfloat16, 
            device_map="auto"
        )
        qwen_processor = AutoProcessor.from_pretrained(model_id)
        print("Offline Qwen model loaded successfully.")
    except Exception as e:
        import traceback
        print(f"Failed to load Qwen model: {e}")
        traceback.print_exc()

def fetch_description(track_id, class_name, cropped_image, base_event_dict):
    import traceback
    start_time = time.time()
    print("[QWEN] Started")
    print(f"[QWEN] Started for tracker {track_id}")
    try:
        if qwen_model is None or qwen_processor is None:
            desc = f"A {class_name}"
        else:
            rgb_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            prompt = f"Describe this {class_name}'s appearance, any carried objects, and their immediate surroundings/activity naturally. Be concise."
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": pil_image},
                        {"type": "text", "text": prompt},
                    ],
                }
            ]
            
            text = qwen_processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = qwen_processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(qwen_model.device)
            print(f"[QWEN] Input prepared for tracker {track_id}")

            print(f"[QWEN] Generate started for tracker {track_id}")
            generated_ids = qwen_model.generate(**inputs, max_new_tokens=25)
            print(f"[QWEN] Generate completed for tracker {track_id}")
            
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            desc = qwen_processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0].strip()
            
        print(f"[QWEN OUTPUT] {desc}")
        elapsed = time.time() - start_time
        print(f"Qwen inference time: {elapsed:.2f} seconds")
        
        # Append rich description and fire event
        print(f"[QWEN] Completed for tracker {track_id}:\n{desc}")
        base_event_dict["objects"][0]["attributes"] = {"description": desc}
        track_memory[track_id]["description"] = desc
        print(f"[EVENT] Sending for Tracker ID {track_id}")
        asyncio.run(send_event(base_event_dict))
        logged_track_ids.add(track_id)
        
    except Exception as e:
        print(f"[QWEN] Fatal error during inference for tracker {track_id}: {e}")
        traceback.print_exc()
        base_event_dict["objects"][0]["attributes"] = {"description": f"A {class_name}"}
        track_memory[track_id]["description"] = f"A {class_name}"
        asyncio.run(send_event(base_event_dict))
        logged_track_ids.add(track_id)
    finally:
        pending_descriptions.discard(track_id)

class CameraThread:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened() and isinstance(src, int):
            self.cap = cv2.VideoCapture(src, cv2.CAP_AVFOUNDATION)
        self.q = queue.Queue(maxsize=2)
        self.running = True
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()

    def _reader(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        try:
            return True, self.q.get(timeout=2.0)
        except queue.Empty:
            return False, None

    def release(self):
        self.running = False
        self.thread.join()
        self.cap.release()
        
    def isOpened(self):
        return self.cap.isOpened()

def run_pipeline():
    if "--reset" in sys.argv:
        reset_storage()

    init_db()
    init_qwen()
    
    threading.Thread(target=retry_worker, daemon=True).start()

    print("Loading YOLOv11s model...")
    try:
        model = YOLO("yolo11s.pt")
        print("Model loaded. Running warmup...")
        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        _ = model.predict(dummy, verbose=False)
        print("Warmup complete.")
    except Exception as e:
        print(f"Failed to load YOLO: {e}")
        model = None

    camera_source = os.getenv("CAMERA_SOURCE", "0")
    if camera_source.isdigit():
        camera_source = int(camera_source)

    print(f"Opening camera source: {camera_source}")
    cap = CameraThread(camera_source)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera source: {camera_source}.")
        return

    ret, frame = cap.read()
    if not ret or frame is None:
        print("Failed to read a valid frame from the camera.")
        cap.release()
        return

    height, width, _ = frame.shape
    print(f"Camera successfully opened. Resolution: {width}x{height}")

    cv2.namedWindow("SemanticEdge 5G", cv2.WINDOW_NORMAL)
    box_annotator = sv.BoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_scale=0.5, text_thickness=1)
    tracker = sv.ByteTrack()

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Warning: Failed to grab frame from feed.")
            break
        
        annotated_frame = frame.copy()
        
        if model:
            try:
                # Basic classes to keep it robust for demo, added confidence threshold 0.55
                results = model.predict(frame, conf=0.55, classes=[0, 1, 2, 3, 5, 7, 15, 16, 24, 26, 28], verbose=False)
                detections = sv.Detections.from_ultralytics(results[0])
            except Exception as e:
                detections = sv.Detections.empty()

            if detections is not None and len(detections) > 0:
                valid_mask = [(0 <= cid < 80) if cid is not None else False for cid in detections.class_id]
                detections = detections[valid_mask]

            detections = tracker.update_with_detections(detections)

            labels = []
            current_time_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            for i in range(len(detections)):
                xyxy = detections.xyxy[i].tolist()
                confidence = round(float(detections.confidence[i]), 2) if detections.confidence is not None else 0.0
                class_id = int(detections.class_id[i]) if detections.class_id is not None else 0
                tracker_id = int(detections.tracker_id[i]) if detections.tracker_id is not None else -1
                
                class_name = model.names[class_id] if model and hasattr(model, 'names') and class_id in model.names else f"class_{class_id}"
                
                if tracker_id != -1:
                    # Tracker Memory Update
                    if tracker_id not in track_memory:
                        print(f"[TRACK] New tracker {tracker_id}")
                        track_memory[tracker_id] = {"first_seen": current_time_str, "last_seen": current_time_str}
                    else:
                        track_memory[tracker_id]["last_seen"] = current_time_str

                    if tracker_id not in logged_track_ids and tracker_id not in pending_descriptions:
                        event_id = f"evt_{int(time.time()*1000)}_{tracker_id}"
                        frame_filename = f"{event_id}.jpg"
                        frame_path = os.path.abspath(os.path.join(FRAMES_DIR, frame_filename))
                        cv2.imwrite(frame_path, annotated_frame)
                        
                        base_event_dict = {
                            "cam_id": "CAM_01",
                            "timestamp": current_time_str,
                            "zone": "entrance",
                            "track_id": tracker_id,
                            "first_seen": track_memory[tracker_id]["first_seen"],
                            "last_seen": track_memory[tracker_id]["last_seen"],
                            "objects": [
                                {
                                    "type": class_name,
                                    "confidence": confidence,
                                    "attributes": {},
                                    "bbox": xyxy
                                }
                            ],
                            "frame_path": frame_path
                        }
                        
                        x1, y1, x2, y2 = map(int, xyxy)
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(width, x2), min(height, y2)
                        
                        if x2 > x1 and y2 > y1:
                            cropped = frame[y1:y2, x1:x2]
                            pending_descriptions.add(tracker_id)
                            threading.Thread(
                                target=fetch_description, 
                                args=(tracker_id, class_name, cropped.copy(), base_event_dict), 
                                daemon=True
                            ).start()

                label = f"#{tracker_id} {class_name} {confidence}"
                if tracker_id in track_memory and "description" in track_memory[tracker_id]:
                    # Limit the length of the overlay description to keep it visually clean
                    desc_text = track_memory[tracker_id]["description"]
                    label += f" | {desc_text}"
                labels.append(label)

            annotated_frame = box_annotator.annotate(scene=annotated_frame, detections=detections)
            annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)
        
        cv2.imshow("SemanticEdge 5G", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_pipeline()
