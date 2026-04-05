"""Server-Sent Events endpoint for real-time updates."""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Simple in-memory pub/sub for SSE clients
_subscribers: list[asyncio.Queue[dict]] = []


def broadcast(event_type: str, data: dict) -> None:
    """Broadcast an event to all connected SSE clients."""
    message = {"type": event_type, **data}
    dead: list[asyncio.Queue[dict]] = []
    for q in _subscribers:
        try:
            q.put_nowait(message)
        except asyncio.QueueFull:
            dead.append(q)
    for q in dead:
        _subscribers.remove(q)


async def _event_stream(queue: asyncio.Queue[dict]) -> AsyncGenerator[str, None]:
    """Yield SSE-formatted events from a subscriber queue."""
    try:
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"event: {msg['type']}\ndata: {json.dumps(msg)}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive
                yield ": keepalive\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        if queue in _subscribers:
            _subscribers.remove(queue)


@router.get("")
async def stream_events():
    """SSE endpoint for real-time updates (new articles, cluster refreshes)."""
    queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=256)
    _subscribers.append(queue)

    return StreamingResponse(
        _event_stream(queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
