import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import time

# Initialize speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice
engine.setProperty('rate', 150)

# Speak function
def speak(text):
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

# Listen and recognize speech
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
        return ""
    except sr.RequestError:
        speak("Internet connection error.")
        return ""

# Command handling
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
        music_dir = "/home/parthnikamm26/Music"  # Make sure this path is correct
        try:
            songs = os.listdir(music_dir)
            if songs:
                os.system(f"xdg-open '{os.path.join(music_dir, songs[0])}'")
                speak("Playing music.")
            else:
                speak("No music files found.")
        except Exception:
            speak("Could not play music. Check your path.")
    elif "exit" in command or "stop" in command:
        speak("Goodbye, shutting down.")
        return False
    else:
        speak("Sorry, I don't know how to do that yet.")
    return True

# Wake word listener
def listen_for_wake_word():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for wake word...")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        audio = recognizer.listen(source, phrase_time_limit=3)
        print("[DEBUG] Got audio, recognizing...")

    try:
        wake_text = recognizer.recognize_google(audio).lower()
        print(f"[DEBUG] Wake Text: {wake_text}")
        if "hey jarvis" in wake_text:
            return True
    except Exception as e:
        print(f"[DEBUG] Error recognizing wake word: {e}")

    return False

# Main loop with wake word
def run_jarvis_with_wake_word():
    speak("Jarvis is in standby mode. Say 'Hey Jarvis' to activate.")

    while True:
        try:
            activated = listen_for_wake_word()
            if activated:
                speak("Yes, how can I help?")
                command = listen_command()

                if "exit" in command or "shutdown" in command:
                    speak("Goodbye Parth. Going offline.")
                    break

                handle_command(command)

            time.sleep(1)  # Add a short delay to avoid CPU overuse
        except KeyboardInterrupt:
            speak("Interrupted manually. Shutting down.")
            break

# Start JARVIS
run_jarvis_with_wake_word()

