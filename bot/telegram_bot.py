import os
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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
            msg = f"📊 **Stats**\nTotal Events: {data.get('total_events', 0)}\nUnique Persons: {data.get('unique_persons', 0)}\nZones:\n{zone_info}"
            
            await update.message.reply_text(msg, parse_mode="Markdown")
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
    await update.message.reply_text(f"🔍 Searching: '{query_text}'...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{BACKEND_URL}/search", json={"query": query_text})
            results = resp.json()
            
            if not results:
                await update.message.reply_text("No relevant events found.")
                return
                
            msgs = []
            for r in results:
                time_part = r.get("timestamp", "").split("T")[-1].split(".")[0] if "T" in r.get("timestamp", "") else r.get("timestamp")
                msgs.append(f"📍 Zone: {r.get('zone')} | 🕐 {time_part} | 👤 {r.get('objects')}")
                
            await update.message.reply_text("\n".join(msgs))
    except Exception as e:
        await update.message.reply_text(f"Search failed: {e}")

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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
