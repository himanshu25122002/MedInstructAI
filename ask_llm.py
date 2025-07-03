import requests

def ask_ollama(prompt, model="medinstruct"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False  # Important: disables chunked streaming
        }
    )

    try:
        return response.json()["response"]
    except Exception as e:
        print("⚠️ Error:", e)
        print("Raw response:", response.text)
        return "Failed to get response from Ollama"
