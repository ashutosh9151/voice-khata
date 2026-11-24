# Khata Mitra

**Voice-first Udhaar Khata for Kirana Stores**

[![BolBharat Challenge](https://img.shields.io/badge/BolBharat-Gnani%20Voice%20AI%202026-22c55e?style=flat-square)](https://hackbriven.com/event/bolbharat)
[![STT](https://img.shields.io/badge/STT-Gnani%20Prisma%20v3.0-3b82f6?style=flat-square)](https://docs.gnani.ai)
[![TTS](https://img.shields.io/badge/TTS-Gnani%20Timbre%20v3.0-f97316?style=flat-square)](https://docs.gnani.ai)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

> A real-time voice agent that lets a kirana shopkeeper manage customer credit (udhaar) by speaking — even during rush hour and street noise.

**Track:** PS2 – Voice Khata for kirana stores  
**Challenge:** BolBharat × Gnani Voice AI Innovation Challenge 2026

---

## Why this exists

Most small kirana stores still keep udhaar in a paper khata. During busy hours the shopkeeper cannot type into an app. Speech is fast, heavily code-mixed (Hindi + English), full of numbers and names, and happens over the noise of a busy street.

**Khata Mitra** solves exactly this:

- Shopkeeper says → `"Ramesh ka 340 udhaar"`
- Agent records it and confirms by voice
- Later he can ask → `"Ramesh ka total?"` and get the answer in under 2 seconds

---

## Live Demo Preview

Open `frontend/index.html` in any browser to see the project landing page and conversation flow.

---

## Features

| Feature | Status | Notes |
|---------|--------|-------|
| Streaming STT (WebSocket) | ✅ | Gnani Prisma v3.0 |
| Streaming TTS (WebSocket) | ✅ | Gnani Timbre v3.0 |
| Hindi + English code-mix | ✅ | indic-auto + candidates |
| Number accuracy under noise | ✅ | 340 / teen sau chaalis / three-forty |
| Credit & Payment recording | ✅ | |
| Spoken corrections | ✅ | “nahi, 430” |
| Name disambiguation | ✅ | Asks clarifying question |
| Balance queries < 2s | ✅ | Challenge requirement |
| Today’s summary | ✅ | |
| AI disclosure (first turn) | ✅ | Responsible AI |
| Local SQLite storage | ✅ | No cloud customer data |
| API key never in repo | ✅ | `.env` + `.gitignore` |

---

## Architecture

```
Microphone  ──WebSocket──►  Gnani Prisma v3.0 (STT)
                                │
                                ▼
                         Pipecat Pipeline
                    + Ledger Logic (SQLite)
                    + LLM (optional enrichment)
                                │
                                ▼
Speaker     ◄──WebSocket──  Gnani Timbre v3.0 (TTS)
```

- **Core loop is owned by us** (Pipecat + custom logic)
- No hosted end-to-end agent platform is used as the core
- Fully compliant with challenge rules

---

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| STT | **Gnani Prisma v3.0** | Required + best code-mix |
| TTS | **Gnani Timbre v3.0** | Required + low latency |
| Orchestration | Pipecat | Official Gnani plugin available |
| LLM | Groq (Llama 3.3 / 3.1) | Fast + free tier |
| Database | SQLite | Local, simple, private |
| Language | Python 3.11+ | |

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/<your-username>/voice-khata.git
cd voice-khata
```

### 2. Setup environment

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your keys:

```
GNANI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

### 3. Test Ledger Logic (works on mobile too)

```bash
python main.py
```

Try these:

```
Ramesh ka 340 udhaar
Ramesh ne 200 diya
Ramesh ka total
Aaj kitna udhaar gaya
```

### 4. Full Voice Agent

```bash
python bot.py
```

> Attach a Pipecat transport (Daily / SmallWebRTC) for live microphone.  
> See [Pipecat docs](https://docs.pipecat.ai).

### 5. Landing Page

Open `frontend/index.html` in browser.

---

## Project Structure

```
voice-khata/
├── frontend/
│   └── index.html          # Attractive landing + demo page
├── ledger/
│   ├── db.py               # SQLite operations
│   ├── parser.py           # Intent + amount extraction
│   └── __init__.py
├── prompts/
│   └── system_prompt.py    # Agent persona & guardrails
├── docs/
│   └── architecture.md
├── bot.py                  # Full Pipecat + Gnani voice pipeline
├── main.py                 # Text CLI for testing
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Responsible AI Compliance

- Agent discloses it is an AI in the first turn (in user’s language)
- Only synthetic / demo data used
- No lending advice or pressure language
- API key never committed
- Ledger data stays on device
- No real-person voice cloning

---

## Demo Script for Judges

1. `"Namaste, Ramesh ka 340 udhaar"`
2. `"Ramesh ne 200 diya"`
3. `"Ramesh ka total kitna hai?"`
4. `"Nahi, amount 430 tha"` (correction test)
5. `"Aaj kitna udhaar gaya?"`

---

## Submission Checklist

- [x] Working prototype
- [x] Public GitHub repo
- [x] README with setup + architecture + Gnani services used
- [x] Demo video (2–3 min) — record using the text or voice flow
- [x] Live demo ready
- [x] API key not in public repo

---

## Credits

- **STT**: Gnani Prisma v3.0  
- **TTS**: Gnani Timbre v3.0  
- **Orchestration**: Pipecat  
- **Challenge**: BolBharat – The Gnani Voice AI Innovation Challenge

---

## License

MIT
