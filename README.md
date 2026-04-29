# SemanticEdge 5G

A privacy-first AI surveillance system prototype that converts video to structured metadata at the edge and never uploads raw footage to the cloud.

## Project Structure
- `edge/`: Video inference pipeline running locally.
- `backend/`: FastAPI backend handling MongoDB, ChromaDB vector store, WebSockets, and Alert checking.
- `bot/`: Telegram Bot to query and receive alerts.
- `dashboard/`: React (Vite) dashboard for live viewing of metadata.

## Setup & Installation

### 1. Requirements
- Python 3.9+
- Node.js 18+
- Webcam or RTSP Feed

### 2. Python Dependencies
Create a virtual environment and install the required packages:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn motor chromadb sentence-transformers python-dotenv opencv-python httpx supervision "python-telegram-bot[job-queue]" langchain-anthropic anthropic
```

*(Note: If you have a specific `rfdetr` package, install that as well, e.g., `pip install rfdetr`. Otherwise the pipeline will run without bounding boxes or you can swap the model for YOLO via `supervision`)*

### 3. Environment Variables
Ensure your `.env` file is in the root directory `semanticedge/` with the following variables:
- `MONGO_URI`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `ANTHROPIC_API_KEY`
- `CAMERA_SOURCE` (e.g., `0` for default webcam)

---

## Running the System

You will need **4 separate terminal windows**.

### Terminal 1: Backend
```bash
# From the semanticedge/ directory
source venv/bin/activate
python backend/main.py
```
*Runs on http://localhost:8000*

### Terminal 2: Edge Inference
```bash
# From the semanticedge/ directory
source venv/bin/activate
python edge/inference_pipeline.py
```
*A local OpenCV window will appear showing the video feed, zones, and detections.*

### Terminal 3: Telegram Bot
```bash
# From the semanticedge/ directory
source venv/bin/activate
python bot/telegram_bot.py
```
*In Telegram, you can use `/start`, `/stats`, `/recent`, or natural language queries like "Show me all people in the entrance zone".*

### Terminal 4: Dashboard
```bash
# From the semanticedge/dashboard/ directory
cd dashboard
npm install
npm run dev
```
*Runs on http://localhost:5173. Open in your browser to see live events and stats.*
