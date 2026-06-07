from vosk import Model, KaldiRecognizer
import pyaudio
import json

print("Loading model...")

model = Model("models/vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()

stream = mic.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8192
)

stream.start_stream()

print("Speak something...")

while True:
    data = stream.read(4096, exception_on_overflow=False)

    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "")

        if text:
            print("You said:", text)