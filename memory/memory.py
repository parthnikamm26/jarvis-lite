import json

MEMORY_FILE = "memory.json"

conversation_history = []


def load_memory():
    global conversation_history

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            conversation_history = json.load(file)

    except FileNotFoundError:
        conversation_history = []

    except Exception as e:
        print(f"[Memory Error] {e}")
        conversation_history = []


def save_memory():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(conversation_history, file, indent=4)

    except Exception as e:
        print(f"[Memory Save Error] {e}")


def add_to_memory(role, text):
    conversation_history.append({
        "role": role,
        "text": text
    })

    if len(conversation_history) > 10:
        conversation_history.pop(0)

    save_memory()


def build_memory_context():
    context = ""

    for entry in conversation_history:
        if entry["role"] == "user":
            context += f"User: {entry['text']}\n"
        else:
            context += f"Jarvis: {entry['text']}\n"

    return context



