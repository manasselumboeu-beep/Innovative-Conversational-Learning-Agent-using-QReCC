"""
Vercel Python serverless function.
Exposes the same pipeline as server.py via the Vercel handler format.
"""

import os
import sys
import json
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pydantic import ValidationError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import StreamingResponse, JSONResponse

from schemas.memory import LearnerState
from api.hf_client import HFClient, FALLBACK_RESPONSE
from api.pipeline import run_pipeline, _sse
from validators.regex_patterns import check_blocklist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vercel picks up a FastAPI app exported as `app`
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

_hf_client = HFClient(token=os.environ.get("MISTRAL_API_KEY"), model="mistral-small-latest")


@app.post("/api/turn")
async def turn(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    question = body.get("question", "").strip()
    if not question:
        return JSONResponse({"error": "question required"}, status_code=400)

    is_clean, _ = check_blocklist(question)
    if not is_clean:
        return JSONResponse({"error": "Disallowed content"}, status_code=400)

    try:
        raw_state = body.get("session_state", {})
        state = LearnerState(**raw_state) if raw_state else LearnerState()
    except (ValidationError, Exception):
        state = LearnerState()

    async def generate():
        try:
            async for event in run_pipeline(question, state, _hf_client):
                yield event
        except Exception as exc:
            logger.exception("Pipeline error: %s", exc)
            yield _sse("token", {"text": FALLBACK_RESPONSE})
            yield _sse("done", {})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
