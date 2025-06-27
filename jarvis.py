import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import time
import tkinter as tk
import threading
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json
import openai

# =========================
# Configuration
# =========================
openai.api_key = "your-openai-api-key"  # Replace this
vosk_model_path = "vosk-model-small-en-us-0.15"
music_dir = "/home/parthnikamm26/Music"  # ✅ Update to actual music folder

# =========================
# Text-to-Speech Setup
# =========================
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)

def speak(text):
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

# =========================
# GPT Integration
# =========================
def ask_gpt(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT Error: {e}")
        return "I'm having trouble reaching my brain right now."

# =========================
# Wake Word Detection - VOSK
# =========================
model = Model(vosk_model_path)
rec = KaldiRecognizer(model, 16000)
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print("[VOSK STATUS]", status)
    q.put(bytes(indata))

def listen_for_wake_word():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("[VOSK] Listening for wake word...")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                print("[Wake Word Text]:", text)
                if "hey jarvis" in text:
                    return True

# =========================
# Speech Recognition
# =========================
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
    except sr.RequestError:
        speak("Internet connection error.")
    return ""

# =========================
# Authentication
# =========================
def authenticate():
    speak("Please say your password.")
    password = listen_command()
    return password == "1234"

# =========================
# Command Handling
# =========================
def handle_command(command):
    if "your name" in command:
        speak("I am your assistant, Jarvis.")
    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {now}")
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://google.com")
    elif "play music" in command:
        try:
            songs = os.listdir(music_dir)
            if songs:
                os.system(f"xdg-open '{os.path.join(music_dir, songs[0])}'")
                speak("Playing music.")
            else:
                speak("No music files found.")
        except Exception:
            speak("Could not play music. Check your path.")
    elif "delete" in command:
        if authenticate():
            speak("Command authorized. Deleting...")
        else:
            speak("Authentication failed.")
    elif "exit" in command or "shutdown" in command:
        speak("Goodbye Parth. Going offline.")
        return False
    else:
        response = ask_gpt(command)
        speak(response)
    return True

# =========================
# GUI Setup
# =========================
def start_gui():
    root = tk.Tk()
    root.title("JARVIS Lite")
    root.geometry("400x300")

    label = tk.Label(root, text="JARVIS Lite GUI", font=("Helvetica", 16))
    label.pack(pady=10)

    log = tk.Text(root, height=10, width=40)
    log.pack()

    def display(msg):
        log.insert(tk.END, f"{msg}\n")
        log.see(tk.END)

    def jarvis_thread():
        speak("Jarvis is in standby mode. Say 'Hey Jarvis' to activate.")
        while True:
            activated = listen_for_wake_word()
            if activated:
                speak("Yes, how can I help?")
                command = listen_command()
                if not handle_command(command):
                    break
                time.sleep(1)

    threading.Thread(target=jarvis_thread).start()
    root.mainloop()

# =========================
# Start Application
# =========================
start_gui()
