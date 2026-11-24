# Architecture – Khata Mitra

## High Level Flow

1. User speaks into microphone (browser / Android)
2. Audio streamed via WebSocket to **Gnani Prisma v3.0**
3. Transcript (with code-mix support) received
4. Pipecat pipeline + custom ledger logic processes the intent
5. LLM (optional enrichment) + deterministic parser generate reply
6. Reply sent to **Gnani Timbre v3.0** via WebSocket
7. Audio played back to user

## Why this design wins on the rubric

| Rubric Item              | How we address it                                      |
|--------------------------|--------------------------------------------------------|
| Live judge test (30)     | Fast path + accurate number extraction                 |
| Speech-layer depth (20)  | Full streaming STT + TTS + VAD + barge-in ready         |
| Fit for target user (20) | Designed for low-end phone + noisy shop environment    |
| Innovation (10)          | Hybrid rule + LLM parser, name conflict handling       |
| Responsible AI (10)      | Disclosure, no pressure language, local data           |
| Demo & docs (10)         | Clean README + architecture + text fallback            |

## Data Model

- `customers` (id, name, phone, created_at)
- `transactions` (id, customer_id, amount, type[credit|payment], note, created_at)

All data remains on the device (SQLite). Ready for encryption-at-rest if needed.

## Latency Target

- End of user speech → first agent audio: < 2 seconds (challenge requirement for spoken answers)
