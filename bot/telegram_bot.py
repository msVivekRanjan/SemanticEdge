import os
import json
import base64
import websockets
import httpx
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

USER_STATES = {}

def format_event(event: dict) -> str:
    zone = event.get("zone", "unknown")
    
    timestamp = event.get("timestamp", "unknown time")
    if "T" in timestamp:
        # Just grab the time part approx
        time_part = timestamp.split("T")[1].split(".")[0]
        timestamp = time_part
        
    objects_str = "None"
    if "objects" in event and event["objects"]:
        obj = event["objects"][0]
        objects_str = f"{obj.get('type', 'unknown')} ({obj.get('confidence', 0.0)})"
        
    return f"📍 Zone: {zone} | 🕐 {timestamp} | 👤 {objects_str}"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "SemanticEdge 5G active. Commands: /query, /stats, /recent"
    await update.message.reply_text(msg)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BACKEND_URL}/stats")
            data = resp.json()
            
            zone_info = "\n".join([f"- {z}: {c}" for z, c in data.get("zone_counts", {}).items()])
            msg = f"📊 Stats\nTotal Events: {data.get('total_events', 0)}\nUnique Persons: {data.get('unique_persons', 0)}\nZones:\n{zone_info}"
            
            await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Failed to fetch stats: {e}")

async def recent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BACKEND_URL}/events")
            events = resp.json()
            
            if not events:
                await update.message.reply_text("No recent events.")
                return
                
            recent_5 = events[:5]
            msgs = [format_event(e) for e in recent_5]
            await update.message.reply_text("\n".join(msgs))
    except Exception as e:
        await update.message.reply_text(f"Failed to fetch recent events: {e}")

async def query_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = ""
    if context.args:
        query_text = " ".join(context.args)
    else:
        query_text = update.message.text.replace("/query", "").strip()

    if not query_text:
        await update.message.reply_text("Please provide a query text.")
        return
        
    await handle_query(update, query_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text
    if query_text.startswith("/"):
        return
    await handle_query(update, query_text)

async def handle_query(update: Update, query_text: str):
    user_id = update.effective_user.id
    
    if user_id in USER_STATES:
        pending_query = USER_STATES[user_id]
        query_to_send = f"{pending_query} on {query_text}"
        del USER_STATES[user_id]
    else:
        query_to_send = query_text

    msg = await update.message.reply_text(f"🔍 Analyzing: '{query_to_send}'...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{BACKEND_URL}/search", json={"query": query_to_send})
            
            if resp.status_code != 200:
                await msg.edit_text(f"Backend error ({resp.status_code}): {resp.text}")
                return
                
            data = resp.json()
            
            if isinstance(data, dict) and "response" in data:
                text_response = data["response"]
                
                # Check if backend needs a date
                if "narrow down" in text_response.lower() or "specific date" in text_response.lower():
                    USER_STATES[user_id] = query_to_send
                    await msg.edit_text(text_response)
                    return
                
                # Prepend with a helpful note about the /fetch command
                if "id" in text_response.lower() or "ID" in text_response:
                    text_response += "\n\n*Reply with `/fetch [id]` to establish a secure WebSocket tunnel for visual verification.*"
                    
                await msg.edit_text(text_response, parse_mode="Markdown")
            else:
                await msg.edit_text(f"Database returned an unexpected format: {data}")
    except Exception as e:
        await msg.edit_text(f"Search failed: {e}")

async def fetch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide an ID. Usage: /fetch [id]")
        return
        
    doc_id = context.args[0]
    msg = await update.message.reply_text(f"📡 Establishing secure WebSocket tunnel to fetch '{doc_id}'...")
    
    try:
        ws_url = BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://") + "/ws"
        async with websockets.connect(ws_url) as websocket:
            await websocket.send(json.dumps({"action": "fetch", "id": doc_id}))
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("action") == "fetch_response":
                img_data = base64.b64decode(data.get("image"))
                await msg.delete()
                await update.message.reply_photo(photo=BytesIO(img_data), caption=f"Visual Confirmation for ID: {doc_id}")
            else:
                await msg.edit_text(f"Error: {data.get('error', 'Unknown error occurred')}")
    except Exception as e:
        await msg.edit_text(f"WebSocket connection failed: {e}")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN is missing in .env")
        return
        
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("recent", recent_command))
    application.add_handler(CommandHandler("query", query_command))
    application.add_handler(CommandHandler("fetch", fetch_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
