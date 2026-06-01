<div align="center">

<!-- Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=220&section=header&text=Saarthi%20AI&fontSize=72&fontColor=fff&animation=twinkling&fontAlignY=36&desc=Digital%20India%2C%20In%20Every%20Voice&descAlignY=58&descSize=22" width="100%"/>

# 🇮🇳 Saarthi AI — *Bridging the Last Mile*

### **Government Services. Any Language. Every Voice.**

<br/>

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Visit_Site-22c55e?style=for-the-badge&labelColor=16a34a)](https://saarthi-ai-frontend.vercel.app)
[![Demo Video](https://img.shields.io/badge/▶️_Demo-Watch_Now-ef4444?style=for-the-badge&labelColor=dc2626)](https://your-demo-link.com)
[![MIT License](https://img.shields.io/badge/📜_License-MIT-3b82f6?style=for-the-badge&labelColor=2563eb)](./LICENSE)

<br/>

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![AWS Bedrock](https://img.shields.io/badge/AWS_Bedrock-FF9900?style=flat-square&logo=amazonaws&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)
![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=flat-square&logo=whatsapp&logoColor=white)

<br/>

> **Saarthi AI** is an AI-powered, voice-first full-stack platform that makes India's **100+ government schemes** and **legal services** accessible to every citizen — in their own language, on any device, regardless of literacy level.

<br/>

---

</div>

## 📌 Table of Contents

| # | Section |
|---|---------|
| 1 | [🔴 The Problem](#-the-problem) |
| 2 | [✅ Our Solution](#-our-solution) |
| 3 | [✨ Core Features](#-core-features) |
| 4 | [🏗️ System Architecture](#%EF%B8%8F-system-architecture) |
| 5 | [🔄 Request Lifecycle](#-request-lifecycle) |
| 6 | [🗺️ Data Model](#%EF%B8%8F-data-model) |
| 7 | [🛠️ Tech Stack](#%EF%B8%8F-tech-stack) |
| 8 | [📂 Project Structure](#-project-structure) |
| 9 | [🚀 Getting Started](#-getting-started) |
| 10 | [🌐 Environment Variables](#-environment-variables) |
| 11 | [📡 API Endpoints](#-api-endpoints) |
| 12 | [🗺️ Roadmap](#%EF%B8%8F-roadmap) |
| 13 | [🤝 Contributing](#-contributing) |
| 14 | [📜 License](#-license) |

---

## 🔴 The Problem

India's digital transformation has accelerated — yet **millions of citizens remain cut off** from services they legally deserve. The barriers are structural and systemic:

```
┌─────────────────────────────────────────────────────────────────────────┐
│   780M+ internet users in India — yet access ≠ understanding            │
│   600M+ regional-language speakers — yet portals are in English/Hindi   │
│   100+ government welfare schemes — yet most go undiscovered            │
└─────────────────────────────────────────────────────────────────────────┘
```

| ⚠️ Barrier | 💥 Real-World Impact |
|---|---|
| 🌐 **Language Diversity** | Portals are in English/Hindi — 600M+ regional speakers are effectively excluded |
| 📖 **Literacy Gap** | Dense legal jargon blocks eligible citizens from understanding and claiming benefits |
| 📵 **UX Inaccessibility** | Interfaces designed for tech-savvy users, not first-time or low-literacy users |
| 🧭 **Scheme Complexity** | 100+ welfare schemes with different eligibility criteria — impossible to navigate alone |
| 🏛️ **Middlemen & Corruption** | Eligible citizens are exploited by intermediaries who charge fees for "assistance" |

> **The result:** Eligible citizens miss welfare, subsidies, and legal protections — not because the schemes don't exist, but because **the system was never designed for them.**

---

## ✅ Our Solution

Saarthi AI is a **multilingual, voice-first AI companion** that removes every barrier between a citizen and their rights — with zero intermediaries.

| 🗣️ Speak | 🔍 Discover | 📄 Understand | 🎧 Hear Back |
|---|---|---|---|
| Ask in any Indian language — spoken or typed | Find schemes matching your exact profile | Upload documents, get plain-language summaries | Responses in natural, regional-accent audio |

**Saarthi removes the intermediary.** No middlemen. No confusion. No exclusion. Just a citizen and their rights.

---

## ✨ Core Features

### 🤖 Conversational AI — AWS Bedrock

![Nova Pro](https://img.shields.io/badge/Nova_Pro-Complex_Reasoning-FF9900?style=flat-square&logo=amazonaws&logoColor=white)
![Nova Lite](https://img.shields.io/badge/Nova_Lite-Fast_Intent-f59e0b?style=flat-square&logo=amazonaws&logoColor=white)

Saarthi uses a **dual-model AI strategy** built on AWS Bedrock in the `ap-south-1` region:

- **`amazon.nova-pro-v1:0`** — Deep multi-step reasoning, complex Q&A, document summarization, and multilingual response generation
- **`amazon.nova-lite-v1:0`** — Sub-100ms intent classification and routing (scheme discovery, legal query, document analysis, general chat)
- **Persistent multi-turn memory** — Full conversation history stored in Supabase PostgreSQL for stateful, contextual sessions
- **Profile-aware personalization** — Responses dynamically adapt to citizen's State, Income Band, Age, and Occupation

---

### 🎙️ Voice & Multilingual Engine

Powered by **Microsoft Edge TTS**, Saarthi speaks India's languages with natural prosody and regional accents:

![Hindi](https://img.shields.io/badge/Hindi-हिंदी-FF9933?style=flat-square)
![Marathi](https://img.shields.io/badge/Marathi-मराठी-ff5733?style=flat-square)
![Bengali](https://img.shields.io/badge/Bengali-বাংলা-007bff?style=flat-square)
![Telugu](https://img.shields.io/badge/Telugu-తెలుగు-6f42c1?style=flat-square)
![Tamil](https://img.shields.io/badge/Tamil-தமிழ்-28a745?style=flat-square)
![Kannada](https://img.shields.io/badge/Kannada-ಕನ್ನಡ-dc3545?style=flat-square)
![Gujarati](https://img.shields.io/badge/Gujarati-ગુજરાતી-17a2b8?style=flat-square)
![Punjabi](https://img.shields.io/badge/Punjabi-ਪੰਜਾਬੀ-e67e22?style=flat-square)
![Odia](https://img.shields.io/badge/Odia-ଓଡ଼ିଆ-8e44ad?style=flat-square)

**15+ Indian languages** supported with regional accents built for community trust. Designed for first-time internet users more comfortable speaking than typing.

**Voice Pipeline:**
1. **Speech-to-Text** — Browser Web Speech API captures voice input in real-time
2. **Text Transmission** — Transcribed text sent to FastAPI backend with language code
3. **AI Processing** — Nova Pro generates response in the user's native language
4. **Text-to-Speech** — Edge TTS synthesizes natural audio (e.g., `mr-IN-AarohiNeural` for Marathi)
5. **Audio Playback** — Streamed `.mp3` played back directly in the browser UI

---

### 📚 RAG-Powered Scheme Discovery

Saarthi's knowledge base uses **Retrieval-Augmented Generation (RAG)** to deliver precise, contextual answers about government schemes:

- **Vector Embeddings** — All scheme documents are embedded and stored in a custom vector store
- **Semantic Search** — User queries are embedded and matched against the knowledge base using cosine similarity
- **Context Injection** — Top-3 relevant scheme chunks are injected into the Nova Pro prompt for grounded, hallucination-resistant answers
- **Profile Filtering** — Eligibility criteria (state, income, age, occupation) pre-filter retrieved chunks before LLM reasoning

**Supported Scheme Categories:**
- Agriculture & Farmer Welfare (PM-KISAN, Fasal Bima)
- Women & Child Development (Sukanya Samriddhi, Ujjwala)
- Housing & Urban Development (PMAY)
- Education & Scholarships
- Healthcare (Ayushman Bharat)
- Employment & Skill Development (MGNREGS)
- Social Security & Pension

---

### 📄 Legal Document Analysis

![Pytesseract](https://img.shields.io/badge/Pytesseract-OCR_Engine-4caf50?style=flat-square&logo=python&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-Image_Processing-2196f3?style=flat-square&logo=python&logoColor=white)
![PDF Supported](https://img.shields.io/badge/PDF-Supported-red?style=flat-square&logo=adobeacrobatreader&logoColor=white)

Citizens can upload any government document and receive a plain-language summary:

- Upload government notices, legal letters, court summons, or scanned PDFs
- **Pytesseract + Pillow** pipeline performs high-accuracy OCR on images and scanned documents
- **Nova Pro** analyzes extracted text and summarizes in the citizen's chosen language
- Output highlights **key rights**, **deadlines**, **required actions**, and **legal implications**
- Works with handwritten forms, official stamps, blurry scans — not just clean digital PDFs

---

### 📊 Admin & Analytics Dashboard

Built for government stakeholders and programme managers to understand citizen needs at scale:

| Metric | Description |
|---|---|
| 🔥 **Trending Queries** | Most searched schemes and questions in real time — showing which schemes citizens are most confused about |
| 🗺️ **Language Distribution Map** | Active languages and query volumes by region |
| ❌ **Failed/Unresolved Queries** | Queries where Saarthi couldn't find an answer — signals knowledge base gaps |
| 📈 **Engagement Trends** | Daily/weekly active citizens segmented by state, language, and scheme category |
| 👥 **User Demographics** | Anonymized income band, occupation, and age distribution of active users |

All analytics are powered by Supabase's real-time PostgreSQL and accessible via a protected admin route (`/admin`).

---

### 💬 WhatsApp Integration *(Beta)*

![WhatsApp Bot](https://img.shields.io/badge/WhatsApp_Bot-Beta-25D366?style=flat-square&logo=whatsapp&logoColor=white)

A low-latency WhatsApp bot for citizens without smartphone access or high-speed internet:

- **Webhook-based** — FastAPI receives and processes WhatsApp messages via Meta's Cloud API
- **Same AI backend** — Uses identical Nova Pro + RAG pipeline as the web interface
- **Text-only mode** — No app download required; works on any phone with WhatsApp
- **Meeting citizens where they are** — 500M+ Indians already use WhatsApp daily

---

### 🔐 Authentication & Session Management

- **JWT-based authentication** via Supabase Auth
- Secure user sessions with token refresh
- Complete conversation history persisted per user
- Anonymous query logging for analytics (privacy-preserving)

---

## 🏗️ System Architecture

> End-to-end view of how Saarthi AI processes a citizen's request — from voice input to spoken response.

```
                        ┌─────────────────────────────────────┐
                        │         👤 CITIZEN                  │
                        │   Voice · Text · Document Upload    │
                        └──────────────┬──────────────────────┘
                                       │
                        ┌─────────────▼──────────────────────────────────┐
                        │         🖥️ FRONTEND LAYER — Vanilla JS          │
                        │                                                  │
                        │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
                        │  │ index.html│  │ voice.js │  │    api.js    │  │
                        │  │  UI Shell │  │ STT/TTS  │  │  API Client  │  │
                        │  └──────────┘  └──────────┘  └──────────────┘  │
                        │             Hosted on Vercel                     │
                        └─────────────────┬──────────────────────────────┘
                                          │ REST API (HTTP/HTTPS)
                        ┌─────────────────▼──────────────────────────────┐
                        │       ⚡ FastAPI Server — Uvicorn Port 8080     │
                        │                                                  │
                        │  /auth   /ai/chat   /schemes   /admin           │
                        └──────┬───────────────────┬───────────┬──────────┘
                               │                   │           │
             ┌─────────────────▼──┐   ┌────────────▼──┐  ┌────▼────────────────┐
             │  🤖 AI LAYER       │   │  📚 RAG LAYER  │  │  🗃️ DATA LAYER       │
             │                    │   │                │  │                     │
             │  ┌──────────────┐  │   │  ┌──────────┐ │  │  ┌───────────────┐  │
             │  │ Nova Lite    │  │   │  │ Embedder │ │  │  │ Supabase Auth │  │
             │  │ Intent Classif│  │   │  │(Vectorize│ │  │  │ JWT Sessions  │  │
             │  └──────┬───────┘  │   │  └────┬─────┘ │  │  └───────────────┘  │
             │         │          │   │       │        │  │                     │
             │  ┌──────▼───────┐  │   │  ┌────▼─────┐ │  │  ┌───────────────┐  │
             │  │ Nova Pro     │  │   │  │ Vector DB│ │  │  │ Chat History  │  │
             │  │ Reasoning    │  │   │  │ Semantic │ │  │  │  PostgreSQL   │  │
             │  │ Generation   │  │   │  │ Search   │ │  │  └───────────────┘  │
             │  └──────┬───────┘  │   │  └────┬─────┘ │  │                     │
             │         │          │   │       │Context │  │  ┌───────────────┐  │
             │  ┌──────▼───────┐  │   └───────┘        │  │  │ Query Logs    │  │
             │  │ Edge TTS     │  │                     │  │  │ Analytics     │  │
             │  │ 15+ Languages│  │                     │  │  └───────────────┘  │
             │  └──────────────┘  │                     │  │ Supabase Cloud      │
             └────────────────────┘                     │  └─────────────────────┘
                        │                               │
             ┌──────────▼───────────────────────────────────────┐
             │          ☁️ AWS BEDROCK — ap-south-1              │
             │                                                    │
             │   amazon.nova-pro-v1:0      amazon.nova-lite-v1:0 │
             │   Deep Reasoning            Fast Intent Classify   │
             │   Multilingual Generation   Sub-100ms Response     │
             └────────────────────────────────────────────────────┘
                        │
             ┌──────────▼──────────────────┐
             │    🔗 INTEGRATIONS          │
             │                             │
             │  💬 WhatsApp Bot (Beta)     │
             │  🛡️ Admin Dashboard         │
             └─────────────────────────────┘
```

---

## 🔄 Request Lifecycle

> A single voice query — from Marathi speech to spoken audio response.

```
Citizen          Frontend           FastAPI          Supabase           Nova Lite       RAG            Nova Pro         Edge TTS
   │                 │                  │                │                   │             │                │                │
   │── Speaks in ───►│                  │                │                   │             │                │                │
   │   Marathi       │                  │                │                   │             │                │                │
   │                 │── STT (Browser)──┤                │                   │             │                │                │
   │                 │   (text ready)   │                │                   │             │                │                │
   │                 │── POST /ai/chat ─►                │                   │             │                │                │
   │                 │   {text, lang,   │                │                   │             │                │                │
   │                 │    user_id}      │                │                   │             │                │                │
   │                 │                  │── Verify JWT ──►                   │             │                │                │
   │                 │                  │                │── ✅ Authenticated─┤             │                │                │
   │                 │                  │                │                   │             │                │                │
   │                 │                  │── Classify ────────────────────────►             │                │                │
   │                 │                  │   Intent       │                   │             │                │                │
   │                 │                  │                │                   │─intent:────►│                │                │
   │                 │                  │                │                   │ scheme_disc │                │                │
   │                 │                  │                │                   │             │                │                │
   │                 │                  │── Embed Query ─────────────────────────────────►│                │                │
   │                 │                  │                │                   │             │── Top 3 ───────┤                │
   │                 │                  │                │                   │             │   Chunks       │                │
   │                 │                  │                │                   │             │                │                │
   │                 │                  │── Generate ────────────────────────────────────────────────────►│                │
   │                 │                  │   Response     │                   │             │                │                │
   │                 │                  │   (nova-pro    │                   │             │                │── Marathi ─────┤
   │                 │                  │    + context)  │                   │             │                │   Text         │
   │                 │                  │                │                   │             │                │                │
   │                 │                  │── TTS Synthesize───────────────────────────────────────────────────────────────►│
   │                 │                  │   (mr-IN voice)│                   │             │                │                │
   │                 │                  │                │                   │             │                │◄── Audio ──────┤
   │                 │                  │                │                   │             │                │    Stream      │
   │                 │                  │── Save History ►                   │             │                │                │
   │                 │                  │                │                   │             │                │                │
   │◄── 🔊 Spoken ───│◄── {text, audio}─┤                │                   │             │                │                │
   │    Marathi      │                  │                │                   │             │                │                │
   │    Response     │                  │                │                   │             │                │                │
```

---

## 🗺️ Data Model

> Core database entities powering Saarthi's personalized scheme recommendations and session management.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          SUPABASE POSTGRESQL SCHEMA                             │
└──────────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────┐           ┌───────────────────────────┐
  │         CITIZEN          │           │          SESSION           │
  ├─────────────────────────┤           ├───────────────────────────┤
  │ 🔑 id          UUID PK  │───────────│ 🔑 id         UUID PK     │
  │    name        STRING   │    1:N    │ 🔗 citizen_id  UUID FK    │
  │    state       STRING   │           │    messages    JSONB       │
  │    language    STRING   │           │    language    STRING      │
  │    age         INT      │           │    updated_at  TIMESTAMP  │
  │    income_band STRING   │           └───────────────────────────┘
  │    occupation  STRING   │
  │    phone       STRING   │           ┌───────────────────────────┐
  │    created_at  TIMESTAMP│           │         SCHEME             │
  └─────────────────────────┘           ├───────────────────────────┤
              │                         │ 🔑 id         UUID PK     │
              │ 1:N                     │    name        STRING      │
              ▼                         │    ministry    STRING      │
  ┌─────────────────────────┐           │    category    STRING      │
  │        QUERY_LOG         │           │    eligibility JSONB       │
  ├─────────────────────────┤           │    benefit_type STRING     │
  │ 🔑 id         UUID PK   │           │    languages   STRING[]    │
  │ 🔗 citizen_id  UUID FK  │           │    embedding   VECTOR      │
  │    query_text  STRING   │           └───────────────────────────┘
  │    language    STRING   │
  │    intent      STRING   │
  │    resolved    BOOLEAN  │
  │    logged_at   TIMESTAMP│
  └─────────────────────────┘
```

**Entity Relationships:**
- `CITIZEN` has many `SESSION` (one-to-many) — each citizen can have multiple conversation sessions
- `CITIZEN` generates many `QUERY_LOG` (one-to-many) — every query is logged for analytics
- `SESSION` references many `SCHEME` (many-to-many) — each session can surface multiple relevant schemes
- `SCHEME.embedding` (VECTOR type) — enables semantic similarity search via pgvector

---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.10+ | Core backend runtime |
| **FastAPI** | Latest | Async REST API framework |
| **Uvicorn** | Latest | ASGI server (port 8080) |
| **AWS Bedrock** | `ap-south-1` | LLM inference (Nova Pro + Nova Lite) |
| **boto3** | Latest | AWS SDK for Python |
| **Supabase** | Latest | Auth, PostgreSQL, real-time analytics |
| **Edge TTS** | Latest | Microsoft multilingual voice synthesis |
| **Pytesseract** | Latest | OCR engine for document analysis |
| **Pillow** | Latest | Image preprocessing for OCR pipeline |
| **python-jose** | Latest | JWT token handling |
| **python-multipart** | Latest | File upload handling |
| **asyncio** | Built-in | Async I/O for concurrent requests |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| **HTML5** | — | Application shell (`index.html`) |
| **CSS3** | — | Responsive design system (`styles.css`) |
| **Vanilla JavaScript** | ES2022+ | Zero-dependency UI layer |
| **Web Speech API** | Browser | Real-time speech-to-text recognition |
| **Fetch API** | Browser | Backend communication (`api.js`) |
| **Audio API** | Browser | TTS audio playback (`voice.js`) |

### Infrastructure & Deployment

| Service | Purpose |
|---|---|
| **Vercel** | Frontend deployment (CDN, edge functions) |
| **AWS Bedrock** (`ap-south-1`) | LLM inference — Nova Pro & Nova Lite |
| **Supabase** | Managed PostgreSQL + Auth + Realtime |
| **Meta WhatsApp Cloud API** | WhatsApp Bot webhook integration |

### AI/ML Models

| Model ID | Tier | Use Case |
|---|---|---|
| `amazon.nova-pro-v1:0` | Heavy | Deep reasoning, multilingual generation, document summarization |
| `amazon.nova-lite-v1:0` | Fast | Intent classification, routing decisions (sub-100ms) |
| Microsoft Edge TTS | — | Voice synthesis in 15+ Indian languages |
| Pytesseract (Tesseract 5) | — | OCR on government documents and scanned PDFs |

---

## 📂 Project Structure

```
Saarthi-AI-Prototype/
│
├── 📁 Backend/                          # Python / FastAPI Core
│   │
│   ├── 🐍 main.py                       # Application entry point
│   │                                    #   - FastAPI app initialization
│   │                                    #   - CORS middleware configuration
│   │                                    #   - Route registration
│   │                                    #   - Uvicorn server launch
│   │
│   ├── 📁 routes/                       # API Route Handlers (v1)
│   │   ├── 🔐 auth.py                   # JWT authentication & user management
│   │   │                                #   POST /auth/register
│   │   │                                #   POST /auth/login
│   │   │                                #   POST /auth/logout
│   │   │                                #   GET  /auth/me
│   │   │
│   │   ├── 🤖 ai.py                     # Core AI endpoints
│   │   │                                #   POST /ai/chat        — Main conversation
│   │   │                                #   POST /ai/voice       — Voice TTS synthesis
│   │   │                                #   POST /ai/document    — OCR + summarization
│   │   │                                #   GET  /ai/history     — Chat history
│   │   │
│   │   ├── 📋 schemes.py                # Scheme discovery endpoints
│   │   │                                #   GET  /schemes/       — List all schemes
│   │   │                                #   GET  /schemes/search — Profile-filtered search
│   │   │                                #   GET  /schemes/{id}   — Scheme detail
│   │   │
│   │   └── 📊 admin.py                  # Admin & analytics endpoints
│   │                                    #   GET  /admin/analytics  — Dashboard data
│   │                                    #   GET  /admin/queries    — Query log
│   │                                    #   GET  /admin/languages  — Language distribution
│   │
│   ├── 📁 core/                         # Shared Infrastructure Clients
│   │   ├── ☁️ bedrock_client.py          # AWS Bedrock connection & model invocation
│   │   │                                #   - Nova Pro inference
│   │   │                                #   - Nova Lite intent classification
│   │   │                                #   - Streaming response handling
│   │   │
│   │   └── 🗄️ supabase_client.py        # Supabase connection & query helpers
│   │                                    #   - Auth verification
│   │                                    #   - Chat history read/write
│   │                                    #   - Query log insertion
│   │                                    #   - Analytics aggregation
│   │
│   ├── 📁 rag/                          # Retrieval-Augmented Generation
│   │   └── 📚 knowledge_base/           # Indexed scheme documents & embeddings
│   │                                    #   - Government scheme JSON files
│   │                                    #   - Pre-computed vector embeddings
│   │                                    #   - Retriever logic (semantic search)
│   │
│   └── 📁 seed/
│       └── 🌱 schemes_data.py           # Initial scheme data & seeding scripts
│                                        #   - 100+ scheme definitions
│                                        #   - Eligibility criteria mapping
│                                        #   - Embedding generation pipeline
│
├── 📁 Frontend/                         # Static HTML / CSS / JS Interface
│   │
│   ├── 🌐 index.html                    # Application shell
│   │                                    #   - Single-page application structure
│   │                                    #   - Language selector component
│   │                                    #   - Chat interface layout
│   │                                    #   - Document upload zone
│   │                                    #   - User profile panel
│   │
│   ├── 📁 JS/
│   │   ├── 🎙️ voice.js                  # Speech Recognition & Audio Playback
│   │   │                                #   - Web Speech API integration
│   │   │                                #   - Language-aware STT configuration
│   │   │                                #   - Audio stream management
│   │   │                                #   - TTS playback controller
│   │   │
│   │   ├── 🔌 api.js                    # Backend API Communication Layer
│   │   │                                #   - Fetch-based API client
│   │   │                                #   - JWT token management
│   │   │                                #   - Request/response interceptors
│   │   │                                #   - Error handling & retries
│   │   │
│   │   └── 🎨 ui.js                     # UI State Management & Event Handlers
│   │                                    #   - Chat message rendering
│   │                                    #   - Loading states
│   │                                    #   - Language preference persistence
│   │                                    #   - Document drag-and-drop handling
│   │
│   └── 📁 CSS/
│       └── 🎨 styles.css                # Responsive Design System
│                                        #   - CSS custom properties (tokens)
│                                        #   - Mobile-first responsive layout
│                                        #   - RTL language support
│                                        #   - Dark/light mode variables
│                                        #   - Accessibility styles
│
├── 📄 .gitignore                        # Git ignore rules (excludes .env, venv, __pycache__)
├── 📄 requirements.txt                  # Python dependencies (pip install)
└── 📄 README.md                         # This file
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following before cloning:

| Requirement | Minimum Version | Check |
|---|---|---|
| Python | 3.10+ | `python --version` |
| pip | Latest | `pip --version` |
| Tesseract OCR | 5.0+ | `tesseract --version` |
| AWS Account | — | Bedrock access enabled in `ap-south-1` |
| Supabase Project | — | Project URL + anon key ready |

**Install Tesseract OCR** (required for document analysis):
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-hin tesseract-ocr-mar

# macOS
brew install tesseract

# Windows
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
```

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/ompatilm4-web/Saarthi-AI-Prototype-.git
cd Saarthi-AI-Prototype-/Backend
```

---

### Step 2 — Create & Activate Virtual Environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

Key packages installed:
- `fastapi` + `uvicorn[standard]` — API server
- `boto3` — AWS Bedrock SDK
- `supabase` — Database & auth client
- `edge-tts` — Multilingual TTS engine
- `pytesseract` + `Pillow` — OCR pipeline
- `python-jose[cryptography]` — JWT handling
- `python-multipart` — File upload support

---

### Step 4 — Configure Environment Variables

```bash
cp .env.example .env
```

Then edit `.env` with your credentials (see [Environment Variables](#-environment-variables) section below).

---

### Step 5 — Seed the Knowledge Base *(Optional but recommended)*

```bash
python seed/schemes_data.py
```

This populates the vector knowledge base with 100+ government scheme documents and pre-computes embeddings.

---

### Step 6 — Start the Backend Server

```bash
uvicorn main:app --reload --port 8080
```

| Endpoint | URL |
|---|---|
| 🔌 API Base | `http://localhost:8080` |
| 📖 Swagger UI | `http://localhost:8080/docs` |
| 📘 ReDoc | `http://localhost:8080/redoc` |
| 💓 Health Check | `http://localhost:8080/health` |

---

### Step 7 — Launch the Frontend

```bash
cd ../Frontend

# Option A: Using npx serve (recommended)
npx serve .

# Option B: Using Python's built-in server
python -m http.server 3000

# Option C: Open directly in browser
open index.html
```

Navigate to `http://localhost:3000` (or the serve URL) to use the application.

---

## 🌐 Environment Variables

Create a `.env` file in the `Backend/` directory with the following variables:

```env
# ── Server Configuration ─────────────────────────────────────────────────
PORT=8080
DEBUG=false
ALLOWED_ORIGINS=http://localhost:3000,https://saarthi-ai-frontend.vercel.app

# ── AWS Credentials ───────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=ap-south-1
BEDROCK_REGION=us-east-1

# ── AWS Bedrock Model IDs ─────────────────────────────────────────────────
NOVA_PRO_MODEL_ID=amazon.nova-pro-v1:0
NOVA_LITE_MODEL_ID=amazon.nova-lite-v1:0

# ── Supabase ──────────────────────────────────────────────────────────────
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_role_key

# ── JWT ───────────────────────────────────────────────────────────────────
JWT_SECRET=your_jwt_secret_key_min_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# ── WhatsApp (Beta) ───────────────────────────────────────────────────────
WHATSAPP_TOKEN=your_meta_whatsapp_cloud_api_token
WHATSAPP_VERIFY_TOKEN=your_webhook_verify_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

> ⚠️ **Security Warning:** Never commit your `.env` file. It is already listed in `.gitignore`. Use environment secrets in production (Vercel, AWS Secrets Manager, etc.).

---

## 📡 API Endpoints

### Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register` | Register new citizen | ❌ |
| `POST` | `/auth/login` | Login and receive JWT | ❌ |
| `POST` | `/auth/logout` | Invalidate session | ✅ |
| `GET` | `/auth/me` | Get current user profile | ✅ |

### AI Chat & Voice (`/ai`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/ai/chat` | Send text/voice query, receive AI response | ✅ |
| `POST` | `/ai/voice` | Generate TTS audio for given text + language | ✅ |
| `POST` | `/ai/document` | Upload image/PDF for OCR + AI summarization | ✅ |
| `GET` | `/ai/history` | Retrieve conversation history | ✅ |
| `DELETE` | `/ai/history` | Clear conversation history | ✅ |

**`POST /ai/chat` Request Body:**
```json
{
  "text": "पीएम किसान योजना के लिए मैं पात्र हूं?",
  "language": "hi-IN",
  "user_id": "uuid-here",
  "profile": {
    "state": "Maharashtra",
    "occupation": "farmer",
    "income_band": "below_1_lakh",
    "age": 45
  }
}
```

**`POST /ai/chat` Response:**
```json
{
  "text_response": "हाँ, आप PM-KISAN योजना के लिए पात्र हो सकते हैं...",
  "audio_url": "/static/audio/response_abc123.mp3",
  "intent": "scheme_discovery",
  "schemes_referenced": ["PM-KISAN", "Fasal Bima Yojana"],
  "session_id": "session-uuid"
}
```

### Scheme Discovery (`/schemes`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/schemes/` | List all schemes (paginated) | ❌ |
| `GET` | `/schemes/search?q=...` | Semantic search + profile filter | ✅ |
| `GET` | `/schemes/{id}` | Get full scheme details | ❌ |
| `GET` | `/schemes/categories` | List scheme categories | ❌ |

### Admin Analytics (`/admin`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/admin/analytics` | Dashboard metrics (queries, languages, trends) | ✅ Admin |
| `GET` | `/admin/queries` | Paginated query log with resolution status | ✅ Admin |
| `GET` | `/admin/languages` | Language usage distribution | ✅ Admin |
| `GET` | `/admin/failed` | Unresolved queries for knowledge base gaps | ✅ Admin |

### WhatsApp Webhook (`/webhook`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/webhook/whatsapp` | Meta webhook verification |
| `POST` | `/webhook/whatsapp` | Receive & process WhatsApp messages |

---

## 🗺️ Roadmap

### ✅ Completed (v1.0 — Current)

- [x] Voice chat engine with 15+ Indian language support
- [x] AWS Bedrock Nova Pro + Nova Lite dual-model integration
- [x] Profile-based scheme discovery with RAG pipeline
- [x] Legal document OCR + AI summarization
- [x] Admin analytics dashboard (trending queries, language map, failed queries)
- [x] JWT authentication with Supabase
- [x] Persistent multi-turn conversation history
- [x] Vanilla JS frontend hosted on Vercel
- [x] Core RAG vector knowledge base

### 🔄 In Progress (v1.1)

- [ ] WhatsApp Bot — low-latency bot for feature phones (Beta testing)
- [ ] Expanded Scheme Coverage — scaling from 100 to 500+ schemes
- [ ] Improved OCR accuracy for regional language documents

### 🔮 Upcoming (v2.0)

- [ ] **Offline Mode** — Service Worker + cached responses for low-bandwidth areas
- [ ] **Aadhaar Autofill** — Profile population via DigiLocker / Aadhaar verification API
- [ ] **React Native App** — Native mobile application for iOS and Android
- [ ] **Voice Biometrics** — Speaker identification for secure, passwordless login
- [ ] **Grievance Filing** — Direct integration with state government grievance portals
- [ ] **Sarpanch Dashboard** — Village-level admin panel for gram panchayat officials
- [ ] **Multi-Agent System** — Specialized agents per ministry (Agriculture, Education, Health)

---

## 🤝 Contributing

We are **building for a billion voices** — contributions are welcome and deeply valued.

### Areas Needing Help

| Area | Description |
|---|---|
| 🌍 **Localized Datasets** | Scheme data and translations in underrepresented regional languages (Santali, Bodo, Dogri, Kashmiri) |
| 🎙️ **Voice Quality** | Improved TTS prosody and accent naturalness for regional dialects |
| ♿ **Accessibility** | Screen reader support, motor impairment adaptations, low-vision UI |
| 🧪 **Test Coverage** | Unit and integration tests for API routes, AI pipelines, and OCR accuracy |
| 📚 **Scheme Data** | Research and add missing central and state government schemes |
| 🔒 **Security** | Penetration testing, auth hardening, data privacy compliance |

### How to Contribute

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Saarthi-AI-Prototype-.git

# 3. Create a feature branch
git checkout -b feature/your-feature-name

# 4. Make your changes and commit
git add .
git commit -m "feat: add Malayalam TTS support"

# 5. Push and open a Pull Request
git push origin feature/your-feature-name
```

**Commit Convention:** Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `test:` — test coverage
- `chore:` — maintenance

**Pull Request Checklist:**
- [ ] Feature branch from `main`
- [ ] Code follows existing patterns
- [ ] No hardcoded secrets or credentials
- [ ] Tested locally
- [ ] PR description explains the change and why

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

You are free to use, modify, and distribute this software for any purpose, including commercial use, provided the original license notice is included.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer" width="100%"/>

**Built with purpose, for every citizen of India** 🇮🇳

*If Saarthi helped you or inspired your work, please consider giving it a* ⭐

[![Made with ❤️ in India](https://img.shields.io/badge/Made_with_❤️_in-India-FF9933?style=for-the-badge)](https://github.com/ompatilm4-web/Saarthi-AI-Prototype-)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge&logo=github)](https://github.com/ompatilm4-web/Saarthi-AI-Prototype-/pulls)

</div>
