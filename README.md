# JARVIS Lite 🧠🎙️

A Python-based voice assistant with wake word detection — inspired by Iron Man's JARVIS.

> Your personal AI that listens, talks, and performs useful tasks on command.

---

## 🚀 Features

- 🗣️ Wake word: `"Hey Jarvis"`
- 🎧 Speech recognition via Google API
- 🔊 Text-to-speech with `pyttsx3`
- 🤖 AI responses powered by **Google Gemini** (with conversation memory)
- 🕒 Time & date
- 🌐 Opens Google, YouTube, GitHub
- 🎵 Plays local music (with voice authentication)
- 📱 Opens Spotify, WhatsApp, VS Code, Notepad, Calculator
- ⏱️ Set voice timers
- 😂 Tells programming jokes
- 🔊 Volume control (up/down)
- 📸 Takes screenshots
- 💾 Conversation memory (last 5 exchanges)
- 🖥️ Dark-themed GUI console

---

## 🛠 Requirements

- Python 3.12
- Windows 10/11
- Working microphone
- Internet connection (for speech recognition + Gemini AI)

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/parthnikam26/jarvis-lite.git
cd jarvis-lite
```

### 2. Create virtual environment
```powershell
py -3.12 -m venv jarvis-env
jarvis-env\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory and add the following:

```env
GEMINI_API_KEY=your_gemini_api_key
JARVIS_PASSWORD=your_password
```

Get a free Gemini API key from:
https://aistudio.google.com/app/apikey

Example:

```env
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXX
JARVIS_PASSWORD=parth
```

The application automatically loads these values when it starts.

### Security Note

Never commit your `.env` file or API keys to GitHub.

The project includes a `.gitignore` file that prevents sensitive credentials from being uploaded to the repository.


### 5. Set your Music folder path
```python
MUSIC_DIR = r"C:\Users\YourName\Music"
```

### 6. Run JARVIS
```bash
python jarvis.py
```

---

## 🎯 Voice Commands

| Command | Action |
|---|---|
| `"Hey Jarvis"` | Wake up |
| `"What's the time?"` | Speaks current time |
| `"What's the date?"` | Speaks today's date |
| `"Open Google"` | Opens Google |
| `"Open YouTube"` | Opens YouTube |
| `"Open GitHub"` | Opens GitHub |
| `"Open Spotify"` | Opens Spotify app |
| `"Open WhatsApp"` | Opens WhatsApp |
| `"Open VS Code"` | Opens VS Code |
| `"Open Notepad"` | Opens Notepad |
| `"Open Calculator"` | Opens Calculator |
| `"Play music"` | Plays local music (needs voice auth) |
| `"Set a timer for 5 minutes"` | Sets a countdown timer |
| `"Tell me a joke"` | Tells a programming joke |
| `"Volume up"` | Increases system volume |
| `"Volume down"` | Decreases system volume |
| `"Take a screenshot"` | Saves screenshot to Desktop |
| `"Shutdown computer"` | Shuts down PC (with confirmation) |
| `"Restart computer"` | Restarts PC (with confirmation) |
| `"Exit"` / `"Goodbye"` | Shuts down JARVIS |
| Any other sentence | Asks Gemini AI (with memory) |

---

## 📁 File Structure

```
jarvis-lite/
├── jarvis.py          # Main assistant logic
├── requirements.txt   # Python dependencies
├── README.md          # Project documentation
└── .gitignore         # Ignored files (API keys, venv)
```

---

## 🔐 Security Note

**Never commit your API key to GitHub.**
Your `.gitignore` excludes config files. Always keep `GEMINI_API_KEY` private.

---

## 🧪 Dependencies

| Package | Purpose |
|---|---|
| `SpeechRecognition` | Voice input |
| `PyAudio` | Microphone access |
| `pyttsx3` | Text-to-speech |
| `requests` | Gemini API calls |
| `Pillow` | Screenshots |
| `pycaw` | Volume control |
| `tkinter` | GUI console |

---

## 💡 Future Plans

- Offline wake word with OpenWakeWord
- Face recognition authentication
- IoT integration (Arduino/NodeMCU)
- Weather command
- GUI dashboard with animations

---

## 🙌 Credits

Created by **Parth Nikam**  
Inspired by Iron Man's J.A.R.V.I.S.  
Built with 💻 and ☕ using Python
