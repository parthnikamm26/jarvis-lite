import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import time
import tkinter as tk
from tkinter import scrolledtext
import threading
import requests
import random
import subprocess
import ctypes
from vosk import Model, KaldiRecognizer
import pyaudio
import json
from dotenv import load_dotenv


load_dotenv()

JARVIS_PASSWORD = os.getenv("JARVIS_PASSWORD", "parth")

# ============================================================
# API KEY
# ============================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MUSIC_DIR = r"C:\Users\Bhavesh\Music"

# ============================================================
# CONVERSATION MEMORY (last 5 exchanges)
# ============================================================
conversation_history = []

def add_to_memory(role, text):
    conversation_history.append({"role": role, "text": text})
    if len(conversation_history) > 10:  # 5 user + 5 jarvis
        conversation_history.pop(0)

def build_memory_context():
    context = ""
    for entry in conversation_history:
        if entry["role"] == "user":
            context += f"User: {entry['text']}\n"
        else:
            context += f"Jarvis: {entry['text']}\n"
    return context

# ============================================================
# GUI SETUP
# ============================================================
root = tk.Tk()
root.title("JARVIS Lite Console")
root.geometry("700x500")
root.configure(bg="#0a0a0a")

# Status indicator label
status_var = tk.StringVar(value="● STANDBY")
status_label = tk.Label(root, textvariable=status_var, fg="#00ff88", bg="#0a0a0a",
                        font=("Courier New", 10, "bold"), anchor="w", padx=10)
status_label.pack(fill="x")

# Main console text area
text_widget = scrolledtext.ScrolledText(
    root, wrap="word",
    font=("Courier New", 11),
    bg="#0a0a0a", fg="#00ff88",
    insertbackground="#00ff88",
    selectbackground="#003322",
    borderwidth=0, padx=10, pady=10
)
text_widget.pack(expand=True, fill="both")

def gui_log(text, color="#00ff88"):
    text_widget.insert(tk.END, f"{text}\n")
    text_widget.see(tk.END)

def set_status(text):
    status_var.set(f"● {text}")

# ============================================================
# SPEECH ENGINE
# ============================================================
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
engine.setProperty('rate', 150)

def speak(text):
    gui_log(f"JARVIS: {text}")
    add_to_memory("jarvis", text)
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.8)  # prevent mic from picking up speaker

# ============================================================
# VOSK OFFLINE SPEECH MODEL
# ============================================================

vosk_model = Model("models/vosk-model-small-en-us-0.15")

# ============================================================
# OFFLINE COMMAND LISTENER (VOSK)
# ============================================================

def listen_command():
    set_status("LISTENING...")

    recognizer = KaldiRecognizer(vosk_model, 16000)

    mic = pyaudio.PyAudio()

    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8192
    )

    stream.start_stream()

    gui_log("Listening for command...")

    while True:
        data = stream.read(4096, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())

            text = result.get("text", "").strip()

            if text:
                gui_log(f"You said: {text}")
                add_to_memory("user", text)

                stream.stop_stream()
                stream.close()
                mic.terminate()

                set_status("ACTIVE")

                return text.lower()


# ============================================================
# WAKE WORD DETECTION (Google-based, no API key needed)
# ============================================================
def listen_for_wake_word():
    recognizer = KaldiRecognizer(vosk_model, 16000)

    mic = pyaudio.PyAudio()

    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8192
    )

    stream.start_stream()

    set_status("STANDBY — Say 'Hey Jarvis'")

    while True:
        data = stream.read(4096, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())

            text = result.get("text", "").lower()

            if text:
                gui_log(f"[Wake check]: {text}")

            if "hey jarvis" in text or "jarvis" in text:
                stream.stop_stream()
                stream.close()
                mic.terminate()
                return True

# ============================================================
# AUTHENTICATION
# ============================================================
def authenticate():
    speak("Please say the password to continue.")
    password = listen_command()
    return JARVIS_PASSWORD.lower() in password.lower()

# ============================================================
# GEMINI AI (with conversation memory)
# ============================================================
def ask_gemini(prompt, retries=3):
    memory_context = build_memory_context()
    full_prompt = f"""You are JARVIS, a helpful AI assistant. Be concise.

{memory_context}
User: {prompt}
Jarvis:"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"maxOutputTokens": 150, "temperature": 0.7}
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            elif response.status_code == 429:
                wait_time = 20 * (attempt + 1)
                gui_log(f"[Gemini] Quota hit. Retrying in {wait_time} seconds...")
                speak(f"I'm thinking, please wait {wait_time} seconds.")
                time.sleep(wait_time)
            else:
                gui_log(f"[Gemini Error] {response.status_code}: {response.text}")
                return "I'm having trouble thinking right now."
        except Exception as e:
            gui_log(f"[Gemini Exception] {e}")
            return "Something went wrong with my brain."

    return "Sorry, I'm overloaded right now. Please try again in a minute."

# ============================================================
# SYSTEM CONTROLS
# ============================================================
def increase_volume():
    for _ in range(5):
        ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # Volume Up key
        ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
    speak("Volume increased.")

def decrease_volume():
    for _ in range(5):
        ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # Volume Down key
        ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
    speak("Volume decreased.")

def take_screenshot():
    try:
        import PIL.ImageGrab
        import winreg
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            desktop = winreg.QueryValueEx(key, "Desktop")[0]
        except:
            desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        path = os.path.join(desktop, f"screenshot_{timestamp}.png")
        screenshot = PIL.ImageGrab.grab()
        screenshot.save(path)
        speak(f"Screenshot saved to your Desktop.")
        gui_log(f"[Screenshot] Saved: {path}")
    except Exception as e:
        gui_log(f"[Screenshot Error] {e}")
        speak("Couldn't take screenshot. Make sure Pillow is installed.")

def shutdown_pc():
    speak("Shutting down the computer in 10 seconds. Say cancel to stop.")
    time.sleep(3)
    os.system("shutdown /s /t 10")

def restart_pc():
    speak("Restarting the computer in 10 seconds.")
    time.sleep(3)
    os.system("shutdown /r /t 10")

# ============================================================
# TIMER
# ============================================================
def set_timer(command):
    import re
    # Extract number from command e.g. "set a timer for 5 minutes"
    numbers = re.findall(r'\d+', command)
    if not numbers:
        speak("How many minutes should I set the timer for?")
        response = listen_command()
        numbers = re.findall(r'\d+', response)

    if numbers:
        minutes = int(numbers[0])
        speak(f"Timer set for {minutes} minutes.")
        gui_log(f"[Timer] {minutes} minutes started...")

        def timer_thread():
            time.sleep(minutes * 60)
            speak(f"Time's up! Your {minutes} minute timer is done.")
            # Flash the GUI
            for _ in range(5):
                root.configure(bg="#ff0000")
                time.sleep(0.3)
                root.configure(bg="#0a0a0a")
                time.sleep(0.3)

        threading.Thread(target=timer_thread, daemon=True).start()
    else:
        speak("Sorry, I couldn't understand the duration.")

# ============================================================
# JOKES
# ============================================================
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "I told my computer I needed a break. Now it won't stop sending me vacation ads.",
    "Why did the developer go broke? Because he used up all his cache.",
    "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
    "Why do Java developers wear glasses? Because they don't C sharp!",
    "I would tell you a UDP joke, but you might not get it.",
    "There are only 10 types of people in the world: those who understand binary and those who don't.",
    "Why was the computer cold? It left its Windows open.",
]

def tell_joke():
    joke = random.choice(JOKES)
    speak(joke)

# ============================================================
# COMMAND HANDLER
# ============================================================
def handle_command(command):
    if not command:
        return True

    # --- Identity ---
    if "your name" in command:
        speak("I am JARVIS, your Just A Rather Very Intelligent System.")

    # --- Time & Date ---
    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {now}")

    elif "date" in command:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {today}")

    # --- Open Websites ---
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")

    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://google.com")

    elif "open github" in command:
        speak("Opening GitHub")
        webbrowser.open("https://github.com")

    # --- Open Apps ---
    elif "open spotify" in command:
        speak("Opening Spotify")
        try:
            subprocess.Popen(r"C:\Users\Bhavesh\AppData\Roaming\Spotify\Spotify.exe")
        except FileNotFoundError:
            webbrowser.open("https://open.spotify.com")

    elif "open whatsapp" in command:
        speak("Opening WhatsApp")
        try:
            subprocess.Popen(["cmd", "/c", "start", "whatsapp:"])
        except Exception:
            webbrowser.open("https://web.whatsapp.com")

    elif "open vs code" in command or "open vscode" in command or "open visual studio" in command:
        speak("Opening VS Code")
        try:
            subprocess.Popen("code", shell=True)
        except Exception:
            speak("Couldn't open VS Code. Make sure it's installed.")

    elif "open notepad" in command:
        speak("Opening Notepad")
        subprocess.Popen("notepad.exe")

    elif "open calculator" in command:
        speak("Opening Calculator")
        subprocess.Popen("calc.exe")

    # --- Music ---
    elif "play music" in command:
        speak("Please authenticate before playing music.")
        if authenticate():
            try:
                songs = [f for f in os.listdir(MUSIC_DIR)
                         if f.endswith(('.mp3', '.wav', '.flac', '.m4a'))]
                if songs:
                    song_path = os.path.join(MUSIC_DIR, songs[0])
                    os.startfile(song_path)
                    speak(f"Playing {songs[0]}")
                else:
                    speak("No music files found in your Music folder.")
            except Exception as e:
                gui_log(f"[Music Error] {e}")
                speak("Could not play music.")
        else:
            speak("Authentication failed.")

    # --- Timer ---
    elif "timer" in command or "remind" in command:
        set_timer(command)

    # --- Jokes ---
    elif "joke" in command or "funny" in command or "laugh" in command:
        tell_joke()

    # --- Volume ---
    elif "volume up" in command or "increase volume" in command or "louder" in command:
        increase_volume()

    elif "volume down" in command or "decrease volume" in command or "quieter" in command:
        decrease_volume()

    # --- Screenshot ---
    elif "screenshot" in command or "screen capture" in command:
        take_screenshot()

    # --- System ---
    elif "shutdown" in command and "computer" in command:
        speak("Are you sure you want to shut down? Say yes to confirm.")
        confirm = listen_command()
        if "yes" in confirm:
            shutdown_pc()
        else:
            speak("Shutdown cancelled.")

    elif "restart" in command and "computer" in command:
        speak("Are you sure you want to restart? Say yes to confirm.")
        confirm = listen_command()
        if "yes" in confirm:
            restart_pc()
        else:
            speak("Restart cancelled.")

    # --- Exit ---
    elif "exit" in command or "stop" in command or "goodbye" in command:
        speak("Goodbye. Going offline.")
        return False

    # --- AI Fallback (Gemini with memory) ---
    else:
        gui_log("[Gemini] Thinking...")
        response = ask_gemini(command)
        speak(response)

    return True

# ============================================================
# MAIN LOOP
# ============================================================
def run_jarvis():
    speak("JARVIS online. Say Hey Jarvis to activate.")
    while True:
        try:
            if listen_for_wake_word():
                speak("Yes, how can I help?")
                command = listen_command()
                if not handle_command(command):
                    root.quit()
                    break
        except Exception as e:
            gui_log(f"[Error] {e}")
        time.sleep(0.5)

# ============================================================
# LAUNCH
# ============================================================
threading.Thread(target=run_jarvis, daemon=True).start()
root.mainloop()
