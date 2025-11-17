<div align="center">

# ⚾ SARG

### Speech-Automated Real-time Game Tracker

*A voice-activated baseball scorekeeping system powered by AI*

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Educational](https://img.shields.io/badge/license-Educational-green.svg)](LICENSE)
[![Status: Beta](https://img.shields.io/badge/status-beta-yellow.svg)](https://github.com)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

---

</div>

## 🎯 What is SARG?

SARG transforms the way baseball games are scored by combining **speech recognition** and **natural language processing** to automatically track every play, every out, every run—all from voice announcements.

Simply speak the play, and SARG does the rest.

### ✨ Why SARG?

- 🎤 **Voice-First**: No more manual scorekeeping—just speak naturally
- 🧠 **AI-Powered**: Uses OpenAI Whisper + Local LLM for intelligent parsing
- ⚡ **Real-Time**: Instant updates to game state with every play
- 🔄 **Undo Support**: Made a mistake? Just say "undo" or click a button
- 💾 **Persistent**: Save and load games seamlessly

---

## 🌟 Features

<table>
<tr>
<td width="50%">

### Core Tracking
- ✅ Balls, strikes, and outs
- ✅ Base runners and scoring
- ✅ Inning progression
- ✅ Complete play history
- ✅ All play types supported

</td>
<td width="50%">

### Advanced Features
- 🎙️ Voice command recognition
- 🤖 LLM-based natural language parsing
- 🖥️ Live GUI with PyQt5
- 📝 JSON persistence
- 🔙 Multi-level undo system

</td>
</tr>
</table>

---

## 🏗️ Architecture

```mermaid
graph TB
    A[🎤 Audio Input] -->|MP3 Files| B[Speech Module]
    B -->|Whisper AI| C[Transcription]
    C -->|Clean & Standardize| D[Parser Module]
    D -->|LLM Processing| E[Structured Play Data]
    E --> F[GameState Manager]
    F -->|Update Logic| G[🖥️ PyQt5 GUI]
    F -.->|Save| H[💾 JSON Storage]
    
    style A fill:#e1f5ff
    style D fill:#fff3e0
    style F fill:#f3e5f5
    style G fill:#e8f5e9
```

<details>
<summary><b>🔍 Component Details</b></summary>

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Speech Recognition** | OpenAI Whisper | Converts audio to text |
| **NLP Parser** | LangChain + Ollama | Extracts structured play data |
| **Game Logic** | Python + Pydantic | Manages state and validation |
| **Interface** | PyQt5 | Visual scoreboard display |
| **Storage** | JSON | Persistent game data |

</details>

---

## 🚀 Installation

### Prerequisites

Before you begin, ensure you have:

- 🐍 **Python 3.9+**
- 🎬 **ffmpeg** (for audio processing)
- 🦙 **Ollama** with llama3.1 model

### Quick Start

```bash
# 1️⃣ Clone the repository
cd SARG-project

# 2️⃣ Install Python dependencies
pip install -r requirements.txt

# 3️⃣ Install Ollama (macOS example)
brew install ollama
ollama serve
ollama pull llama3.1

# 4️⃣ Install ffmpeg
brew install ffmpeg  # macOS
# sudo apt-get install ffmpeg  # Linux
```

> 💡 **Windows Users**: Download ffmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)

---

## 💻 Usage

### Basic Workflow

```python
# 1. Prepare your audio files
play_files = ["play1.mp3", "play2.mp3", "play3.mp3"]

# 2. Run SARG
python3 main.py

# 3. Watch the magic happen! ✨
```

### 🎙️ Announcement Format

For best results, follow this structure:

```
[Batter Name] [Action]. Count: [Balls]-[Strikes]. [Base State]. [Outs]. [Score].
```

#### Examples

| Play Type | Announcement |
|-----------|-------------|
| **Ball** | `Marcus takes a ball. Count: 1-0. Bases empty. No outs. Score: 0-0.` |
| **Home Run** | `Jessica hits a home run. Count: 0-0. Bases empty. No outs. Score: 2-0.` |
| **Ground Out** | `Chen grounds out to shortstop. Count: 0-0. Bases empty. 1 out. Score: 2-0.` |
| **Double** | `Sarah doubles to left field. Count: 2-1. Runner on first. 1 out. Score: 3-1.` |

---

## 📁 Project Structure

```
SARG-project/
│
├── 🎯 main.py              # Entry point & orchestration
├── 🎮 gamestate.py         # Core game logic
├── 📋 schema.py            # Data models (Pydantic)
├── 🧠 parse_play.py        # LLM play parser
├── 🎤 speech.py            # Whisper transcription
├── 🖥️ userinterf.py        # PyQt5 GUI
├── 🎙️ recorder.py          # Audio utilities
│
├── 📖 README.md
├── 📦 requirements.txt
└── 📂 audio/
    ├── play1.mp3
    ├── play2.mp3
    └── ...
```

---

## 🔧 How It Works

### The SARG Pipeline

```
┌─────────────────────────────────────────────────────────┐
│  1. AUDIO CAPTURE                                       │
│  🎤 Record or load MP3 files                            │
└───────────────────┬─────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────┐
│  2. TRANSCRIPTION (Whisper)                             │
│  🗣️  "Marcus hits a single to center field"            │
│  🧹 Clean & standardize transcript                      │
└───────────────────┬─────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────┐
│  3. PARSING (LLM)                                       │
│  🤖 Extract structured data:                            │
│     • Play type: "single"                               │
│     • Batter: "Marcus"                                  │
│     • Runner movements                                  │
└───────────────────┬─────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────┐
│  4. STATE UPDATE                                        │
│  🎮 Apply play to game state                            │
│  ✅ Validate logic                                      │
│  💾 Save to history                                     │
└───────────────────┬─────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────┐
│  5. DISPLAY                                             │
│  🖥️  Update GUI scoreboard                             │
│  📊 Show play-by-play                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

### Run Test Sequences

```python
# Complete half-inning test (12 plays)
play_files = [f"test_play{i}.mp3" for i in range(1, 13)]
python3 main.py

# Expected final state:
# AWAY: 3 | HOME: 0 | Inning: Bottom 1, Count: 0-0, Outs: 0
```

### Interactive Testing

Use the included Jupyter notebook:

```python
from gamestate import GameState
from parse_play import parse_transcript

# Create game
game = GameState("HOME", "AWAY")

# Test a play
play = parse_transcript("Marcus hits a single. Count: 0-0...")
game.update(play)
print(game)
```

---

## ⚠️ Known Limitations

| Issue | Description | Workaround |
|-------|-------------|------------|
| 🎯 **LLM Accuracy** | Local model occasionally misparses complex plays | Use GPT-4 for critical games |
| 🎤 **Audio Quality** | Depends on clear recordings | Use high-quality microphone |
| 🔴 **No Live Mode** | Pre-recorded audio only | Future enhancement |
| 🏃 **Complex Runners** | Double plays need manual check | Verify in GUI |

---

## 🚀 Roadmap

### 📅 Phase 1: Core Improvements
- [ ] Live audio recording mode
- [ ] GPT-4 integration for better accuracy
- [ ] Pitch tracking (velocity, location)
- [ ] Player substitutions

### 📅 Phase 2: Platform Expansion
- [ ] Web dashboard
- [ ] Mobile app (iOS/Android)
- [ ] Database backend (PostgreSQL)
- [ ] Multi-game tournament tracking

### 📅 Phase 3: Advanced Features
- [ ] Real-time streaming integration
- [ ] Statistical analysis & reports
- [ ] Support for other sports
- [ ] Machine learning for play prediction

---

## 📊 Performance Metrics

| Operation | Time | Technology |
|-----------|------|------------|
| 🎤 **Transcription** | 2-5s | Whisper (base) |
| 🧠 **Parsing** | 1-3s | llama3.1 |
| ⚡ **State Update** | <0.1s | Python |
| **Total** | **3-8s per play** | - |

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🎉 Open a Pull Request

---

## 📚 Tech Stack

<div align="center">

| Category | Technologies |
|----------|-------------|
| **AI/ML** | ![OpenAI](https://img.shields.io/badge/OpenAI-Whisper-412991?logo=openai) ![Ollama](https://img.shields.io/badge/Ollama-llama3.1-000000) |
| **Framework** | ![LangChain](https://img.shields.io/badge/LangChain-🦜-green) ![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?logo=qt) |
| **Language** | ![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white) |
| **Storage** | ![JSON](https://img.shields.io/badge/JSON-Storage-000000?logo=json) |

</div>

---

## 📝 License

This project is licensed for **educational purposes**.

---

## 🙏 Acknowledgments

Special thanks to:

- 🤖 **OpenAI** for Whisper speech recognition
- 🦙 **Ollama** team for local LLM deployment
- 🦜 **LangChain** for LLM orchestration
- 🖥️ **PyQt5** for the GUI framework
- ⚾ **Baseball enthusiasts** everywhere

---

<div align="center">

**Built with ❤️ for the love of baseball and AI**

*Fall 2024 Academic Project*

[Report Bug](https://github.com/yourusername/sarg/issues) • [Request Feature](https://github.com/yourusername/sarg/issues) • [Documentation](https://github.com/yourusername/sarg/wiki)

</div>
