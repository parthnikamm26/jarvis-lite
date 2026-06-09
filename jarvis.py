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

from memory.memory import (
    load_memory,
    add_to_memory,
    build_memory_context
)

from speech.listener import (
    listen_command,
    listen_for_wake_word
)

from memory.user_profile import (
    remember_fact,
    get_fact,
    get_profile
)

from ai.gemini import ask_gemini

from dotenv import load_dotenv

load_dotenv()

JARVIS_PASSWORD = os.getenv("JARVIS_PASSWORD", "parth")

# ============================================================
# API KEY
# ============================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found")
    
MUSIC_DIR = r"C:\Users\Bhavesh\Music"
       
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
# AUTHENTICATION
# ============================================================
def authenticate():
    speak("Please say the password to continue.")
    password = listen_command(
    vosk_model,
    gui_log,
    set_status,
    add_to_memory
)
    return JARVIS_PASSWORD.lower() in password.lower()

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
        response = listen_command(
    vosk_model,
    gui_log,
    set_status,
    add_to_memory
)
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
    if "my name is" in command:   
        
        name = command.replace(
            "my name is",
            ""
        ).strip()

        remember_fact("name", name)

        speak(
            f"I'll remember that your name is {name}"
        )

    elif "what is my name" in command:

        name = get_fact("name")

        if name:
            speak(
                f"Your name is {name}"
            )
        else:
            speak(
                "You haven't told me your name yet."
            )

    elif "your name" in command:
        speak(
            "I am JARVIS, your Just A Rather Very Intelligent System."
        )
        
    elif "my favorite language is" in command:

        language = command.replace(
            "my favorite language is",
            ""
        ).strip()

        remember_fact(
            "favorite_language",
            language
        )

        speak(
            f"I'll remember that your favorite language is {language}"
        )

    elif "what is my favorite language" in command:

        language = get_fact(
            "favorite_language"
        )

        if language:
            speak(
                f"Your favorite language is {language}"
            )
        else:
            speak(
                "You haven't told me your favorite language yet."
            )
            
    elif "i study at" in command:

        college = command.replace(
            "i study at",
            ""
        ).strip()

        remember_fact(
            "college",
            college
        )

        speak(
            f"I'll remember that you study at {college}"
        )

    elif "where do i study" in command:

        college = get_fact(
            "college"
        )

        if college:
            speak(
                f"You study at {college}"
            )
        else:
            speak(
                "You haven't told me where you study yet."
            )
            
    elif "show my profile" in command:

        profile = get_profile()

        speak(
            str(profile)
        )        
                

        

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
        confirm = listen_command(
    vosk_model,
    gui_log,
    set_status,
    add_to_memory
)
        if "yes" in confirm:
            shutdown_pc()
        else:
            speak("Shutdown cancelled.")

    elif "restart" in command and "computer" in command:
        speak("Are you sure you want to restart? Say yes to confirm.")
        confirm = listen_command(
    vosk_model,
    gui_log,
    set_status,
    add_to_memory
)
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
        response = ask_gemini(
    command,
    build_memory_context(),
    GEMINI_API_KEY,
    gui_log,
    speak
)
        speak(response)

    return True

# ============================================================
# MAIN LOOP
# ============================================================
def run_jarvis():
    speak("JARVIS online. Say Hey Jarvis to activate.")
    while True:
        try:
            if listen_for_wake_word(
    vosk_model,
    gui_log,
    set_status
):
                speak("Yes, how can I help?")
                command = listen_command(
    vosk_model,
    gui_log,
    set_status,
    add_to_memory
)
                if not handle_command(command):
                    root.quit()
                    break
        except Exception as e:
            gui_log(f"[Error] {e}")
        time.sleep(0.5)

# ============================================================
# ============================================================
# LAUNCH
# ============================================================

load_memory()

threading.Thread(target=run_jarvis, daemon=True).start()
root.mainloop()