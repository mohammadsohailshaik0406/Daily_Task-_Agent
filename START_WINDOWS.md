# Jarvis – Windows Quick Start (Updated)

## 1. One-time setup

```powershell
cd E:\Jarvis_Setup_Package

# Create / activate venv
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# Install packages
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyttsx3 pyaudio
```

## 2. Groq API key (free)

1. Get a key: https://console.groq.com/keys  
2. Save it:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openjarvis"
"YOUR_GROQ_KEY_HERE" | Out-File -Encoding ascii -FilePath "$env:USERPROFILE\.openjarvis\free.key"
```

## 3. Run (two terminals)

**Terminal 1 – Holographic UI**

```powershell
cd E:\Jarvis_Setup_Package
.\.venv\Scripts\Activate.ps1
python jarvis_server.py
```

Browser opens at http://127.0.0.1:8765/

**Terminal 2 – Voice agent**

```powershell
cd E:\Jarvis_Setup_Package
.\.venv\Scripts\Activate.ps1
python jarvis_voice.py
```

## Voice commands

- Open VS Code
- Open Chrome
- Open Gmail
- Open GitHub
- Open Notepad
- Play lofi on YouTube
- Stock market report
- What time is it
- Send WhatsApp message to …

## Notes

- Keep the HUD server running while using voice.
- Do not open the HTML by double-click; use the server URL.
- VS Code must be on PATH (`code` command) for “Open VS Code” to work.
