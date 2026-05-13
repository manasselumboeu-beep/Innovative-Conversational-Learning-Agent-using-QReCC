"""
Hugging Face Inference API client.
Handles retries, streaming, and model fallback.
"""

import os
import time
import json
import logging
import requests
from typing import Iterator

logger = logging.getLogger(__name__)

_HF_API_BASE = "https://api.mistral.ai/v1"

MODELS = [
    "mistral-small-latest",
]

_MAX_RETRIES = 2
_RETRY_BACKOFF = 2.0


class HFClient:
    def __init__(self, token: str | None = None, model: str = MODELS[0]):
        # Prefer explicit token argument, fall back to MISTRAL_API_KEY environment variable
        self.token = token or os.environ.get("MISTRAL_API_KEY", "")
        self.model = model
        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _url(self, model: str) -> str:
        # Chat completions endpoint
        return f"{_HF_API_BASE}/chat/completions"

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.0,
        system: str | None = None,
    ) -> str:
        """Non-streaming generation with retry and model fallback."""
        # Build chat-completion payload for Mistral
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": max(temperature, 0.01),
            "max_tokens": max_tokens,
            "stream": False,
        }

        for attempt in range(_MAX_RETRIES + 1):
            try:
                resp = requests.post(
                    self._url(self.model),
                    headers=self._headers,
                    json=payload,
                    timeout=55,
                )
                # Retry on common transient errors
                if resp.status_code in (429, 503):
                    if attempt < _MAX_RETRIES:
                        logger.warning("HF rate limit/unavailable (status=%s), retrying in %ss", resp.status_code, _RETRY_BACKOFF)
                        time.sleep(_RETRY_BACKOFF)
                        continue
                # If non-200, log body for diagnosis before raising
                if resp.status_code != 200:
                    body = None
                    try:
                        body = resp.text
                    except Exception:
                        body = "<could not read body>"
                    logger.error("Model generate failed (status=%s): %s", resp.status_code, body)
                    # Authentication failure — return a safe fallback for the user and log for admin
                    if resp.status_code == 401:
                        logger.error("Unauthorized: Mistral API key may be invalid or missing (MISTRAL_API_KEY)")
                        return FALLBACK_RESPONSE
                resp.raise_for_status()

                data = resp.json()
                # Mistral-style successful response may include 'choices' (standard) or 'outputs'/'generated_text' (some legacy)
                if isinstance(data, dict):
                    if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                        choice = data["choices"][0]
                        if "message" in choice and isinstance(choice["message"], dict):
                            return choice["message"].get("content", "")
                    if "outputs" in data and isinstance(data["outputs"], list) and data["outputs"]:
                        out = data["outputs"][0]
                        if isinstance(out, dict):
                            return out.get("text") or out.get("generated_text") or str(out)
                    if "generated_text" in data:
                        return data.get("generated_text", "")
                if isinstance(data, list) and data:
                    return data[0].get("generated_text", "")
                return str(data)
            except requests.exceptions.Timeout:
                if attempt < _MAX_RETRIES:
                    logger.warning("HF timeout, retrying (%d/%d)", attempt + 1, _MAX_RETRIES)
                    time.sleep(_RETRY_BACKOFF)
                    continue
                raise
            except Exception as exc:
                logger.exception("Generation failed on attempt %d: %s", attempt + 1, exc)
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_BACKOFF)
                    continue
                raise

        raise RuntimeError("All HF retries exhausted")

    def stream(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 512,
    ) -> Iterator[str]:
        """Token-streaming generation using the text-generation-inference API."""
        # Build chat messages for Mistral chat completions
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            with requests.post(
                self._url(self.model),
                headers=self._headers,
                json=payload,
                stream=True,
                timeout=60,
            ) as resp:
                # If the streaming endpoint rejected the request, log and fall back
                if resp.status_code != 200:
                    body = "<no body>"
                    try:
                        body = resp.text
                    except Exception:
                        pass
                    logger.error("HF stream start failed (status=%s): %s", resp.status_code, body)
                    # Try a non-streaming generate as fallback
                    try:
                        # Non-streaming fallback using chat-completion with a system message
                        text = self.generate(
                            user_message,
                            max_tokens=max_tokens,
                            temperature=0.3,
                            system=system_prompt,
                        )
                        yield text
                        return
                    except Exception as ge:
                        logger.exception("HF fallback generate failed: %s", ge)
                        yield ""
                        return

                for line in resp.iter_lines():
                    if not line:
                        continue
                    line = line.decode("utf-8")
                    if line.startswith("data:"):
                        line = line[5:].strip()
                    if line == "[DONE]":
                        return
                    try:
                        chunk = json.loads(line)
                        token = ""
                        if isinstance(chunk, dict):
                            # Standard format: choices[0].delta.content
                            if "choices" in chunk and isinstance(chunk["choices"], list) and chunk["choices"]:
                                choice = chunk["choices"][0]
                                if "delta" in choice and isinstance(choice["delta"], dict):
                                    token = choice["delta"].get("content", "")
                            # Fallbacks for other formats
                            if not token:
                                if "delta" in chunk:
                                    d = chunk.get("delta")
                                    if isinstance(d, dict):
                                        token = d.get("content", "") or d.get("text", "")
                                    else:
                                        token = str(d)
                                elif "generated_text" in chunk:
                                    token = chunk.get("generated_text", "")
                                elif "output" in chunk:
                                    outs = chunk.get("output")
                                    if isinstance(outs, list) and outs:
                                        for o in outs:
                                            if isinstance(o, dict):
                                                content = o.get("content") or o.get("text")
                                                if isinstance(content, list):
                                                    for c in content:
                                                        if isinstance(c, dict) and c.get("type") == "output_text":
                                                            token += c.get("text", "")
                                                elif isinstance(content, str):
                                                    token += content
                        if token:
                            yield token
                    except json.JSONDecodeError:
                        continue
        except Exception as exc:
            logger.exception("HF stream error: %s", exc)
            # Fall back to non-streaming
            try:
                text = self.generate(
                    user_message,
                    max_tokens=max_tokens,
                    temperature=0.3,
                    system=system_prompt,
                )
                yield text
            except Exception as fallback_exc:
                logger.exception("HF fallback also failed: %s", fallback_exc)
                yield ""

    def generate_with_system(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
    ) -> str:
        """Non-streaming generation with a separate system prompt (chat completion)."""
        return self.generate(
            user_message,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
        )

    @staticmethod
    def _format_instruct(system: str, user: str) -> str:
        """Mistral instruct format: [INST] <<SYS>>...</SYS>> user [/INST]"""
        if system:
            return f"<s>[INST] <<SYS>>\n{system}\n<</SYS>>\n\n{user} [/INST]"
        return f"<s>[INST] {user} [/INST]"


FALLBACK_RESPONSE = (
    "That's a thoughtful question — let me make sure I give you the clearest "
    "answer I can. Could you tell me a bit more about which part feels unclear? "
    "That will help me explain it better."
)
