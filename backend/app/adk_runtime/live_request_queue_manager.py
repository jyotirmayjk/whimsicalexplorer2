import asyncio
from typing import Optional, Any

class LiveRequestQueue:
    """
    An async FIFO buffer that sequences upstream messages (audio, text, video) 
    to prevent race conditions before sending them to the ADK `run_live()` generator.
    Conforms to the required ADK implementation spec Phase 3 loop.
    """
    def __init__(self):
        self._queue: asyncio.Queue[Any] = asyncio.Queue()
        self._is_closed = False

    async def put(self, item: Any):
        if self._is_closed:
            raise RuntimeError("Cannot put into a closed LiveRequestQueue")
        await self._queue.put(item)

    async def get(self) -> Any:
        return await self._queue.get()

    def task_done(self):
        self._queue.task_done()

    def close(self):
         self._is_closed = True
         # Unblock any waiting get() calls by pushing a sentinel
         self._queue.put_nowait(None)

    @property
    def is_closed(self) -> bool:
         return self._is_closed

class LiveRequestQueueManager:
    """
    Manages queues for concurrent active sessions.
    """
    def __init__(self):
        self.queues: dict[str, LiveRequestQueue] = {}

    def create_queue(self, session_id: str) -> LiveRequestQueue:
        queue = LiveRequestQueue()
        self.queues[session_id] = queue
        return queue

    def get_queue(self, session_id: str) -> Optional[LiveRequestQueue]:
        return self.queues.get(session_id)

    def close_queue(self, session_id: str):
        if session_id in self.queues:
            self.queues[session_id].close()
            del self.queues[session_id]

queue_manager = LiveRequestQueueManager()
