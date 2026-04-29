import os
import json
import asyncio
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from alert_engine import check_alerts

load_dotenv()

app = FastAPI(title="SemanticEdge 5G Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global clients
db_client = None
db = None
chroma_client = None
chroma_collection = None
embedder = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    global db_client, db, chroma_client, chroma_collection, embedder
    
    # MongoDB
    mongo_uri = os.getenv("MONGO_URI")
    db_client = AsyncIOMotorClient(mongo_uri)
    db = db_client.semanticedge
    
    # ChromaDB
    chroma_client = chromadb.Client()
    chroma_collection = chroma_client.get_or_create_collection(name="semantic_events")
    
    # Sentence Transformer
    embedder = SentenceTransformer('all-MiniLM-L6-v2')

@app.on_event("shutdown")
async def shutdown_event():
    db_client.close()

@app.post("/events")
async def receive_event(request: Request):
    event = await request.json()
    
    # MongoDB Insert
    result = await db.events.insert_one(event)
    event['_id'] = str(result.inserted_id)
    
    # Create text summary and embed in ChromaDB
    objects_str = ' '.join([o.get('type', '') for o in event.get('objects', [])])
    summary = f"Zone: {event.get('zone', '')}. Objects detected: {objects_str}."
    
    embedding = embedder.encode(summary).tolist()
    
    chroma_collection.add(
        ids=[event.get('timestamp')],
        embeddings=[embedding],
        metadatas=[{"zone": event.get("zone", ""), "objects": objects_str}],
        documents=[summary]
    )
    
    # Alert Engine
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # We fire and forget the alert check
    asyncio.create_task(check_alerts(event, bot_token, chat_id))
    
    # WebSocket Broadcast
    await manager.broadcast(json.dumps(event))
    
    return {"status": "ok"}

@app.get("/events")
async def get_events():
    cursor = db.events.find().sort("timestamp", -1).limit(50)
    events = []
    async for document in cursor:
        document['_id'] = str(document['_id'])
        events.append(document)
    return events

@app.get("/stats")
async def get_stats():
    # Zone counts
    pipeline = [
        {"$group": {"_id": "$zone", "count": {"$sum": 1}}}
    ]
    zone_counts = {}
    async for doc in db.events.aggregate(pipeline):
        zone_counts[doc["_id"]] = doc["count"]
        
    # Unique Track IDs
    unique_tracks = await db.events.distinct("track_id")
    
    # Total count
    total_count = await db.events.count_documents({})
    
    return {
        "zone_counts": zone_counts,
        "unique_persons": len([t for t in unique_tracks if t != -1]),
        "total_events": total_count
    }

@app.post("/search")
async def search_events(request: Request):
    data = await request.json()
    query = data.get("query", "")
    
    if not query:
        return []
        
    query_embedding = embedder.encode(query).tolist()
    results = chroma_collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    
    parsed_results = []
    if results['ids']:
        for i in range(len(results['ids'][0])):
            parsed_results.append({
                "timestamp": results['ids'][0][i],
                "zone": results['metadatas'][0][i].get("zone", ""),
                "objects": results['metadatas'][0][i].get("objects", "")
            })
            
    return parsed_results

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # keep-alive or just ignore incoming
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
