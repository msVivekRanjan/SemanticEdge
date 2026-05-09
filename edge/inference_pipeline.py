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

try:
    from rfdetr import RFDETRBase
except ImportError:
    print("Warning: rfdetr not installed or not found. Please ensure it is installed.")
    RFDETRBase = None

import base64
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

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

blip_processor = None
blip_model = None

def init_blip():
    global blip_processor, blip_model
    try:
        print("Loading local BLIP model... (this may take a moment)")
        blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        print("Offline BLIP model loaded successfully.")
    except Exception as e:
        print(f"Failed to load BLIP model: {e}")

def fetch_description(track_id, cropped_image):
    try:
        if blip_model is None or blip_processor is None:
            description_cache[track_id] = "person"
            return
            
        rgb_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        inputs = blip_processor(pil_image, return_tensors="pt")
        out = blip_model.generate(**inputs)
        description = blip_processor.decode(out[0], skip_special_tokens=True)
        
        description_cache[track_id] = description.strip()
    except Exception as e:
        print(f"Vision error: {e}")
        description_cache[track_id] = "person"
    finally:
        pending_descriptions.discard(track_id)

def run_pipeline():
    init_db()
    init_blip()
    
    # Start retry worker thread
    threading.Thread(target=retry_worker, daemon=True).start()

    model = None
    if RFDETRBase:
        print("Loading RFDETR model...")
        model = RFDETRBase()
        if hasattr(model, 'optimize_for_inference'):
            try:
                model.optimize_for_inference()
            except Exception:
                pass
        print("Model loaded. Running warmup...")
        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        _ = model.predict(dummy)
        print("Warmup complete.")
    else:
        print("Model not loaded, bounding boxes will not be generated.")

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
        
        # Sample every 6th frame for inference
        if frame_count % 6 == 0 and model:
            try:
                results = model.predict(frame)
                
                # Check how results are structured and parse to sv.Detections
                if isinstance(results, sv.Detections):
                    detections = results
                elif isinstance(results, list) and len(results) > 0 and isinstance(results[0], sv.Detections):
                    detections = results[0]
                elif hasattr(results, 'boxes'):
                    detections = sv.Detections.from_ultralytics(results)
                elif isinstance(results, list) and len(results) > 0 and hasattr(results[0], 'boxes'):
                    detections = sv.Detections.from_ultralytics(results[0])
                else:
                    detections = sv.Detections.empty()
            except Exception as e:
                # If there's a prediction error (like out of bounds class_id), mock empty detections
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
                
                # Fetch rich description if not cached
                class_name = "person" if class_id == 0 else f"class_{class_id}"
                if tracker_id != -1:
                    if tracker_id in description_cache:
                        class_name = description_cache[tracker_id]
                        
                        # DEBOUNCING: Only log once per tracker_id
                        if tracker_id not in logged_track_ids:
                            logged_track_ids.add(tracker_id)
                            
                            event_id = f"evt_{int(time.time()*1000)}_{i}"
                            frame_filename = f"{event_id}.jpg"
                            frame_path = os.path.abspath(os.path.join(FRAMES_DIR, frame_filename))
                            
                            event_dict = {
                                "cam_id": "CAM_01",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "zone": "whole_frame",
                                "track_id": tracker_id,
                                "objects": [
                                    {
                                        "type": class_name,
                                        "confidence": confidence,
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
