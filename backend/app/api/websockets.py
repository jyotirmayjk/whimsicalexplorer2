import asyncio
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.db_models import Session as DBSession, Device
from app.schemas.live_events import DeviceLiveEvent, ServerLiveEvent

router = APIRouter()

# Global proxy for tracking active connections
class ConnectionManager:
    def __init__(self):
        # Maps transport_connection_id -> WebSocket
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

    async def send_event(self, connection_id: str, event: ServerLiveEvent):
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_json(event.model_dump())

manager = ConnectionManager()

@router.websocket("/live")
async def live_device_endpoint(websocket: WebSocket, device_uid: str, db: Session = Depends(get_db)):
    # 1: Initialization
    device = db.query(Device).filter(Device.device_uid == device_uid).first()
    if not device:
        await websocket.close(code=4003, reason="Unregistered device")
        return

    connection_id = f"{device_uid}_{id(websocket)}"
    await manager.connect(websocket, connection_id)

    # Note: In the full ADK implementation, this routes input chunks to the LiveRequestQueue
    # and listens concurrently to the generator. Implementing mock loop for architectural verification.
    
    try:
        while True:
            # Task A - Upstream Receiver (Blocked on WS wait usually)
            data = await websocket.receive_json()
            event = DeviceLiveEvent.model_validate(data)
            
            if event.type == "session_start":
                 await manager.send_event(connection_id, ServerLiveEvent(type="ack", payload={"status": "session_started"}))
            elif event.type == "audio_chunk":
                 # Route to LiveRequestQueue in real implementation
                 pass
            elif event.type == "interrupt":
                 # Route explicit interruption to Runner
                 pass
            elif event.type == "heartbeat":
                 await manager.send_event(connection_id, ServerLiveEvent(type="ack"))
                 
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        # Notify the ADK Runner to abort/save state
    except Exception as e:
        manager.disconnect(connection_id)
