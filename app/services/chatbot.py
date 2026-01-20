
import requests
import json
from app.models.message import ChatMessage
from app.core.personalities import PERSONALITIES
from app.core.models_registry import MODELS
import os

OLLAMA_URL = "http://localhost:11434/api/chat"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

OPENROUTER_API_KEY = "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"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5173",  # required by OpenRouter
    "X-Title": "AI Chatbot Project"            # app name
}

def stream_openrouter_response(messages: list, model_config: dict = None):
    model = model_config["id"] if model_config else "mistralai/devstral-2512:free"
    if not OPENROUTER_API_KEY:
        yield "[ERROR] OpenRouter API key is missing"
        return

    print("model_config:", model)

    payload = {
        "model": model,
        "messages": messages,
        "stream": True
    }

    try:
        with requests.post(
            OPENROUTER_URL,
            headers=HEADERS,
            json=payload,
            stream=True,
            timeout=60
        ) as response:

            # ❌ HTTP errors
            if response.status_code != 200:
                try:
                    err = response.json()
                    message = err.get("error", {}).get("message", "Unknown error")
                except Exception:
                    message = response.text

                yield f"[ERROR] {message}"
                return

            # ✅ Stream tokens
            for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                if not line or not line.startswith("data: "):
                    continue

                data = line.replace("data: ", "")

                if data == "[DONE]":
                    break

                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"]

                    if "content" in delta:
                        yield delta["content"]

                except json.JSONDecodeError:
                    continue

    except Timeout:
        yield "[ERROR] AI service timed out. Please try again."

    except RequestException:
        yield "[ERROR] Unable to connect to AI service."

    except Exception:
        yield "[ERROR] Unexpected server error occurred."

def stream_bot_response(messages: list):
    print("Sending messages to Ollama:", messages)
    payload = {
        "model": "llama3.2",
        "messages": messages,
        "stream": True
    }

    response = requests.post(OLLAMA_URL, json=payload, stream=True)

    for line in response.iter_lines():
        if not line:
            continue

        data = json.loads(line)

        if "message" in data and "content" in data["message"]:
            yield data["message"]["content"]

        if data.get("done"):
            break

def get_chat_history(chat_id: int, db, limit: int = 10):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()[::-1]
    )

def build_ollama_messages(history, new_message: str, personality: str = "default"):
    messages = []

    # ✅ Add system personality FIRST
    system_prompt = PERSONALITIES.get(personality, PERSONALITIES["default"])

    messages.append({
        "role": "system",
        "content": system_prompt
    })

    for msg in history:
        role = "user" if msg.sender == "user" else "assistant"
        messages.append({
            "role": role,
            "content": msg.content
        })

    # Add current user message
    messages.append({
        "role": "user",
        "content": new_message
    })

    return messages

def get_model_config(model_id: str):
    for model in MODELS:
        if model["id"] == model_id:
            return model
    raise ValueError("Invalid model selected")