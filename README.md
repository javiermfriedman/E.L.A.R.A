[# E.L.A.R.A.](https://github.com/user-attachments/assets/f97c235e-2ce1-4978-82fe-470480daab35)

**Enhanced Language Acquisition & Response Agent**


A full-stack AI prank call platform. Build custom voice agents, pick a target from your contacts, and launch a call — E.L.A.R.A. handles the conversation in real-time over the phone while you sit back and listen to the recording.

The entire interface is styled as a classified military operations terminal: CRT scanlines, neon green on black, glitch effects, and monospace everything.

---

## How It Works

1. **Create an agent** — give it a name, personality, system prompt, voice, and avatar.
2. **Add contacts** — names and phone numbers of your targets.
3. **Initiate a call** — pick an agent and a contact, hit launch. Twilio dials the number, connects to a WebSocket, and a Pipecat pipeline runs the conversation using GPT-4 + ElevenLabs TTS + Deepgram STT.
4. **Review recordings** — every call is recorded and saved. Play them back from the Mission Archive.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19, React Router 7, Vite 8, plain CSS |
| Backend | FastAPI, SQLAlchemy, SQLite |
| Voice pipeline | [Pipecat](https://github.com/pipecat-ai/pipecat) (OpenAI GPT-4 + ElevenLabs + Deepgram) |
| Telephony | Twilio (outbound calls + media streams) |
| Tunnel | ngrok (exposes local WebSocket to Twilio) |
| Auth | JWT (python-jose + passlib/bcrypt) |

---

## Project Structure

```
E.L.A.R.A/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, router registration
│   │   ├── config.py            # Env loading, JWT settings
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── dependencies.py      # Shared FastAPI dependencies
│   │   ├── routers/
│   │   │   ├── auth.py          # Register, login, token
│   │   │   ├── agents.py        # CRUD for voice agents
│   │   │   ├── contacts.py      # CRUD for contacts
│   │   │   ├── calls.py         # Call status, cancel, TwiML
│   │   │   └── recordings.py    # List, stream, delete recordings
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/
│   │   │   ├── twilio_service.py    # Twilio call + TwiML generation
│   │   │   └── image_preprocess.py  # Avatar crop/resize
│   │   └── pipelines/
│   │       └── mark_one.py      # Pipecat voice pipeline
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh            # ngrok URL discovery + uvicorn start
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Router, route guards, auth redirects
│   │   ├── context/ElaraContext.jsx
│   │   ├── services/api.js      # All backend API calls
│   │   ├── components/
│   │   │   ├── layout/          # TopBar, Dashboard, AccessGranted, LeftStrip
│   │   │   └── ui/              # PanelWrapper
│   │   ├── panels/
│   │   │   ├── InitiateCall/    # Agent + contact select, launch button
│   │   │   ├── Agents/          # Agent cards, create agent, voice registry
│   │   │   ├── Contacts/        # Contact list + add contact
│   │   │   ├── MissionArchive/  # Call recordings + playback modal
│   │   │   └── SystemStatus/    # Decorative system diagnostics
│   │   ├── pages/login/         # Login + register
│   │   └── styles/              # Global CSS, theme tokens, animations
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- A [ngrok](https://ngrok.com/) account (free tier works)
- API keys for: **Twilio**, **OpenAI**, **ElevenLabs**, **Deepgram**

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/E.L.A.R.A.git
cd E.L.A.R.A
```

### 2. Configure environment variables

Create a `.env` file in the project root with your ngrok auth token:

```bash
cp .env.example .env
```

```
NGROK_AUTHTOKEN=your_ngrok_authtoken
```

Create (or verify) `backend/.env` with your service credentials:

```
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
DEEPGRAM_API_KEY=...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+1...
ENV=local
```

> `LOCAL_SERVER_URL` does **not** need to be set — the backend entrypoint discovers it from ngrok automatically.

### 3. Start everything

```bash
docker compose up --build
```

That's it. Three services come up:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| ngrok dashboard | http://localhost:4040 |

### 4. First use

1. Open http://localhost:5173
2. Register an account
3. Create an agent (name, description, system prompt, first message, voice, avatar image)
4. Add a contact
5. Go to Initiate Call, select the agent and contact, and launch

---

## Running Without Docker

If you prefer running locally without containers:

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

**ngrok (separate terminal):**

```bash
ngrok http 8000
```

Then set `LOCAL_SERVER_URL` in `backend/.env` to the ngrok HTTPS URL.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/` | Register |
| POST | `/auth/token` | Login (OAuth2 form) |
| GET | `/agents/` | List agents |
| POST | `/agents/` | Create agent (multipart) |
| DELETE | `/agents/{id}` | Delete agent |
| GET | `/contacts/` | List contacts |
| POST | `/contacts/` | Create contact (multipart) |
| DELETE | `/contacts/` | Delete all contacts |
| POST | `/dialout` | Initiate a call |
| GET | `/call/status` | Poll call status |
| POST | `/call/cancel` | Cancel active call |
| GET | `/recordings/` | List recordings |
| GET | `/recordings/{id}/audio` | Stream recording audio |
| DELETE | `/recordings/{id}` | Delete recording |
| GET | `/health` | Health check |

---

## Architecture Notes

- **Voice pipeline**: Twilio dials the target, then connects the audio stream via WebSocket to a local Pipecat pipeline. The pipeline chains Deepgram STT → GPT-4 → ElevenLabs TTS, with VAD (voice activity detection) for natural turn-taking.
- **Recordings**: Both channels (agent + target) are captured by an `AudioBufferProcessor` in the pipeline, saved as WAV files locally and as blobs in SQLite.
- **ngrok**: Required because Twilio needs a public HTTPS endpoint to send TwiML webhooks and connect media streams. The Docker entrypoint auto-discovers the tunnel URL so you don't have to copy-paste it.
- **Auth**: JWT tokens issued by the backend, stored in `localStorage` on the frontend. All API calls (except register/login) require a valid token.
- **Routing**: React Router with three routes — `/login`, `/access` (post-login animation), and `/dashboard`. Route guards redirect unauthenticated users to `/login` and bounce already-authenticated users away from the login page. Any unknown path redirects based on auth status.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
