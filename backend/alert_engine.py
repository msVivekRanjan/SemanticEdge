import os
import time
import asyncio
from telegram import Bot
from telegram.error import TelegramError

last_triggered = {}

# Rules are list of dicts with name, condition (callable), message, and optional debounce_seconds
RULES = [
    {
        "name": "Person at Entrance",
        "condition": lambda event: event.get("zone") == "entrance" and any(obj.get("type") == "person" for obj in event.get("objects", [])),
        "message": "Person detected at entrance zone",
        "debounce_seconds": 10
    },
    {
        "name": "Crowd Threshold Exceeded",
        "condition": lambda event: len(event.get("objects", [])) > 3,
        "message": "More than 3 objects detected in a single event",
        "debounce_seconds": 10
    },
    {
        "name": "Uncertain Detection",
        "condition": lambda event: any(obj.get("confidence", 1.0) < 0.5 for obj in event.get("objects", [])),
        "message": "Detection with confidence below 0.5",
        "debounce_seconds": 10
    },
    {
        "name": "Scene Update",
        "condition": lambda event: len(event.get("objects", [])) > 0,
        "message": "Routine description of objects currently visible",
        "debounce_seconds": 30
    }
]

async def check_alerts(event, bot_token, chat_id):
    if not bot_token or not chat_id:
        return
        
    bot = Bot(token=bot_token)
    
    for rule in RULES:
        if rule["condition"](event):
            rule_name = rule["name"]
            debounce_sec = rule.get("debounce_seconds", 10)
            now = time.time()
            
            # Debounce
            if rule_name in last_triggered and (now - last_triggered[rule_name]) < debounce_sec:
                continue
                
            last_triggered[rule_name] = now
            
            zone = event.get("zone", "unknown")
            timestamp = event.get("timestamp", "unknown time")
            if "T" in timestamp:
                timestamp = timestamp.replace("T", " ").split(".")[0]
            objects = ", ".join(f"{obj.get('type', 'unknown')} ({obj.get('confidence', 0.0):.2f})" for obj in event.get("objects", []))
            
            if rule_name == "Scene Update":
                msg = f"📸 **Camera Update**\n📍 Zone: {zone}\n🕐 Time: {timestamp}\n👀 Visible: {objects}"
            else:
                msg = f"🚨 **ALERT: {rule_name}**\n📍 Zone: {zone}\n🕐 Time: {timestamp}\n⚠️ Objects: {objects}"
            
            try:
                await bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
            except TelegramError as e:
                print(f"Failed to send alert via Telegram: {e}")

if __name__ == "__main__":
    import asyncio
    
    mock_event = {
        "zone": "entrance",
        "timestamp": "2023-10-27T10:00:00Z",
        "objects": [{"type": "person", "confidence": 0.9}]
    }
    
    print("Testing check_alerts condition matched (requires valid tokens to actually send).")
    # asyncio.run(check_alerts(mock_event, "dummy_token", "dummy_chat"))
