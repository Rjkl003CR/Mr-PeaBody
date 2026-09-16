"""Grounded Mr. Peabody prompt construction and answer generation."""

from __future__ import annotations

import os
from typing import Any

import requests

NO_MEMORY_RESPONSE = "That topic has not yet been saved to Mr. Peabody's records."


def build_system_prompt(memories: list[dict[str, Any]]) -> str:
    """Format retrieved memories as the only permitted source of truth."""
    if not memories:
        return (
            "You are Mr. Peabody, a careful personal memory assistant. "
            "No memories were retrieved. Do not invent an answer."
        )

    context = "\n\n".join(
        f"Memory {index}: {memory['text']}\nSource: {memory['metadata']}"
        for index, memory in enumerate(memories, start=1)
    )
    return (
        "You are Mr. Peabody, a precise and helpful personal memory assistant. "
        "Answer using only the retrieved memories below. If the answer is not "
        "supported by them, say that it has not been saved. Never fabricate facts.\n\n"
        f"Retrieved memories:\n{context}"
    )


def generate_answer(
    question: str,
    memories: list[dict[str, Any]],
    api_key: str | None = None,
    model: str = "gpt-4o-mini",
) -> str:
    """Generate a grounded answer, or return the no-memory response."""
    if not memories:
        return NO_MEMORY_RESPONSE
    if not api_key:
        return generate_local_answer(question, memories)

    from openai import OpenAI
    from openai import APIConnectionError, APIStatusError, RateLimitError

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": build_system_prompt(memories)},
                {"role": "user", "content": question},
            ],
        )
    except RateLimitError:
        return (
            "OpenAI is unavailable because the API account has no remaining "
            "credits. Retrieved memory:\n\n"
            + "\n\n".join(memory["text"] for memory in memories)
        )
    except APIConnectionError as error:
        raise RuntimeError(
            "Could not connect to OpenAI. Check your internet connection and try again."
        ) from error
    except APIStatusError as error:
        raise RuntimeError(
            f"OpenAI returned an error ({error.status_code}). Check the model and API settings."
        ) from error

    return response.choices[0].message.content or NO_MEMORY_RESPONSE


def generate_local_answer(
    question: str,
    memories: list[dict[str, Any]],
    model: str | None = None,
    base_url: str | None = None,
) -> str:
    """Generate a grounded answer through a local Ollama server."""
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": build_system_prompt(memories)},
                    {"role": "user", "content": question},
                ],
            },
            timeout=120,
        )
        response.raise_for_status()
    except requests.ConnectionError as error:
        raise RuntimeError(
            "No OpenAI key is configured and Ollama is not running. "
            "Install Ollama, run `ollama pull llama3.2`, then start Ollama."
        ) from error
    except requests.RequestException as error:
        raise RuntimeError(f"Local Ollama request failed: {error}") from error

    answer = response.json().get("message", {}).get("content")
    if not answer:
        raise RuntimeError("Local Ollama returned an empty answer")
    return answer