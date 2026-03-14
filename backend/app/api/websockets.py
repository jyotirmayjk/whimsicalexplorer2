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

    from app.models.enums import SessionStatus
    active_session = db.query(DBSession).filter(DBSession.device_id == device.id, DBSession.status != SessionStatus.ended).first()
    if not active_session:
        active_session = DBSession(device_id=device.id, adk_session_key=f"session_{device_uid}", status=SessionStatus.active, household_id=device.household_id)
        db.add(active_session)
        db.commit()

    settings = db.query(HouseholdSettings).filter(HouseholdSettings.household_id == device.household_id).first()

    await websocket.accept()

    user_id = str(device.household_id)
    session_id = active_session.adk_session_key

    agent, run_config = RunConfigFactory.build_config(active_session, settings)
    
    # Consistent app_name to avoid runner warnings
    runner = Runner(app_name="agents", agent=agent, session_service=session_service)
    live_request_queue = LiveRequestQueue()

    # Create the ADK session in InMemorySessionService so run_live() can find it
    await session_service.create_session(
        app_name="agents",
        user_id=user_id,
        session_id=session_id,
    )

    async def upstream_task():
        """Receives messages from WebSocket and sends to LiveRequestQueue."""
        try:
            while True:
                data = await websocket.receive_json()
                event = DeviceLiveEvent.model_validate(data)

                if event.type == "session_start":
                     await websocket.send_json(ServerLiveEvent(type="ack", payload={"status": "session_started"}).model_dump())
                elif event.type == "audio_chunk":
                     b64 = event.payload.get("data_base64") if event.payload else ""
                     if b64:
                         decoded = base64.b64decode(b64)
                         content = types.Content(parts=[types.Part(inline_data=types.Blob(mime_type="audio/pcm", data=decoded))])
                         live_request_queue.send_content(content)
                elif event.type == "text_message":
                     txt = event.payload.get("text") if event.payload else ""
                     if txt:
                         content = types.Content(parts=[types.Part(text=txt)])
                         live_request_queue.send_content(content)
                elif event.type == "image_frame":
                     b64 = event.payload.get("data_base64") if event.payload else ""
                     if b64:
                         decoded = base64.b64decode(b64)
                         content = types.Content(parts=[types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=decoded))])
                         live_request_queue.send_content(content)
                elif event.type == "activity_start":
                     live_request_queue.send_activity_start()
                elif event.type == "activity_end":
                     live_request_queue.send_activity_end()
                elif event.type == "interrupt":
                     # ADK handles interruption via activity_start generally, 
                     # but we can also signal explicit interrupt if needed.
                     live_request_queue.send_activity_start()
                elif event.type == "heartbeat":
                     await websocket.send_json(ServerLiveEvent(type="ack").model_dump())
                     
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"Upstream task exception: {e}")

    async def downstream_task():
        """Receives Events from run_live() and sends to WebSocket (wrapped in ServerLiveEvent)."""
        try:
            async for adk_event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config
            ):
                # 1. Check for global interruption flag (User spoke over Model)
                if hasattr(adk_event, 'interrupted') and adk_event.interrupted:
                    await websocket.send_json(ServerLiveEvent(type="interrupted").model_dump())
                    continue

                if hasattr(adk_event, 'server_content') and adk_event.server_content:
                    sc = adk_event.server_content
                    
                    # 2. Check for content-level interruption
                    if sc.interrupted:
                        await websocket.send_json(ServerLiveEvent(type="interrupted").model_dump())
                    
                    if sc.model_turn:
                        for part in sc.model_turn.parts:
                            # 3. Audio Delivery (24kHz from Gemini)
                            if part.inline_data:
                                audio_b64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                                await websocket.send_json(ServerLiveEvent(
                                    type="audio_out", 
                                    payload={"data_base64": audio_b64}
                                ).model_dump())
                            
                            # 4. Transcripts
                            if part.text:
                                await websocket.send_json(ServerLiveEvent(
                                    type="transcript_out", 
                                    payload={"text": part.text, "is_partial": True, "speaker": "agent"}
                                ).model_dump())

                    if sc.turn_complete:
                        await websocket.send_json(ServerLiveEvent(type="turn_complete").model_dump())

                elif hasattr(adk_event, 'tool_call'):
                    # Handle tool calls if any are defined later
                    pass
                
        except Exception as e:
            print(f"Downstream task exception: {e}")
            await websocket.send_json(ServerLiveEvent(type="error", payload={"detail": str(e)}).model_dump())

    try:
        await asyncio.gather(upstream_task(), downstream_task(), return_exceptions=True)
    finally:
        live_request_queue.close()
