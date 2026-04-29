import os
import time
import asyncio
from telegram import Bot
from telegram.error import TelegramError

last_triggered = {}

# Rules are list of dicts with name, condition (callable), message
RULES = [
    {
        "name": "Person at Entrance",
        "condition": lambda event: event.get("zone") == "entrance" and any(obj.get("type") == "person" for obj in event.get("objects", [])),
        "message": "Person detected at entrance zone"
    },
    {
        "name": "Crowd Threshold Exceeded",
        "condition": lambda event: len(event.get("objects", [])) > 3,
        "message": "More than 3 objects detected in a single event"
    },
    {
        "name": "Uncertain Detection",
        "condition": lambda event: any(obj.get("confidence", 1.0) < 0.5 for obj in event.get("objects", [])),
        "message": "Detection with confidence below 0.5"
    }
]

async def check_alerts(event, bot_token, chat_id):
    if not bot_token or not chat_id:
        return
        
    bot = Bot(token=bot_token)
    
    for rule in RULES:
        if rule["condition"](event):
            rule_name = rule["name"]
            now = time.time()
            
            # Debounce 10 seconds
            if rule_name in last_triggered and (now - last_triggered[rule_name]) < 10:
                continue
                
            last_triggered[rule_name] = now
            
            zone = event.get("zone", "unknown")
            timestamp = event.get("timestamp", "unknown time")
            objects = ", ".join(obj.get("type", "unknown") for obj in event.get("objects", []))
            
            msg = f"🚨 ALERT: {rule_name}\nZone: {zone}\nTime: {timestamp}\nObjects: {objects}"
            
            try:
                await bot.send_message(chat_id=chat_id, text=msg)
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
