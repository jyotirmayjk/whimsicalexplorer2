# Kids Pokédex — Backend 🐾

This is the Python FastAPI backend system powering the Kids Pokédex mobile app and ADK audio runtime. 

## Features
- **Strict Separation of Concerns**: Auth/Households, REST Telemetry, and real-time ADK WebSocket streaming are conceptually isolated.
- **Bi-Directional Audio Streaming**: Implements the ADK Dual-Loop Concurrency pattern.
  - An Upstream `LiveRequestQueue` intercepts raw device audio chunks (50-100ms) buffering and preventing stream clipping.
  - A Downstream Generator processes Gemini server output, formatting raw transcripts, filtering content, and tunneling TTS audio back to the device.
- **Safety First**: Device playback is instantaneously stopped upon receiving `interrupted` socket signals, minimizing unsafe overlap.
- **Data Persistence**: Uses SQLAlchemy + PostgreSQL to map standard User flows (Households, Discoveries, Activity Timelines, Transcripts).

## Local Development 

### Requirements
- Python 3.11+
- PostgreSQL
- Redis Server (Optional for Socket Resumption Layer)
- `google-genai` SDK and Gemini API Key (`GOOGLE_API_KEY`)

### Setup Environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure
Create a `.env` in the root:
```env
PROJECT_NAME="Kids Pokédex"
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=kids_pokedex
SECRET_KEY=dev_key_only
GOOGLE_API_KEY=AIzaSy...
```

### Run Server
```bash
uvicorn app.main:app --reload --port 8000
```

## ADK Architecture Walkthrough
The `app/adk_runtime/` directory isolates the Google Live interaction loop:
1. `run_config_factory.py`: Anchors safety system prompts mapping Mobile Session AppModes (Story, Learn) and contextual image captures instantly into the API.
2. `live_request_queue_manager.py`: Ensures fast non-blocking WebSocket receives are sequenced.
3. `runner.py`: The async `ADKSessionRunner` processes the dual-direction IO streams continuously until termination.
