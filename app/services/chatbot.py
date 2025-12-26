
import requests
import json

def get_bot_response(user_message: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2",  # Change to your model name if needed
        "prompt": user_message
    }
    try:
        response = requests.post(url, json=payload, stream=True)
        full_response = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                full_response += data.get("response", "")
        return full_response if full_response else "No response from model."
    except Exception as e:
        return f"Exception occurred: {str(e)}"
