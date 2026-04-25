from enum import Enum

class Provider(str, Enum):
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"


MODELS = [
    {
        "id": "llama3.2",
        "label": "🦙 LLaMA 3.2 (Local)",
        "provider": Provider.OLLAMA,
        "description": "Fast, private, runs on your machine",
        "free": True,
    },
    {
        "id": "nvidia/nemotron-3-nano-30b-a3b:free",
        "label": "⚡ NVIDIA: Nemotron 3 Nano 30B A3B",
        "provider": Provider.OPENROUTER,
        "description": "Good reasoning, free OpenRouter model",
        "free": True,
    },
    {
        "id": "openai/gpt-oss-120b:free",
        "label": "🔥 OpenAI: gpt-oss-120b",
        "provider": Provider.OPENROUTER,
        "description": "Better responses, slightly slower",
        "free": True,
    },
    {
        "id": "qwen/qwen3-coder:free",
        "label": "🔥 Qwen: Qwen3 Coder 480B A35B",
        "provider": Provider.OPENROUTER,
        "description": "Better responses, slightly slower",
        "free": True,
    },
]
