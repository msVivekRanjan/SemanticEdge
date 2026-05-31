import os
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
                    pass # Keep trying next time
            conn.close()
        except Exception as e:
            print(f"Retry worker error: {e}")
        
        time.sleep(30)

async def send_event(event_dict):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(BACKEND_URL, json=event_dict, timeout=5.0)
            if resp.status_code != 200:
                save_event_locally(event_dict)
    except Exception:
        save_event_locally(event_dict)

description_cache = {}
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
        print(f"Failed to load Qwen model: {e}")

def parse_attributes_from_description(desc: str) -> dict:
    desc = desc.lower()
    attributes = {}
    
    colors = ["red", "blue", "green", "black", "white", "yellow", "orange", "purple", "pink", "grey", "gray", "brown"]
    top_clothing = ["shirt", "t-shirt", "tshirt", "jacket", "hoodie", "sweater", "top", "coat", "suit"]
    bottom_clothing = ["pants", "jeans", "shorts", "skirt", "trousers", "bottoms"]
    
    top_found = False
    bot_found = False
    
    for color in colors:
        if not top_found:
            for top in top_clothing:
                if f"{color} {top}" in desc or (color in desc and top in desc and abs(desc.find(color) - desc.find(top)) < 20):
                    attributes["top"] = f"{color} {top}"
                    top_found = True
                    break
        if not bot_found:
            for bot in bottom_clothing:
                if f"{color} {bot}" in desc or (color in desc and bot in desc and abs(desc.find(color) - desc.find(bot)) < 20):
                    attributes["bottom"] = f"{color} {bot}"
                    bot_found = True
                    break
                    
    if not attributes:
        attributes["description"] = desc
        
    return attributes

def fetch_description(track_id, cropped_image):
    try:
        if qwen_model is None or qwen_processor is None:
            description_cache[track_id] = "person"
            return
            
        rgb_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": pil_image},
                    {"type": "text", "text": "Describe this person's appearance: gender, facial hair, and clothing colors. Be concise."},
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

        generated_ids = qwen_model.generate(**inputs, max_new_tokens=50)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        description = qwen_processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        
        description_cache[track_id] = description.strip()
    except Exception as e:
        print(f"Vision error: {e}")
        description_cache[track_id] = "person"
    finally:
        pending_descriptions.discard(track_id)

def run_pipeline():
    init_db()
    init_qwen()
    
    # Start retry worker thread
    threading.Thread(target=retry_worker, daemon=True).start()

    print("Loading YOLOv11 model...")
    try:
        model = YOLO("yolo11n.pt")
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
    cap = cv2.VideoCapture(camera_source) # Rely on default backend
    
    # macOS fallback
    if not cap.isOpened() and isinstance(camera_source, int):
        print("Default backend failed, trying CAP_AVFOUNDATION...")
        cap = cv2.VideoCapture(camera_source, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print(f"ERROR: Cannot open camera source: {camera_source}. Please check connections and permissions.")
        return

    # Read one frame to get dimensions
    ret, frame = False, None
    for _ in range(10):
        ret, frame = cap.read()
        if ret:
            break
        time.sleep(0.2)

    if not ret:
        print("Failed to read a valid frame from the camera. The feed might be black or unavailable.")
        cap.release()
        return

    height, width, _ = frame.shape
    print(f"Camera successfully opened. Resolution: {width}x{height}")

    cv2.namedWindow("SemanticEdge 5G", cv2.WINDOW_NORMAL)

    box_annotator = sv.BoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_scale=0.5, text_thickness=1)
    
    tracker = sv.ByteTrack()

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Warning: Failed to grab frame from feed.")
            break

        frame_count += 1
        
        # We always create annotated_frame to display it smoothly
        annotated_frame = frame.copy()
        
        if model:
            try:
                # YOLOv11 detects everything natively. 
                # Using classes=[0, 1, 2, 3, 5, 7, 24, 26] for person, vehicles and bags
                results = model.predict(frame, classes=[0, 1, 2, 3, 5, 7, 24, 26], verbose=False)
                detections = sv.Detections.from_ultralytics(results[0])
            except Exception as e:
                detections = sv.Detections.empty()

            # Filter out invalid class_ids (e.g., > 80 mapping to empty string)
            if detections is not None and len(detections) > 0:
                valid_mask = []
                for class_id in detections.class_id:
                    if class_id is None:
                        valid_mask.append(False)
                    else:
                        # Depending on the model, MS COCO has 80 classes usually (0 to 79)
                        valid_mask.append(0 <= class_id < 80)
                detections = detections[valid_mask]

            # Update tracker
            detections = tracker.update_with_detections(detections)

            labels = []
            events_to_send = []

            for i in range(len(detections)):
                xyxy = detections.xyxy[i].tolist()
                confidence = round(float(detections.confidence[i]), 2) if detections.confidence is not None else 0.0
                class_id = int(detections.class_id[i]) if detections.class_id is not None else 0
                tracker_id = int(detections.tracker_id[i]) if detections.tracker_id is not None else -1
                
                class_name = "person" if class_id == 0 else f"class_{class_id}"
                if tracker_id != -1:
                    if tracker_id in description_cache:
                        desc_text = description_cache[tracker_id]
                        attributes = parse_attributes_from_description(desc_text)
                        
                        # DEBOUNCING: Only log once per tracker_id
                        if tracker_id not in logged_track_ids:
                            logged_track_ids.add(tracker_id)
                            
                            event_id = f"evt_{int(time.time()*1000)}_{i}"
                            frame_filename = f"{event_id}.jpg"
                            frame_path = os.path.abspath(os.path.join(FRAMES_DIR, frame_filename))
                            
                            # Format explicitly as requested
                            event_dict = {
                                "cam_id": "CAM_01",
                                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                                "zone": "entrance", # Set default zone or logic here
                                "track_id": tracker_id,
                                "objects": [
                                    {
                                        "type": class_name,
                                        "confidence": confidence,
                                        "attributes": attributes,
                                        "bbox": xyxy
                                    }
                                ],
                                "frame_path": frame_path
                            }
                            events_to_send.append(event_dict)
                            
                    elif tracker_id not in pending_descriptions:
                        # Crop and send to LLM
                        x1, y1, x2, y2 = map(int, xyxy)
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(width, x2), min(height, y2)
                        if x2 > x1 and y2 > y1:
                            cropped = frame[y1:y2, x1:x2]
                            pending_descriptions.add(tracker_id)
                            threading.Thread(target=fetch_description, args=(tracker_id, cropped.copy()), daemon=True).start()

                labels.append(f"#{tracker_id} {class_name} {confidence}")

            # Annotate
            annotated_frame = box_annotator.annotate(scene=annotated_frame, detections=detections)
            annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)
            
            # Save the frame if there are events
            if len(events_to_send) > 0:
                cv2.imwrite(events_to_send[0]["frame_path"], annotated_frame)
                # Since all events in this frame share the same visual moment, they can all point to the same frame.
                for ev in events_to_send:
                    ev["frame_path"] = events_to_send[0]["frame_path"]

            # Fire off events
            for event_dict in events_to_send:
                try:
                    threading.Thread(target=lambda e=event_dict: asyncio.run(send_event(e)), daemon=True).start()
                except Exception as e:
                    pass

            # Annotate
            annotated_frame = box_annotator.annotate(scene=annotated_frame, detections=detections)
            annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)
        
        # We always draw the zones
            cv2.imshow("SemanticEdge 5G", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_pipeline()
