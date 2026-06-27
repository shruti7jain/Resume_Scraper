"""
LLM Client — Groq SDK Wrapper
Phase 3 Implementation

Provides a thin wrapper around the Groq Python SDK with:
- Lazy singleton client initialisation
- Automatic retry with exponential backoff (rate-limit & server errors)
- Fallback to a longer-context model when primary exceeds token limits
- Structured JSON response parsing with validation
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import Any

from groq import Groq, RateLimitError, APIStatusError  # type: ignore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_PROMPT_DIR = Path(__file__).parent.parent / "prompts"

_DEFAULT_PRIMARY  = "llama-3.3-70b-versatile"
_DEFAULT_FALLBACK = "mixtral-8x7b-32768"

_MAX_RETRIES      = 3
_RETRY_BASE_DELAY = 2.0   # seconds (doubles each retry)
_TOKEN_LIMIT_HINT = 28_000  # approx threshold; if prompt exceeds this, use fallback

# ---------------------------------------------------------------------------
# Singleton client
# ---------------------------------------------------------------------------
_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY environment variable is not set. "
                "Add it to your .env file."
            )
        _client = Groq(api_key=api_key)
    return _client


# ---------------------------------------------------------------------------
# Prompt loader
# ---------------------------------------------------------------------------

def load_prompt(template_name: str) -> str:
    """
    Load a prompt template from the prompts/ directory.

    Args:
        template_name: File name without path, e.g. 'match_analysis.txt'

    Returns:
        Raw template string with {{placeholder}} variables.
    """
    path = _PROMPT_DIR / template_name
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Core call_groq function
# ---------------------------------------------------------------------------

def call_groq(
    prompt: str,
    model: str | None = None,
    allow_fallback: bool = True,
) -> dict[str, Any]:
    """
    Send a prompt to Groq and return the parsed JSON response.

    Implements:
    - Primary model selection from env (default: llama-3.3-70b-versatile)
    - Automatic fallback to mixtral-8x7b-32768 for long prompts
    - Exponential backoff retry on rate-limit (429) and server errors (5xx)
    - JSON validation on the response

    Args:
        prompt:         The user prompt string
        model:          Optional model override; if None, uses GROQ_MODEL_PRIMARY
        allow_fallback: If True, retry with fallback model on token-limit errors

    Returns:
        dict: Parsed JSON response from the LLM

    Raises:
        RuntimeError: If all retries are exhausted or response is not valid JSON
        EnvironmentError: If GROQ_API_KEY is not set
    """
    primary_model  = model or os.environ.get("GROQ_MODEL_PRIMARY", _DEFAULT_PRIMARY)
    fallback_model = os.environ.get("GROQ_MODEL_FALLBACK", _DEFAULT_FALLBACK)

    # Use fallback immediately for very long prompts
    chosen_model = (
        fallback_model
        if allow_fallback and len(prompt) > _TOKEN_LIMIT_HINT * 3  # ~3 chars/token heuristic
        else primary_model
    )

    last_error: Exception | None = None

    for attempt in range(_MAX_RETRIES):
        try:
            logger.debug(
                "Groq call attempt %d/%d — model=%s prompt_len=%d",
                attempt + 1, _MAX_RETRIES, chosen_model, len(prompt),
            )
            result = _call_once(prompt, chosen_model)
            return result

        except RateLimitError as exc:
            last_error = exc
            wait = _RETRY_BASE_DELAY * (2 ** attempt)
            logger.warning("Groq rate limit hit (attempt %d). Retrying in %.1fs…", attempt + 1, wait)
            time.sleep(wait)

        except APIStatusError as exc:
            # 413 / context-length exceeded → switch to fallback model
            if exc.status_code in (413, 400) and allow_fallback and chosen_model != fallback_model:
                logger.warning(
                    "Token limit exceeded on %s — switching to fallback %s",
                    chosen_model, fallback_model,
                )
                chosen_model = fallback_model
                last_error = exc
                continue

            # 5xx server errors — retry with backoff
            if exc.status_code >= 500:
                last_error = exc
                wait = _RETRY_BASE_DELAY * (2 ** attempt)
                logger.warning("Groq server error %d (attempt %d). Retrying in %.1fs…",
                               exc.status_code, attempt + 1, wait)
                time.sleep(wait)
            else:
                raise  # 4xx (non-rate-limit) are not retried

        except json.JSONDecodeError as exc:
            # Bad JSON from LLM — retry once
            last_error = exc
            logger.warning("LLM returned non-JSON on attempt %d. Retrying…", attempt + 1)
            if attempt >= _MAX_RETRIES - 1:
                raise RuntimeError(
                    f"LLM returned non-JSON after {_MAX_RETRIES} attempts: {exc}"
                ) from exc

    raise RuntimeError(
        f"Groq call failed after {_MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    ) from last_error


def _call_once(prompt: str, model: str) -> dict[str, Any]:
    """
    Make a single Groq API call and parse the JSON response.
    """
    client = _get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,   # Low temp for deterministic, structured output
        max_tokens=4096,
    )
    raw_content = response.choices[0].message.content
    return json.loads(raw_content)
