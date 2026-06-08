import requests


def ask_gemini(
    prompt,
    memory_context,
    api_key,
    gui_log,
    speak,
    retries=3
):
    full_prompt = f"""You are JARVIS, a helpful AI assistant. Be concise.

{memory_context}
User: {prompt}
Jarvis:"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 150,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            return (
                data["candidates"][0]
                ["content"]["parts"][0]
                ["text"]
                .strip()
            )

        elif response.status_code == 429:

            gui_log("[Gemini] Quota exceeded.")
            gui_log(response.text)

            return (
                "My Gemini API quota is unavailable right now. "
                "Please check the Google AI Studio project settings."
            )

        else:

            gui_log(
                f"[Gemini Error] "
                f"{response.status_code}: {response.text}"
            )

            return "I'm having trouble thinking right now."

    except Exception as e:

        gui_log(f"[Gemini Exception] {e}")

        return "Something went wrong with my brain."