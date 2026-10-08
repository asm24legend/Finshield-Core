import json
import ollama

# If Ollama hangs or is down, give up after this long instead of waiting forever.
OLLAMA_TIMEOUT_SECONDS = 120
_client = ollama.Client(timeout=OLLAMA_TIMEOUT_SECONDS)


def chat_json(model: str, system_prompt: str, user_prompt: str, fallback: dict) -> dict:
    """
    Calls the local LLM and returns a parsed JSON dict.

    Never raises for LLM problems. Instead it returns the fallback values plus
    "llm_ok": False and an "error" string, so the calling agent can record a
    degraded result rather than crashing the case or faking a clean one.
    """
    try:
        response = _client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            format="json",
        )
    except Exception as e:
        return {**fallback, "llm_ok": False, "error": f"LLM unreachable or timed out ({type(e).__name__})"}

    raw = response["message"]["content"]
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {**fallback, "llm_ok": False, "error": f"LLM returned unparseable output: {raw[:200]}"}

    parsed["llm_ok"] = True
    return parsed