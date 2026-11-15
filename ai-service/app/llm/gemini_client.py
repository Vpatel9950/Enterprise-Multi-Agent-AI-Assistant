"""
Central Gemini LLM Client — using new google-genai SDK
Sab agents yahi use karenge real AI responses ke liye.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger("enterprise.ai.llm")

_client = None
_model_name = "gemini-3.5-flash"
_gemini_available = False

def _init_gemini():
    global _client, _model_name, _gemini_available
    try:
        from google import genai
        from app.config import settings

        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. Using mock responses.")
            return

        _model_name = settings.GEMINI_MODEL_NAME or "gemini-3.5-flash"
        _client = genai.Client(api_key=api_key)
        _gemini_available = True
        logger.info(f"✅ Gemini AI connected: {_model_name}")

    except ImportError:
        logger.warning("google-genai not installed. Run: pip install google-genai")
    except Exception as e:
        logger.error(f"Gemini init failed: {e}")

_init_gemini()


def ask_gemini(
    system_prompt: str,
    user_query: str,
    context: str = "",
    temperature: float = 0.3,
    fallback_response: str = ""
) -> str:
    """
    Call Gemini API. Falls back to fallback_response if unavailable.
    """
    if not _gemini_available or _client is None:
        logger.debug("Gemini not available, using mock response")
        return fallback_response

    try:
        from google import genai

        # Build full prompt
        full_prompt = f"{system_prompt}\n\n"
        if context:
            full_prompt += f"CONTEXT (from company documents):\n{context}\n\n"
        full_prompt += f"USER QUERY: {user_query}\n\nRespond professionally in markdown format."

        config = genai.types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=1024,
        )

        response = _client.models.generate_content(
            model=_model_name,
            contents=full_prompt,
            config=config
        )
        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini API call failed: {e}. Using fallback.")
        if fallback_response:
            return fallback_response
        return f"⚠️ AI response unavailable: {str(e)}"


def is_gemini_available() -> bool:
    return _gemini_available
