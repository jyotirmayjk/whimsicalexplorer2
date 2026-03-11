import asyncio
from google import genai
from google.genai import types
from app.core.config import settings
from app.adk_runtime.run_config_factory import RunConfigFactory
from app.adk_runtime.live_request_queue_manager import queue_manager
from app.schemas.live_events import ServerLiveEvent
from app.models.db_models import Session, HouseholdSettings

# Global client initialization per ADK specs best practice
client = genai.Client(http_options={'api_version': 'v1alpha'})

class ADKSessionRunner:
    """
    Orchestrates the active Gemini Live connection.
    Implements the dual-loop architecture: 
    1. Streaming audio chunks UP from the LiveRequestQueue
    2. Receiving responses DOWN and emitting them via callback
    """
    def __init__(self, session: Session, settings: HouseholdSettings, broadcast_callback):
        self.session = session
        self.settings = settings
        self.broadcast_callback = broadcast_callback # Async fn(ServerLiveEvent)
        self.queue = queue_manager.get_queue(session.adk_session_key)
        self.run_config = RunConfigFactory.build_config(session, settings)
        self._interrupted = False

    async def _send_to_gemini(self, live_session):
        """Task 1: Drain the LiveRequestQueue and send to Gemini."""
        while not self.queue.is_closed:
            item = await self.queue.get()
            if item is None:
                continue

            # Check if it's an explicit interruption signal from the device
            if isinstance(item, dict) and item.get("type") == "interrupt":
                self._interrupted = True
                await self.broadcast_callback(ServerLiveEvent(type="interrupted"))
                continue

            try:
                # Expecting raw audio or text input to be dispatched
                await live_session.send(input=item, end_of_turn=False)
            except Exception as e:
                print(f"Error sending to Gemini: {e}")
            finally:
                self.queue.task_done()

    async def _receive_from_gemini(self, live_session):
        """Task 2: Listen for replies and stream them back to the device."""
        try:
            async for response in live_session.receive():
                if self._interrupted:
                    # Drop partial transcripts and audio if interrupted
                    self._interrupted = False
                    continue
                
                # Forward server content chunks out
                server_content = response.server_content
                if server_content is not None:
                    model_turn = server_content.model_turn
                    if model_turn:
                        for part in model_turn.parts:
                            # 1. Forward Audio Content
                            if part.inline_data:
                                audio_b64 = part.inline_data.data.decode('utf-8')
                                await self.broadcast_callback(
                                    ServerLiveEvent(type="audio_out", payload={"data_base64": audio_b64})
                                )
                            # 2. Forward Text Content / Transcripts
                            if part.text:
                                await self.broadcast_callback(
                                    ServerLiveEvent(type="transcript_out", payload={"text": part.text, "is_partial": True, "speaker": "agent"})
                                )
                    
                    if server_content.turn_complete:
                         await self.broadcast_callback(ServerLiveEvent(type="turn_complete"))

        except Exception as e:
             await self.broadcast_callback(ServerLiveEvent(type="error", payload={"detail": str(e)}))

    async def start(self):
        """Bootstraps the Live API context window."""
        model = self.run_config["model"]
        config = self.run_config.copy()
        del config["model"]

        async with client.aio.live.connect(model=model, config=config) as live_session:
            send_task = asyncio.create_task(self._send_to_gemini(live_session))
            receive_task = asyncio.create_task(self._receive_from_gemini(live_session))
            await asyncio.gather(send_task, receive_task)
