from app.core.personalities import PERSONALITIES

def build_rag_prompt(context: str, history: list, user_message: str, personality: str = "default"):
    """
    Builds a prompt that specifically instructs the AI to use provided context.
    """
    messages = []

    # 1. System Personality + RAG Instructions
    base_personality = PERSONALITIES.get(personality, PERSONALITIES["default"])
    rag_instructions = (
        "\n\nCONTEXTUAL INSTRUCTIONS:\n"
        "You have access to specific document segments provided below. "
        "Use this context to answer the user's question accurately. "
        "If the information is not in the context, mention that you couldn't find it in the documents but answer based on your general knowledge if appropriate, or ask for clarification. "
        "Always cite or refer to the 'provided documents' when using them."
    )
    
    messages.append({
        "role": "system",
        "content": base_personality + rag_instructions
    })

    # 2. The Context itself
    messages.append({
        "role": "system",
        "content": f"DOCUMENT CONTEXT:\n{context if context else 'No relevant document context found.'}"
    })

    # 3. Conversation History (trimmed for context window)
    for msg in history[-5:]: # Keep last 5 messages for continuity
        role = "user" if msg.sender == "user" else "assistant"
        messages.append({
            "role": role,
            "content": msg.content
        })

    # 4. Current Question
    messages.append({
        "role": "user",
        "content": user_message
    })

    return messages

def build_resume_prompt(context: str, history: list, user_message: str):
    # Legacy wrapper for OpenRouter endpoint
    return build_rag_prompt(context, history, user_message, personality="default")

def build_messages(history, new_message: str, personality: str = "default"):
    messages = []
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

    messages.append({
        "role": "user",
        "content": new_message
    })

    return messages