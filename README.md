# JARVIS Lite 🧠🎙️

A Python-based voice assistant with custom wake word ("Hey Jarvis") — inspired by Iron Man's JARVIS.

> Your offline personal AI that listens, talks, and performs useful tasks on command.

---

## 🚀 Features

- 🗣️ Custom wake word: `"Hey Jarvis"`
- 🎧 Speech recognition (via Google API)
- 🔊 Text-to-speech with `pyttsx3`
- 🕒 Tells time
- 🌐 Opens Google & YouTube
- 🎵 Plays local music
- 💬 Exit via voice command

---

## 🛠 Requirements

- Python 3.8+
- Works on Linux/Mac/Windows

### Install dependencies:

```bash
pip install -r requirements.txt

requirements.txt includes:
SpeechRecognition==3.10.0
PyAudio==0.2.13
pyttsx3==2.90

HOW TO RUN:
1.Clone the repo:
git clone https://github.com/parthnikam26/jarvis-lite.git
cd jarvis-lite

2.(Optional) Create virtual environment:
python3 -m venv jarvis-env
source jarvis-env/bin/activate

3.Install packages:
pip install -r requirements.txt

4. Run JARVIS:
python3 jarvis.py


🎯 Commands You Can Try
“Hey Jarvis, what’s the time?”

“Hey Jarvis, open Google.”

“Hey Jarvis, play music.”

“Hey Jarvis, shutdown.”

📁 File Structure
jarvis-lite/
├── jarvis.py          # Main assistant logic
├── README.md          # Project readme
├── requirements.txt   # Required Python packages
└── .gitignore         # Ignored files

🧪 Dependencies Used
1.speechrecognition
2.pyttsx3
3.datetime
4.webbrowser
5.os

💡 Future Plans
Offline wake word detection using Vosk or Porcupine
GPT-style natural conversations
GUI dashboard for commands
IoT integration

🙌 Credits
Created by Parth Nikam
Inspired by Iron Man’s J.A.R.V.I.S.
Built with 💻 and ☕ using Python


---

### 🔹 4. Save and Exit

In `nano`, press:

- `Ctrl + O` → to save  
- `Enter` → to confirm  
- `Ctrl + X` → to exit

---

### 🔹 5. Commit & Push the Update

```bash
git add README.md
git commit -m "Updated README with full project info and dependencies"
git push


