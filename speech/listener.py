import json
import pyaudio
from vosk import KaldiRecognizer


def listen_command(
    vosk_model,
    gui_log,
    set_status,
    add_to_memory
):
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


def listen_for_wake_word(
    vosk_model,
    gui_log,
    set_status
):
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