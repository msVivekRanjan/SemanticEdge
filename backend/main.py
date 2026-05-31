import os
import json
import asyncio
import urllib.parse
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from fastapi.responses import FileResponse

from alert_engine import check_alerts
from nlq import route_query, generate_response

load_dotenv()

# --- LIFESPAN MANAGER (Replaces startup/shutdown events) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Securely parse MongoDB URI
    raw_uri = os.getenv("MONGO_URI")
    
    # If your URI contains 'username:password@cluster', let's ensure it's safe.
    # Note: If your .env already has the full escaped URI, you can use it directly.
    # Otherwise, it's safer to build it or escape the credentials as shown below:
    # user = urllib.parse.quote_plus(os.getenv("DB_USER"))
    # pw = urllib.parse.quote_plus(os.getenv("DB_PASS"))
    
    try:
        app.db_client = AsyncIOMotorClient(raw_uri, serverSelectionTimeoutMS=5000)
        # Verify connection
        await app.db_client.admin.command('ping')
        print("MongoDB connected")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
    app.db = app.db_client.semanticedge
    
    # 2. ChromaDB Setup
    app.chroma_client = chromadb.Client()
    app.chroma_collection = app.chroma_client.get_or_create_collection(name="semantic_events")
    
    # 3. Sentence Transformer
    app.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Startup complete: Services initialized.")
    yield
    
    # 4. Shutdown Logic
    app.db_client.close()
    print("Shutdown complete: Connections closed.")

# --- APP INITIALIZATION ---
app = FastAPI(title="SemanticEdge 5G Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# --- ROUTES ---

@app.post("/events")
async def receive_event(request: Request):
    print("[BACKEND] Event received")
    event = await request.json()
    
    # Access state via app instance instead of globals
    db = request.app.db
    embedder = request.app.embedder
    chroma_collection = request.app.chroma_collection
    
    # MongoDB Insert
    try:
        result = await db.events.insert_one(event)
        event['_id'] = str(result.inserted_id)
        print("[BACKEND] MongoDB insert success")
    except Exception as e:
        import traceback
        print(f"[BACKEND] MongoDB insert failed: {e}")
        traceback.print_exc()
    
    # Create text summary and embed in ChromaDB
    objects_desc = []
    for o in event.get('objects', []):
        attrs = " ".join([f"{k}:{v}" for k, v in o.get('attributes', {}).items()])
        objects_desc.append(f"{o.get('type', '')} {attrs}".strip())
    objects_str = ' '.join(objects_desc)
    summary = f"Zone: {event.get('zone', '')}. Objects detected: {objects_str}."
    
    embedding = embedder.encode(summary).tolist()
    
    chroma_collection.add(
        ids=[event.get('timestamp')],
        embeddings=[embedding],
        metadatas=[{"zone": event.get("zone", ""), "objects": objects_str}],
        documents=[summary]
    )
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    asyncio.create_task(check_alerts(event, bot_token, chat_id))
    await manager.broadcast(json.dumps(event))
    
    return {"status": "ok"}

@app.get("/events")
async def get_events(request: Request):
    try:
        cursor = request.app.db.events.find().sort("timestamp", -1).limit(50)
        events = []
        async for document in cursor:
            document['_id'] = str(document['_id'])
            events.append(document)
        return events
    except Exception as e:
        print(f"MongoDB Error in /events: {e}")
        return []

@app.get("/stats")
async def get_stats(request: Request):
    try:
        # Zone counts
        db = request.app.db
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
    except Exception as e:
        print(f"MongoDB Error in /stats: {e}")
        return {
            "zone_counts": {},
            "unique_persons": 0,
            "total_events": 0,
            "error": "Database Connection Failed (Check MongoDB IP Allowlist)"
        }

@app.post("/search")
async def search_events(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        
        if not query:
            return {"response": "Please provide a query."}
            
        # 1. Route the query using LLM
        plan = await route_query(query)
        
        if not isinstance(plan, dict):
            return {"response": f"Failed to plan query. Unexpected output type: {type(plan)}"}
            
        if "error" in plan:
            return {"response": f"Failed to plan query: {plan['error']}"}
            
        db_results = []
        engine = plan.get("engine")
        
        if not engine:
            return {"response": "Failed to determine search engine (mongo vs chroma)."}
        
        # 2. Fetch data
        if engine == "needs_date":
            return {"response": plan.get("reason", "Please provide a specific date or time range to narrow down the search.")}
            
        elif engine == "mongo":
            pipeline = plan.get("pipeline", [])
            # Always limit to prevent massive payload
            if not any("$limit" in stage for stage in pipeline):
                pipeline.append({"$limit": 50})
                
            cursor = request.app.db.events.aggregate(pipeline)
            async for doc in cursor:
                doc['_id'] = str(doc['_id'])
                db_results.append(doc)
                
        elif engine == "chroma":
            search_text = plan.get("search_text", query)
            query_embedding = request.app.embedder.encode(search_text).tolist()
            chroma_res = request.app.chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=5
            )
            
            # Map chroma results
            if chroma_res["ids"] and len(chroma_res["ids"][0]) > 0:
                for i in range(len(chroma_res['ids'][0])):
                    ts = chroma_res['ids'][0][i]
                    # We need the mongo _id for fetching the frame
                    mongo_doc = await request.app.db.events.find_one({"timestamp": ts})
                    doc_id = str(mongo_doc['_id']) if mongo_doc else ts
                    
                    db_results.append({
                        "_id": doc_id,
                        "timestamp": ts,
                        "zone": chroma_res['metadatas'][0][i].get("zone", ""),
                        "objects": chroma_res['metadatas'][0][i].get("objects", ""),
                        "frame_path": mongo_doc.get("frame_path") if mongo_doc else None
                    })
                    
        # 3. Generate Natural Language Response
        final_answer = await generate_response(query, db_results)
        
        # 4. Attach image if requested/available
        best_frame = None
        for res in db_results:
            if "frame_path" in res and res["frame_path"] and os.path.exists(res["frame_path"]):
                best_frame = res["frame_path"]
                break
                
        return {
            "response": final_answer,
            "raw_results": len(db_results),
            "frame_path": best_frame
        }
    except Exception as e:
        print(f"Error in /search: {e}")
        return {"response": f"An error occurred: {str(e)}"}

@app.get("/frame")
async def get_frame(path: str):
    if not path or not os.path.exists(path):
        return {"error": "Frame not found"}
    return FileResponse(path)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "fetch":
                    doc_id = msg.get("id")
                    if doc_id:
                        from bson.objectid import ObjectId
                        # Check MongoDB for the document
                        if ObjectId.is_valid(doc_id):
                            doc = await websocket.app.db.events.find_one({"_id": ObjectId(doc_id)})
                            if doc and doc.get("frame_path") and os.path.exists(doc["frame_path"]):
                                import base64
                                with open(doc["frame_path"], "rb") as f:
                                    b64_img = base64.b64encode(f.read()).decode("utf-8")
                                await websocket.send_json({"action": "fetch_response", "id": doc_id, "image": b64_img})
                                continue
                        
                    await websocket.send_json({"action": "fetch_error", "error": "Frame not found or invalid ID"})
            except Exception as e:
                print(f"WS Parsing error: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)