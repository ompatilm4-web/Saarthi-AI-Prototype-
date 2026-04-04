# Saarthi AI — Technical Architecture & Overview

> Digital India, In Your Voice — A voice-first, multilingual government services assistant

---

## Project Structure

```
Saarthi AI
├── Frontend/               # HTML/CSS/JS web app
│   ├── CSS/                # Stylesheets
│   ├── JS/                 # JavaScript modules
│   └── *.html              # Page files
└── Backend/                # Python FastAPI server
    ├── core/               # AI, DB, TTS services
    ├── models/             # Data models
    ├── rag/                # Document intelligence
    ├── routes/             # API endpoints
    ├── seed/               # DB seed data
    ├── utils/              # Helpers
    └── main.py             # Server entry point
```

---

## Architecture Overview

```
User (Browser)
     │
     ▼
┌─────────────────────────────────────┐
│           FRONTEND                  │
│  index.html → chatbot UI            │
│  login.html → OTP auth              │
│  profile.html → user profile        │
│  apply-scheme.html → applications   │
│  dashboard.html → user dashboard    │
│  JS/main.js → chat + recommendations│
│  JS/api.js  → all backend calls     │
└────────────────┬────────────────────┘
                 │ HTTP (localhost:8080)
                 ▼
┌─────────────────────────────────────┐
│           BACKEND (FastAPI)         │
│  /send-otp     /verify-otp          │
│  /chat         /chat-with-doc       │
│  /profile      /chat-history        │
│  /api/v1/schemes/                   │
│  /api/v1/recommendations/           │
└──┬──────────┬──────────┬────────────┘
   │          │          │
   ▼          ▼          ▼
Supabase   AWS           AWS
(DB)       Bedrock       DynamoDB
           (Claude AI)   (Chat logs)
```

---

## Frontend — Every File Explained

### HTML Pages

| File | Purpose |
|------|---------|
| `index.html` | Main landing page — hero section, chatbot, language switcher, scheme cards, recommendations |
| `login.html` | OTP login via Aadhaar or Mobile number |
| `register.html` | New user registration — collects name, DOB, gender, state, mobile, email |
| `profile.html` | View & edit user profile — name, occupation, income, state, category |
| `dashboard.html` | User's personal dashboard — active schemes, applications, stats |
| `apply-scheme.html` | Browse schemes, check eligibility, fill application form, upload docs |
| `my-schemes.html` | Saved and applied schemes list |
| `education.html` | Education-specific scheme listings |
| `legal.html` | Legal aid and document analysis via AI |
| `admin.html` | Admin panel — scheme management, user overview |
| `admin-login.html` | Separate admin login |

### CSS Files

| File | Purpose |
|------|---------|
| `main.css` | Global styles — layout, hero, chat UI, scheme cards, nav |
| `login.css` | Login & register page specific styles |
| `responsive.css` | Mobile responsiveness — media queries |
| `tts.css` | Text-to-speech button and audio indicator styles |

### JavaScript Files

#### `api.js` — Central API Layer
- All backend calls live here — `sendOtp()`, `verifyOtp()`, `fetchAllSchemes()`, `fetchUserRecommendations()`, `fetchChatHistory()`
- Handles `localStorage` for token (`saarthi_token`) and user (`saarthi_user`)
- `verifyOtp()` merges DB response with locally-saved registration data so no data is lost
- Single source of truth — no other file should call `fetch()` directly to auth endpoints

#### `main.js` — Chat Engine + Recommendations
- `ConversationManager` class — manages full chat history, saves to localStorage and Supabase
- `sendMessageToBackend()` — sends user message + history + profile to `/chat`
- `sendMessageToBackend()` with doc — sends base64 file to `/chat-with-doc`
- `loadPersonalizedRecommendations()` — reads user profile + chat history keywords to fetch matched schemes
- Chat history filter — scans past messages for scheme keywords (agriculture, health, education etc.) and adds `chat_interests` to recommendation profile
- Message buttons — `🔁 Repeat` (re-speaks via TTS), `⏹ Stop`, `✅ Check Eligibility` (only on scheme messages)

#### `auth.js` — Auth Helpers (legacy)
- `isLoggedIn()`, `getUser()`, `logout()` — utility functions
- Logout clears scoped chat history from localStorage
- **Note:** OTP logic has been unified into `api.js`

#### `login.js` — Login Page Logic
- Tab switching (Aadhaar / Mobile)
- OTP send → countdown timer → verify flow
- After successful OTP verify: merges DB user with local registration data, then calls `syncProfileAfterLogin()` to push any locally-saved registration fields back to DB

#### `tts.js` — Text-to-Speech
- `SaarthiTTS` class with `speak(text, langCode, slow)`, `replay()`, `stop()`
- Uses browser `SpeechSynthesis` API
- Picks best available voice for the language
- `window.saarthiTTS` — global instance used by all message buttons

#### `languages.js` — Language Definitions
- Array of 23 Indian languages with `code`, `label` (native script), `name` (English)
- Used to populate language dropdowns and chat language panel

#### `language.js` — Language Persistence
- Reads `saarthi_lang` from localStorage and applies it on page load

#### `voice.js` — Speech Recognition
- Wraps browser `SpeechRecognition` / `webkitSpeechRecognition`
- Auto-detects language from transcript using Unicode character ranges
- Distinguishes Hindi vs Marathi (same Devanagari script) using word markers

#### `mobile.js` — Mobile UX
- Touch event handling, hamburger menu, mobile-specific layout adjustments

---

## Backend — Every File Explained

### Entry Point

#### `main.py`
- Starts FastAPI server on port `8080`
- Registers all route modules (`auth`, `ai`, `schemes`, `recommendations`, `tts`, `legal`, `admin`)
- CORS configured for frontend origin
- Loads `.env` for Supabase and AWS credentials

### Routes (API Endpoints)

#### `routes/auth.py`
- `POST /send-otp` — generates 6-digit OTP, stores in memory dict with 5-min expiry, prints to console in DEV_MODE
- `POST /verify-otp` — validates OTP, fetches or creates user row in Supabase, returns full user object + UUID token
- `PUT /profile` — updates any user profile field in Supabase; `email` and `aadhaar` stored inside `profile` jsonb column since no dedicated columns exist
- DEV_MODE (env var) — skips OTP validation for testing

#### `routes/ai.py`
- `POST /chat` — receives message + language + user profile + history → calls AWS Bedrock (Claude) → returns AI reply + optional TTS audio
- `POST /chat-with-doc` — receives base64 PDF/image + message → Claude analyzes document → returns legal/scheme advice
- `GET /chat-history` — fetches user's past conversations from DynamoDB by mobile number

#### `routes/schemes.py`
- `GET /api/v1/schemes/` — returns all government schemes from Supabase `schemes` table
- `POST /api/v1/schemes/eligibility` — checks if a user profile meets scheme criteria

#### `routes/recommendations.py`
- `POST /api/v1/recommendations/` — basic scheme recommendations by user profile
- `POST /api/v1/recommendations/for-user` — advanced: matches schemes by occupation, age, income, state, gender, caste, AND `chat_interests` (topics from chatbot history)
- `POST /api/v1/recommendations/explain` — LLM explains why a scheme matches a user

#### `routes/tts.py`
- `POST /tts` — converts text to speech using AWS Polly or Bedrock, returns base64 MP3

#### `routes/legal.py`
- Legal document analysis endpoints — powered by Claude via Bedrock

#### `routes/admin.py`
- Admin-only endpoints — scheme CRUD, user management, stats

### Core Services

#### `core/supabase_client.py`
- Initialises Supabase client using `SUPABASE_URL` + `SUPABASE_KEY` env vars
- Used by auth, schemes, recommendations

#### `core/bedrock_client.py`
- AWS Bedrock client setup — used to call Claude AI models
- Handles request formatting for Claude's Messages API

#### `core/recommendation_engine.py`
- Scoring algorithm — matches user profile fields against scheme eligibility criteria
- Weighted scoring: occupation > income > state > age > gender > caste
- `chat_interests` adds bonus score for schemes matching chatbot-discussed topics

#### `core/tts_service.py`
- Text-to-speech logic — calls AWS Polly for supported languages, falls back to Bedrock

#### `core/supabase_bedrock.py`
- Hybrid service — fetches scheme data from Supabase, sends to Bedrock for LLM-enhanced responses

#### `core/Dynamo_bedrock.py`
- DynamoDB operations — stores and retrieves chat history per user session

#### `core/create_tables.py`
- Utility script — creates required Supabase tables if they don't exist

### Models

#### `models/scheme.py`
- Pydantic model for a government scheme — `scheme_id`, `name_en`, `category`, `description`, `benefits`, `eligibility`, `target_group`

### RAG (Document Intelligence)

#### `rag/pipeline.py`
- Retrieval-Augmented Generation pipeline
- Chunks uploaded documents → embeds → retrieves relevant sections → feeds to Claude for answers

#### `rag/autoform.py`
- Auto-fills application forms by reading user documents (Aadhaar, income certificate etc.)

### Seed Data

#### `seed/schemes.py`
- Script to populate Supabase `schemes` table with initial government scheme data

### Utils

#### `utils/audio_utils.py`
- Audio processing helpers — base64 encode/decode, MP3 format conversion

---

## Database — Supabase (PostgreSQL)

### `users` table
```
id           uuid (primary key)
mobile       text (unique)
name         text
full_name    text
age          integer
gender       text
state        text
occupation   text
income       integer
category     text
profile      jsonb   ← stores email, aadhaar, extra fields
created_at   timestamp
```

### `schemes` table
```
scheme_id    text (primary key)
name_en      text
category     text
description  text
benefits     jsonb   ← { amount, type, frequency }
eligibility  jsonb   ← { min_age, max_income, gender, states[] }
target_group text[]
```

### DynamoDB (AWS)
- Table: `saarthi_chat_history`
- Key: `mobile` (partition) + `session_id` (sort)
- Stores: `role`, `message`, `lang`, `created_at`

---

## Process Flows

### 1. User Registration
```
register.html
  → Collects: firstName, lastName, DOB, gender, state, mobile, email, aadhaar
  → Saves to localStorage immediately (saarthi_user)
  → POST /send-otp (creates user row in Supabase)
  → PUT /profile (saves all fields to DB)
  → Redirect to login.html
```

### 2. User Login
```
login.html
  → Enter mobile → POST /send-otp
  → Enter OTP → POST /verify-otp
       → DB: fetch full user row
       → Returns: { token, user }
  → login.js merges DB user with localStorage data
  → syncProfileAfterLogin() → PUT /profile (pushes any missing fields to DB)
  → Redirect to index.html
```

### 3. Chat Message Flow
```
User types/speaks message
  → main.js: sendMessage()
  → conversationManager.addUserMessage()
  → sendMessageToBackend()
       → POST /chat { message, lang, profile, history[last 10] }
       → Backend: Claude AI (Bedrock) processes with context
       → Returns: { reply, tts_audio }
  → Display reply in chat
  → Play TTS audio (base64 MP3 or browser SpeechSynthesis)
  → conversationManager.addAssistantMessage()
  → Save to localStorage + Supabase
```

### 4. Document Analysis Flow
```
User uploads PDF/image
  → File converted to base64
  → POST /chat-with-doc { document, message, profile }
  → Backend: RAG pipeline extracts text → Claude analyzes
  → Returns legal advice / scheme suggestions
```

### 5. Scheme Recommendations Flow
```
Page loads (logged in user)
  → loadPersonalizedRecommendations()
  → Reads user profile from localStorage
  → Scans chat history for keywords → builds chat_interests[]
  → POST /api/v1/recommendations/for-user { profile + chat_interests }
  → Backend: scoring engine ranks schemes
  → Displays scheme cards with match % badge
  → Schemes matching chat_interests show 💬 "From chat" badge
```

### 6. Language Switch Flow
```
User clicks language tag in #languages section
  → switchPageLanguage('hi') called
  → Updates all data-i18n elements on page
  → Updates hero, placeholders, feature cards, footer
  → Sets dir="rtl" for Urdu/Sindhi
  → Saves to localStorage (saarthi_lang)
  → Syncs chat language selector
  → Shows toast notification
```

---

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML, CSS, JavaScript |
| Backend | Python 3.14, FastAPI |
| AI / LLM | AWS Bedrock (Claude) |
| Database | Supabase (PostgreSQL) |
| Chat History | AWS DynamoDB |
| TTS | AWS Polly + Browser SpeechSynthesis |
| STT | Browser Web Speech API |
| Auth | OTP via mobile, UUID tokens |
| Storage | Browser localStorage |
| Hosting | localhost:8080 (backend) |

---

## Environment Variables (`.env`)

```
SUPABASE_URL=
SUPABASE_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
DEV_MODE=true
```

---

*Saarthi AI — Empowering 1.4 billion voices, one conversation at a time*
