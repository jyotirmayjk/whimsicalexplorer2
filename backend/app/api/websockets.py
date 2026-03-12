import asyncio
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.db_models import Session as DBSession, Device, HouseholdSettings
from app.schemas.live_events import DeviceLiveEvent, ServerLiveEvent
from app.adk_runtime.run_config_factory import RunConfigFactory

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.genai import types

router = APIRouter()

# Global proxy for tracking active connections
session_service = InMemorySessionService()

@router.websocket("/live")
async def live_device_endpoint(websocket: WebSocket, device_uid: str, db: Session = Depends(get_db)):
    # 1: Initialization
    device = db.query(Device).filter(Device.device_uid == device_uid).first()
    if not device:
        await websocket.close(code=4003, reason="Unregistered device")
        return

    # In a real system, you'd get the active tracking session to know the app state
    active_session = db.query(DBSession).filter(DBSession.device_id == device.id, DBSession.is_active == True).first()
    if not active_session:
        # If no session, create a mock one for testing
        active_session = DBSession(device_id=device.id, adk_session_key=f"session_{device_uid}", is_active=True)
        db.add(active_session)
        db.commit()

    settings = db.query(HouseholdSettings).filter(HouseholdSettings.household_id == device.household_id).first()

    await websocket.accept()

    user_id = str(device.household_id)
    session_id = active_session.adk_session_key

    # Build the google-adk specific primitives
    agent, run_config = RunConfigFactory.build_config(active_session, settings)
    
    runner = Runner(app_name="kids-pokedex", agent=agent, session_service=session_service)
    live_request_queue = LiveRequestQueue()

    async def upstream_task():
        """Receives messages from WebSocket and sends to LiveRequestQueue."""
        try:
            while True:
                data = await websocket.receive_json()
                event = DeviceLiveEvent.model_validate(data)

                if event.type == "session_start":
                     await websocket.send_json(ServerLiveEvent(type="ack", payload={"status": "session_started"}).model_dump())
                elif event.type == "audio_chunk":
                     # Client sends b64 pcm, stream it into ADK Live
                     b64 = event.payload.get("data_base64") if event.payload else ""
                     if b64:
                         decoded = base64.b64decode(b64)
                         content = types.Content(parts=[types.Part(inline_data=types.Blob(mime_type="audio/pcm", data=decoded))])
                         live_request_queue.send_content(content)
                elif event.type == "image_frame":
                     b64 = event.payload.get("data_base64") if event.payload else ""
                     if b64:
                         decoded = base64.b64decode(b64)
                         content = types.Content(parts=[types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=decoded))])
                         live_request_queue.send_content(content)
                elif event.type == "heartbeat":
                     await websocket.send_json(ServerLiveEvent(type="ack").model_dump())
                     
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"Upstream task exception: {e}")

    async def downstream_task():
        """Receives Events from run_live() and sends to WebSocket."""
        try:
            async for adk_event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config
            ):
                event_json = adk_event.model_dump_json(exclude_none=True, by_alias=True)
                # Note: Currently forwarding raw ADK event json. Client will need to parse ServerLiveEvents appropriately.
                await websocket.send_text(event_json)
        except Exception as e:
            print(f"Downstream task exception: {e}")

    # Start the dual concurrent Bidi-streaming loop
    try:
        await asyncio.gather(upstream_task(), downstream_task(), return_exceptions=True)
    finally:
        # Phase 4: Session Termination
        live_request_queue.close()
