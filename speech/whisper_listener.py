import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
import os

print("[Whisper] Loading model...")

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

print("[Whisper] Model loaded.")


def listen_command_whisper():

    fs = 16000

    print("[Whisper] Listening...")

    recording = sd.rec(
        int(5 * fs),
        samplerate=fs,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    temp_file = "temp.wav"

    write(
        temp_file,
        fs,
        recording
    )

    segments, info = model.transcribe(
        temp_file
    )

    text = ""

    for segment in segments:
        text += segment.text + " "

    try:
        os.remove(temp_file)
    except:
        pass

    return text.strip().lower()