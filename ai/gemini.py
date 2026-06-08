import requests
import time


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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 150,
            "temperature": 0.7
        }
    }

    for attempt in range(retries):
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                return data["candidates"][0]["content"]["parts"][0]["text"].strip()

            elif response.status_code == 429:

                gui_log(response.text)

                wait_time = 20 * (attempt + 1)

                gui_log(
                    f"[Gemini] Quota hit. Retrying in {wait_time} seconds..."
                )

                speak(
                    f"I'm thinking, please wait {wait_time} seconds."
                )

                time.sleep(wait_time)

            else:
                gui_log(
                    f"[Gemini Error] {response.status_code}: {response.text}"
                )

                return "I'm having trouble thinking right now."

        except Exception as e:
            gui_log(f"[Gemini Exception] {e}")

            return "Something went wrong with my brain."

    return "Sorry, I'm overloaded right now. Please try again in a minute."