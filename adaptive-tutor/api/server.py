"""
FastAPI server — local development entry point.
Mirrors the Vercel Python function interface exactly.
Run with: uvicorn api.server:app --reload --port 8000
"""

import os
import sys
import json
import logging
import asyncio
from typing import AsyncIterator

# Make project root importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local"))

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from schemas.memory import LearnerState
from schemas.confusion import ConfusionSignal
from api.hf_client import HFClient, FALLBACK_RESPONSE
from api.pipeline import run_pipeline
from validators.regex_patterns import check_blocklist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AdaptiveTutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

_hf_client = HFClient(token=os.environ.get("MISTRAL_API_KEY"), model="mistral-small-latest")


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": _hf_client.model}


@app.post("/api/turn")
async def turn_endpoint(request: Request):
    """Main conversation turn handler with streaming response."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    question = body.get("question", "").strip()
    if not question:
        return JSONResponse({"error": "question is required"}, status_code=400)

    # Security: blocklist check on incoming question
    is_clean, matched = check_blocklist(question)
    if not is_clean:
        logger.warning("Blocked question — matched pattern: %s", matched)
        return JSONResponse({"error": "Question contains disallowed content"}, status_code=400)

    # Parse and validate session state
    try:
        raw_state = body.get("session_state", {})
        state = LearnerState(**raw_state) if raw_state else LearnerState()
    except (ValidationError, Exception) as exc:
        logger.warning("Invalid session_state, resetting: %s", exc)
        state = LearnerState()

    return StreamingResponse(
        _stream_turn(question, state),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


async def _stream_turn(
    question: str, state: LearnerState
) -> AsyncIterator[str]:
    """Run the pipeline and stream the answer as SSE events."""
    try:
        async for event in run_pipeline(question, state, _hf_client):
            yield event
    except Exception as exc:
        logger.exception("Pipeline error: %s", exc)
        # Tier 2 fallback — static safe response
        is_clean, _ = check_blocklist(FALLBACK_RESPONSE)
        if is_clean:
            yield _sse("token", {"text": FALLBACK_RESPONSE})
        yield _sse("error", {"message": "An error occurred. Please try again."})
        yield _sse("done", {})


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
