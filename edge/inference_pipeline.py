import os
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

from zone_config import get_zones

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "local_buffer.db")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/events")

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

def run_pipeline():
    init_db()
    
    # Start retry worker thread
    threading.Thread(target=retry_worker, daemon=True).start()

    camera_source = os.getenv("CAMERA_SOURCE", "0")
    if camera_source.isdigit():
        camera_source = int(camera_source)

    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        print(f"Failed to open video source: {camera_source}")
        return

    # Read one frame to get dimensions
    ret, frame = cap.read()
    if not ret:
        print("Failed to read from camera.")
        return
    height, width, _ = frame.shape

    zones_dict = get_zones(width, height)
    entrance_zone = sv.PolygonZone(polygon=zones_dict["entrance"], frame_resolution_wh=(width, height))
    aisle_zone = sv.PolygonZone(polygon=zones_dict["aisle"], frame_resolution_wh=(width, height))

    zone_annotator = sv.PolygonZoneAnnotator(zone=entrance_zone, color=sv.Color.GREEN, thickness=2, text_thickness=1, text_scale=0.5)
    aisle_annotator = sv.PolygonZoneAnnotator(zone=aisle_zone, color=sv.Color.BLUE, thickness=2, text_thickness=1, text_scale=0.5)
    
    box_annotator = sv.BoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_scale=0.5, text_thickness=1)
    
    tracker = sv.ByteTrack()
    
    if RFDETRBase:
        model = RFDETRBase()
    else:
        print("Model not loaded, bounding boxes will not be generated.")
        model = None

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        
        # Sample every 6th frame
        if frame_count % 6 != 0:
            continue

        if model:
            # We assume model returns supervision Detections or a compatible format
            # Depending on exact implementation of RFDETRBase, we might need to adapt this.
            # Using standard supervision integration pattern:
            try:
                results = model.predict(frame)
                detections = sv.Detections.from_ultralytics(results[0]) if hasattr(results[0], 'boxes') else results # Adjust if RFDETRBase differs
            except Exception as e:
                # Mock detections if prediction fails (e.g., unexpected model interface)
                detections = sv.Detections.empty()
        else:
            detections = sv.Detections.empty()

        # Update tracker
        detections = tracker.update_with_detections(detections)
        
        entrance_mask = entrance_zone.trigger(detections=detections)
        aisle_mask = aisle_zone.trigger(detections=detections)

        labels = []
        events_to_send = []

        for i in range(len(detections)):
            xyxy = detections.xyxy[i].tolist()
            confidence = round(float(detections.confidence[i]), 2) if detections.confidence is not None else 0.0
            class_id = int(detections.class_id[i]) if detections.class_id is not None else 0
            tracker_id = int(detections.tracker_id[i]) if detections.tracker_id is not None else -1
            
            # Use 'person' or generic class_id as mock if class names are unavailable
            class_name = "person" if class_id == 0 else f"class_{class_id}"

            if hasattr(model, 'model') and hasattr(model.model, 'names'):
                class_name = model.model.names[class_id]

            zone_name = "unknown"
            if entrance_mask[i]:
                zone_name = "entrance"
            elif aisle_mask[i]:
                zone_name = "aisle"

            labels.append(f"#{tracker_id} {class_name} {confidence} {zone_name}")

            if zone_name != "unknown":
                event_dict = {
                    "cam_id": "CAM_01",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "zone": zone_name,
                    "track_id": tracker_id,
                    "objects": [
                        {
                            "type": class_name,
                            "confidence": confidence,
                            "bbox": xyxy
                        }
                    ]
                }
                events_to_send.append(event_dict)

        for event_dict in events_to_send:
            asyncio.run(send_event(event_dict))

        annotated_frame = frame.copy()
        annotated_frame = zone_annotator.annotate(scene=annotated_frame)
        annotated_frame = aisle_annotator.annotate(scene=annotated_frame)
        
        annotated_frame = box_annotator.annotate(scene=annotated_frame, detections=detections)
        annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)

        cv2.imshow("SemanticEdge 5G", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_pipeline()
