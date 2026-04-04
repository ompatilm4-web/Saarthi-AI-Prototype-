# 🇮🇳 Saarthi AI — Complete Build Guide
> Voice-First Digital India Assistant | Full Feature Roadmap & Implementation Guide

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [22+ Indian Languages — Voice, Slow Mode & Replay](#3-22-indian-languages--voice-slow-mode--replay)
4. [All Schemes — Central & State](#4-all-schemes--central--state)
5. [RAG Pipeline — Document Scanning, Notices & AutoForm](#5-rag-pipeline--document-scanning-notices--autoform)
6. [Authentication — Full Auth System](#6-authentication--full-auth-system)
7. [Government Schemes Database](#7-government-schemes-database)
8. [Legal Advice Module](#8-legal-advice-module)
9. [Educational Services — Scholarships & Exam Forms](#9-educational-services--scholarships--exam-forms)
10. [Mobile Responsive Design](#10-mobile-responsive-design)
11. [Folder Structure](#11-folder-structure)
12. [Deployment Checklist](#12-deployment-checklist)

---

## 1. Project Overview

**Saarthi AI** is a voice-first, multilingual AI assistant that helps Indian citizens access government schemes, legal guidance, educational opportunities, and official documents — all in their mother tongue.

### Core Principles
- **Voice-first** — No typing required; speak naturally
- **Language-inclusive** — All 22 scheduled Indian languages
- **Offline-tolerant** — Works on low-bandwidth connections
- **Mobile-first** — Designed for Android feature phones upward
- **Accessible** — No literacy required for core functions

---

## 2. Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | HTML5, CSS3, Vanilla JS | UI, voice interface |
| Voice | Web Speech API (STT) + Web Speech Synthesis API (TTS) | Built-in browser voice, no external API |
| AI / LLM | Amazon Bedrock (Nova Lite & Nova Pro) | Intent detection, scheme analysis, guidance |
| RAG | LangChain + pgvector (via Supabase) | Document scanning, notice parsing |
| OCR | Tesseract.js / AWS Textract | Scan uploaded documents |
| Backend | Python FastAPI | API server, auth, DB bridge |
| Database | Supabase (PostgreSQL) | User data, scheme data, vector embeddings |
| Auth | Supabase Auth | OTP, mobile number login |
| Storage | Supabase Storage / AWS S3 | Document uploads |
| Hosting | Vercel (frontend) + AWS / Railway (backend) | Deployment |

---

## 3. 22+ Indian Languages — Voice, Slow Mode & Replay

### 3.1 Complete Language List

All 22 languages from the 8th Schedule of the Indian Constitution plus English:

```javascript
// JS/languages.js
const INDIAN_LANGUAGES = [
  { code: "hi-IN",  label: "हिंदी",          name: "Hindi"},
  { code: "en-IN",  label: "English",         name: "English"},
  { code: "bn-IN",  label: "বাংলা",           name: "Bengali"},
  { code: "te-IN",  label: "తెలుగు",          name: "Telugu"},
  { code: "mr-IN",  label: "मराठी",           name: "Marathi"},
  { code: "ta-IN",  label: "தமிழ்",           name: "Tamil"},
  { code: "gu-IN",  label: "ગુજરાતી",         name: "Gujarati"},
  { code: "kn-IN",  label: "ಕನ್ನಡ",           name: "Kannada"},
  { code: "ml-IN",  label: "മലയാളം",          name: "Malayalam"},
  { code: "pa-IN",  label: "ਪੰਜਾਬੀ",          name: "Punjabi"},
  { code: "or-IN",  label: "ଓଡ଼ିଆ",           name: "Odia"},
  { code: "as-IN",  label: "অসমীয়া",         name: "Assamese"},
  { code: "ur-IN",  label: "اردو",            name: "Urdu"},
  { code: "mai-IN", label: "मैथिली",          name: "Maithili"},
  { code: "kok-IN", label: "कोंकणी",          name: "Konkani"},
  { code: "doi-IN", label: "डोगरी",           name: "Dogri"},
  { code: "ks-IN",  label: "کٲشُر",           name: "Kashmiri"},
  { code: "sd-IN",  label: "سنڌي",            name: "Sindhi"},
  { code: "ne-IN",  label: "नेपाली",          name: "Nepali"},
  { code: "sa-IN",  label: "संस्कृतम्",       name: "Sanskrit"},
  { code: "mni-IN", label: "ꯃꯩꯇꯩꯂꯣꯟ",        name: "Manipuri"},
  { code: "sat-IN", label: "ᱥᱟᱱᱛᱟᱲᱤ",        name: "Santali"},
  { code: "brx-IN", label: "बर'",             name: "Bodo"}
];
```

### 3.2 Voice Engine — Speech to Text (STT)

```javascript
// JS/voice.js
// Voice input powered entirely by the browser's built-in Web Speech API
// No external STT service required — works offline for supported languages

class SaarthiVoice {
  constructor(langCode) {
    this.langCode = langCode;
    this.recognition = null;
  }

  startListening(onResult, onError) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      onError("Voice input not supported in this browser. Please try Chrome or Edge.");
      return;
    }
    this.recognition = new SpeechRecognition();
    this.recognition.lang = this.langCode;
    this.recognition.interimResults = true;
    this.recognition.continuous = false;
    this.recognition.onresult = (e) => {
      const transcript = Array.from(e.results).map(r => r[0].transcript).join('');
      onResult(transcript, e.results[e.results.length - 1].isFinal);
    };
    this.recognition.onerror = onError;
    this.recognition.start();
  }

  stopListening() {
    this.recognition?.stop();
  }
}
```

### 3.3 Text to Speech (TTS) — Clear Voice + Slow Mode + Replay

```javascript
// JS/tts.js

class SaarthiTTS {
  constructor() {
    this.currentUtterance = null;
    this.lastText = "";
    this.lastLang = "";
    this.slowRate = 0.6;   // Slow voice rate
    this.normalRate = 1.0;
  }

  speak(text, langCode, slow = false) {
    this.lastText = text;
    this.lastLang = langCode;
    window.speechSynthesis.cancel(); // Stop any ongoing speech

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = slow ? this.slowRate : this.normalRate;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Pick best available voice for the language
    const voices = window.speechSynthesis.getVoices();
    const match = voices.find(v => v.lang.startsWith(langCode.split("-")[0]));
    if (match) utterance.voice = match;

    this.currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
    return utterance;
  }

  // Replay last spoken message
  replay() {
    if (this.lastText) this.speak(this.lastText, this.lastLang);
  }

  // Replay in slow mode
  replaySlow() {
    if (this.lastText) this.speak(this.lastText, this.lastLang, true);
  }

  stop() {
    window.speechSynthesis.cancel();
  }
}

// Global TTS instance
window.saarthiTTS = new SaarthiTTS();
```

### 3.4 Chat Message UI — Add Replay & Slow Buttons

```html
<!-- Add after every AI message in chat -->
<div class="message assistant-message" data-text="..." data-lang="hi-IN">
  <p class="msg-text"><!-- AI response here --></p>
  <div class="msg-actions">
    <button class="tts-btn" onclick="saarthiTTS.speak(this.closest('[data-text]').dataset.text, this.closest('[data-lang]').dataset.lang)">
      🔊 सुनें
    </button>
    <button class="tts-slow-btn" onclick="saarthiTTS.speak(this.closest('[data-text]').dataset.text, this.closest('[data-lang]').dataset.lang, true)">
      🐢 धीरे सुनें
    </button>
    <button class="tts-replay-btn" onclick="saarthiTTS.replay()">
      🔁 दोबारा
    </button>
  </div>
</div>
```

```css
/* CSS/tts.css */
.msg-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}
.tts-btn, .tts-slow-btn, .tts-replay-btn {
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
  color: inherit;
  transition: background 0.2s;
}
.tts-btn:hover, .tts-slow-btn:hover, .tts-replay-btn:hover {
  background: rgba(255,255,255,0.3);
}
```

---

## 4. All Schemes — Central & State

### 4.1 Schemes Database Structure

```sql
-- Supabase: Enable pgvector extension first
CREATE EXTENSION IF NOT EXISTS vector;

-- schemes table
CREATE TABLE schemes (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_en       TEXT NOT NULL UNIQUE,
  name_hi       TEXT,
  description   TEXT,
  category      TEXT,        -- Agriculture, Health, Education, Women, Housing, etc.
  level         TEXT,        -- 'central' or 'state'
  state         TEXT,        -- NULL for central; e.g. 'Maharashtra', 'Bihar'
  ministry      TEXT,
  eligibility   JSONB,       -- { "age_min": 18, "income_max": 200000, "gender": "any" }
  documents     JSONB,       -- ["Aadhaar", "Ration Card", ...]
  apply_url     TEXT,
  deadline      DATE,
  benefit       TEXT,        -- "₹6000/year", "Free insurance", etc.
  tags          TEXT[],
  created_at    TIMESTAMP DEFAULT NOW()
);

-- document_chunks table for RAG (pgvector)
CREATE TABLE document_chunks (
  id            TEXT PRIMARY KEY,
  user_id       UUID REFERENCES auth.users(id),
  doc_id        TEXT,
  content       TEXT,
  embedding     VECTOR(1536),
  created_at    TIMESTAMP DEFAULT NOW()
);

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding VECTOR(1536),
  match_count INT,
  user_id_filter UUID
) RETURNS TABLE (content TEXT, similarity FLOAT) AS $$
  SELECT content, 1 - (embedding <=> query_embedding) AS similarity
  FROM document_chunks
  WHERE user_id = user_id_filter
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$ LANGUAGE SQL;
```

### 4.2 Central Government Schemes (Pre-load)

| Scheme | Category | Benefit |
|---|---|---|
| PM-KISAN | Agriculture | ₹6,000/year |
| Ayushman Bharat (PM-JAY) | Health | ₹5 lakh insurance |
| PM Awas Yojana (Urban) | Housing | Home subsidy |
| PM Awas Yojana (Rural) | Housing | ₹1.2–1.3 lakh |
| PM Ujjwala Yojana | Women / LPG | Free gas connection |
| Beti Bachao Beti Padhao | Women | Financial + awareness |
| PM Vishwakarma | Artisans | ₹3 lakh credit |
| PM Mudra Yojana | Business | ₹10 lakh loan |
| Sukanya Samriddhi Yojana | Girl Child | Savings scheme |
| National Scholarship Portal | Education | Multiple scholarships |
| PM Jan Dhan Yojana | Banking | Free bank account |
| Atal Pension Yojana | Pension | ₹1000–₹5000/month |
| PM Jeevan Jyoti Bima | Insurance | ₹2 lakh life cover |
| PM Suraksha Bima | Insurance | ₹2 lakh accident |
| Skill India / PMKVY | Employment | Free skill training |
| National Food Security Act | Food | Subsidised ration |
| MGNREGA | Employment | 100 days work |
| Stand-Up India | SC/ST/Women | ₹10 lakh–₹1 cr loan |
| Startup India | Entrepreneurship | Tax benefits |
| Digital India | Digital Access | Infrastructure |

### 4.3 State Schemes (Example — Maharashtra)

```javascript
// data/state_schemes/maharashtra.js
const maharashtraSchemes = [
  {
    name_en: "Mahatma Phule Jan Arogya Yojana",
    category: "Health",
    benefit: "₹1.5 lakh cashless treatment",
    eligibility: { income_max: 100000 }
  },
  {
    name_en: "Ramai Awas Gharkul Yojana",
    category: "Housing",
    benefit: "House for SC/NT/VJ communities"
  },
  {
    name_en: "Shasan Aplya Dari",
    category: "Services",
    benefit: "Mobile government services"
  }
  // Add all 29 states + UTs similarly
];
```

### 4.4 Schemes Filter UI

```html
<!-- schemes.html — filter bar -->
<div class="scheme-filters">
  <select id="filterLevel">
    <option value="">All (Central + State)</option>
    <option value="central">Central Government</option>
    <option value="state">State Government</option>
  </select>

  <select id="filterState">
    <option value="">All States</option>
    <option value="maharashtra">Maharashtra</option>
    <option value="uttar-pradesh">Uttar Pradesh</option>
    <!-- ... all 28 states + 8 UTs ... -->
  </select>

  <select id="filterCategory">
    <option value="">All Categories</option>
    <option value="agriculture">Agriculture</option>
    <option value="health">Health</option>
    <option value="education">Education</option>
    <option value="housing">Housing</option>
    <option value="women">Women & Child</option>
    <option value="employment">Employment</option>
    <option value="business">Business / MSME</option>
    <option value="pension">Pension / Insurance</option>
  </select>

  <input type="text" id="schemeSearch" placeholder="Search schemes...">
</div>
```

---

## 5. RAG Pipeline — Document Scanning, Notices & AutoForm

### 5.1 Architecture Overview

```
User uploads document (PDF/Image)
        ↓
  OCR (Tesseract / AWS Textract)
        ↓
  Text Extraction + Chunking
        ↓
  Embedding (Amazon Bedrock Titan Embeddings)
        ↓
  Vector Store (Supabase pgvector)
        ↓
  User Query → Semantic Search
        ↓
  Context → Amazon Bedrock Nova Pro
        ↓
  Structured Response + AutoForm Fill
```

### 5.2 Backend RAG Setup

```python
# backend/rag/pipeline.py
import boto3
import json
from supabase import create_client
from PIL import Image
import pytesseract

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

# Step 1: OCR — extract text from uploaded document
def extract_text_from_document(file_path: str, lang: str = "hin") -> str:
    image = Image.open(file_path)
    return pytesseract.image_to_string(image, lang=lang)

# Step 2: Chunk the extracted text
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

# Step 3: Generate embeddings via Amazon Bedrock Titan
def get_embedding(text: str) -> list[float]:
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text})
    )
    return json.loads(response["body"].read())["embedding"]

# Step 4: Store chunks in Supabase pgvector
def index_document(user_id: str, doc_id: str, text: str):
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        supabase.table("document_chunks").insert({
            "id": f"{doc_id}_chunk_{i}",
            "user_id": user_id,
            "doc_id": doc_id,
            "content": chunk,
            "embedding": embedding
        }).execute()

# Step 5: Semantic search via Supabase pgvector
def query_rag(user_id: str, user_query: str) -> str:
    query_embedding = get_embedding(user_query)
    result = supabase.rpc("match_documents", {
        "query_embedding": query_embedding,
        "match_count": 5,
        "user_id_filter": user_id
    }).execute()
    return "\n\n".join([row["content"] for row in result.data])

# Step 6: Generate answer using Amazon Bedrock Nova Pro
def generate_answer(context: str, user_query: str, lang: str = "hi") -> str:
    prompt = f"Context from user's documents:\n{context}\n\nUser question (answer in {lang}): {user_query}"
    response = bedrock.invoke_model(
        modelId="amazon.nova-pro-v1:0",
        body=json.dumps({
            "messages": [{"role": "user", "content": [{"text": prompt}]}]
        })
    )
    return json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]
```

### 5.3 AutoForm Fill — Extract Fields from Documents

```python
# backend/rag/autoform.py
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

def extract_form_fields(document_text: str) -> dict:
    prompt = f"""Extract the following fields from this document and return as JSON only:
    name, father_name, mother_name, date_of_birth, aadhaar_number, mobile,
    address, pincode, state, district, income, caste, bank_account, ifsc.
    
    Document text:
    {document_text}
    
    Return only valid JSON. Use null for missing fields."""

    response = bedrock.invoke_model(
        modelId="amazon.nova-pro-v1:0",
        body=json.dumps({
            "messages": [{"role": "user", "content": [{"text": prompt}]}]
        })
    )
    result_text = json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]
    return json.loads(result_text)
```

### 5.4 Document Upload UI

```html
<!-- Add to schemes application flow -->
<div class="doc-upload-section">
  <h3>📄 Upload Your Documents</h3>
  <p>Upload Aadhaar, Income Certificate, or any notice — we'll read it for you</p>

  <label class="upload-zone" id="uploadZone">
    <input type="file" id="docUpload" accept=".pdf,.jpg,.jpeg,.png" multiple hidden>
    <div class="upload-content">
      <span class="upload-icon">📤</span>
      <span>Tap to upload or take photo</span>
      <span class="upload-sub">PDF, JPG, PNG supported</span>
    </div>
  </label>

  <div id="docPreview" class="doc-preview-list"></div>

  <button class="btn-primary" id="autoFillBtn" style="display:none;">
    ✨ Auto-fill Form from Documents
  </button>
</div>
```

---

## 6. Authentication — Full Auth System

### 6.1 Auth Flow

```
User opens app
    ↓
Choose Login Method:
  ├─ 📱 Mobile OTP (most common)
  ├─ 🆔 Aadhaar OTP (for verified access)
  └─ 📧 Email + Password
    ↓
Token stored in localStorage ('saarthi_token')
    ↓
Profile created in DB (name, state, preferred language)
    ↓
Access to: Dashboard, Scheme Applications, Documents
```

### 6.2 Login Page (login.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Saarthi AI — Login</title>
  <link rel="stylesheet" href="CSS/main.css">
  <link rel="stylesheet" href="CSS/auth.css">
</head>
<body>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-logo">Saarthi AI</div>
      <h2>Login to Continue</h2>

      <!-- Tab: Mobile OTP / Email -->
      <div class="auth-tabs">
        <button class="auth-tab active" data-tab="mobile">📱 Mobile OTP</button>
        <button class="auth-tab" data-tab="email">📧 Email</button>
      </div>

      <!-- Mobile OTP -->
      <div class="auth-form" id="mobileForm">
        <input type="tel" id="mobileNum" placeholder="Enter 10-digit mobile number" maxlength="10">
        <button class="btn-primary" id="sendOtpBtn">Send OTP</button>
        <div id="otpSection" style="display:none;">
          <input type="text" id="otpInput" placeholder="Enter 6-digit OTP" maxlength="6">
          <button class="btn-primary" id="verifyOtpBtn">Verify & Login</button>
        </div>
      </div>

      <!-- Email login -->
      <div class="auth-form" id="emailForm" style="display:none;">
        <input type="email" id="emailInput" placeholder="Email address">
        <input type="password" id="passwordInput" placeholder="Password">
        <button class="btn-primary" id="emailLoginBtn">Login</button>
        <a href="register.html" class="auth-link">New user? Register here</a>
      </div>
    </div>
  </div>
  <script src="JS/auth.js"></script>
</body>
</html>
```

### 6.3 Auth JS

```javascript
// JS/auth.js
const AUTH_API = "/api/auth";

async function sendOTP(mobile) {
  const res = await fetch(`${AUTH_API}/send-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mobile })
  });
  return res.json();
}

async function verifyOTP(mobile, otp) {
  const res = await fetch(`${AUTH_API}/verify-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mobile, otp })
  });
  const data = await res.json();
  if (data.token) {
    localStorage.setItem("saarthi_token", data.token);
    localStorage.setItem("saarthi_user", JSON.stringify(data.user));
    window.location.href = "dashboard.html";
  }
  return data;
}

function logout() {
  localStorage.removeItem("saarthi_token");
  localStorage.removeItem("saarthi_user");
  window.location.href = "login.html";
}

function isLoggedIn() {
  return !!localStorage.getItem("saarthi_token");
}

function getUser() {
  return JSON.parse(localStorage.getItem("saarthi_user") || "{}");
}
```

### 6.4 Backend Auth Routes

```python
# backend/routes/auth.py (FastAPI + Supabase Auth)
from fastapi import APIRouter, HTTPException
from supabase import create_client
from pydantic import BaseModel
import random, time

router = APIRouter()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# In-memory OTP store — persists per FastAPI process lifetime
# For multi-instance deploys, move this to a Supabase table with an expires_at column
otp_store: dict = {}

class OTPRequest(BaseModel):
    mobile: str

class OTPVerify(BaseModel):
    mobile: str
    otp: str

# Send OTP
@router.post("/send-otp")
async def send_otp(req: OTPRequest):
    otp = str(random.randint(100000, 999999))
    otp_store[req.mobile] = {"otp": otp, "expires": time.time() + 300}
    # Deliver OTP via AWS SNS (Amazon Simple Notification Service)
    # sns_client.publish(PhoneNumber=f"+91{req.mobile}", Message=f"Your Saarthi OTP: {otp}")
    print(f"[DEV] OTP for {req.mobile}: {otp}")
    return {"success": True}

# Verify OTP
@router.post("/verify-otp")
async def verify_otp(req: OTPVerify):
    stored = otp_store.get(req.mobile)
    if not stored or stored["otp"] != req.otp or time.time() > stored["expires"]:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    del otp_store[req.mobile]

    # Upsert user in Supabase
    result = supabase.table("users").upsert(
        {"mobile": req.mobile}, on_conflict="mobile"
    ).execute()
    user = result.data[0]

    # Use Supabase JWT or generate your own
    token = supabase.auth.sign_in_with_otp({"phone": f"+91{req.mobile}"})
    return {"token": token.session.access_token, "user": user}
```

---

## 7. Government Schemes Database

### 7.1 Seeding the Database

```python
# backend/seed/schemes.py — run once to populate Supabase
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

central_schemes = [
  {
    "name_en": "PM-KISAN Samman Nidhi",
    "name_hi": "पीएम किसान सम्मान निधि",
    "category": "Agriculture",
    "level": "central",
    "ministry": "Ministry of Agriculture",
    "benefit": "₹6,000 per year in 3 installments",
    "eligibility": {"occupation": "farmer", "land": "any"},
    "documents": ["Aadhaar", "Bank Passbook", "Land Records"],
    "apply_url": "https://pmkisan.gov.in",
    "tags": ["farmer", "income support", "kisaan"]
  },
  {
    "name_en": "Ayushman Bharat PM-JAY",
    "name_hi": "आयुष्मान भारत पीएम-जेएवाई",
    "category": "Health",
    "level": "central",
    "ministry": "Ministry of Health",
    "benefit": "₹5 lakh health insurance per family per year",
    "eligibility": {"income_max": 200000, "secc_listed": True},
    "documents": ["Aadhaar", "Ration Card", "SECC document"],
    "apply_url": "https://pmjay.gov.in",
    "tags": ["health", "insurance", "hospital", "treatment"]
  },
  # ... add all 50+ central schemes
]

supabase.table("schemes").upsert(central_schemes, on_conflict="name_en").execute()
print("✅ Schemes seeded successfully")
```

### 7.2 Scheme Chat Integration

```javascript
// JS/api.js — scheme-aware AI query via FastAPI backend
async function askSaarthi(userMessage, lang, userProfile) {
  const response = await fetch("/api/ai/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("saarthi_token")}`
    },
    body: JSON.stringify({
      message: userMessage,
      lang: lang,
      profile: userProfile
    })
  });
  const data = await response.json();
  return data.reply;
}
```

```python
# backend/routes/ai.py — FastAPI route calling Amazon Bedrock
import boto3, json
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

class ChatRequest(BaseModel):
    message: str
    lang: str
    profile: dict

@router.post("/chat")
async def chat(req: ChatRequest):
    system_prompt = f"""You are Saarthi AI, a helpful assistant for Indian government schemes.
    Always respond in {req.lang} language.
    User profile: State={req.profile.get('state')}, Income={req.profile.get('income')}, Age={req.profile.get('age')}
    
    When asked about schemes:
    1. Identify relevant schemes based on profile
    2. Explain eligibility in simple language
    3. List required documents
    4. Provide application steps
    5. Give official website/helpline
    
    Keep responses clear, short, and actionable."""

    response = bedrock.invoke_model(
        modelId="amazon.nova-pro-v1:0",
        body=json.dumps({
            "system": [{"text": system_prompt}],
            "messages": [{"role": "user", "content": [{"text": req.message}]}]
        })
    )
    reply = json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]
    return {"reply": reply}
```

---

## 8. Legal Advice Module

### 8.1 Legal Flow

```
User describes legal problem (voice/text)
        ↓
  STEP 1: ANALYZE
  AI identifies: issue type, applicable law, jurisdiction
        ↓
  STEP 2: EXPLAIN
  Plain-language explanation in user's language
        ↓
  STEP 3: SOLUTION
  Recommended action: file RTI / complaint / FIR / consumer forum / legal aid
        ↓
  STEP 4: RESOURCES
  Nearest legal aid center, helpline numbers, draft complaint
```

### 8.2 Legal Module UI

```html
<!-- legal.html -->
<section class="legal-section">
  <div class="legal-header">
    <h2>⚖️ Legal Help</h2>
    <p>Describe your problem. We will analyze, explain, and guide you — in your language.</p>
  </div>

  <!-- Step indicators -->
  <div class="legal-steps">
    <div class="step active" id="step-analyze">🔍 Analyze</div>
    <div class="step" id="step-explain">📖 Explain</div>
    <div class="step" id="step-solve">✅ Solution</div>
  </div>

  <!-- Input -->
  <div class="legal-input-area">
    <textarea id="legalQuery" rows="4"
      placeholder="Describe your problem... e.g. 'My employer has not paid salary for 3 months'"></textarea>
    <div class="legal-input-actions">
      <button class="mic-btn" id="legalMicBtn">🎤 Speak</button>
      <button class="btn-primary" id="analyzeLegalBtn">Analyze My Problem →</button>
    </div>
  </div>

  <!-- Results -->
  <div class="legal-results" id="legalResults" style="display:none;">
    <div class="legal-card analysis-card">
      <h4>🔍 Your Issue</h4>
      <p id="legalIssueText"></p>
    </div>
    <div class="legal-card explanation-card">
      <h4>📖 Your Rights</h4>
      <p id="legalExplanationText"></p>
    </div>
    <div class="legal-card solution-card">
      <h4>✅ What You Should Do</h4>
      <p id="legalSolutionText"></p>
      <div class="legal-actions-btns">
        <button class="btn-secondary" id="draftComplaintBtn">📝 Draft Complaint</button>
        <button class="btn-secondary" id="findLegalAidBtn">🏛️ Find Legal Aid Near Me</button>
        <button class="btn-secondary" id="callHelplineBtn">📞 Call Helpline</button>
      </div>
    </div>
  </div>
</section>
```

### 8.3 Legal AI Logic

```javascript
// JS/legal.js — calls FastAPI backend which uses Amazon Bedrock
async function analyzeLegalIssue(userQuery, lang) {
  const response = await fetch("/api/ai/legal", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("saarthi_token")}`
    },
    body: JSON.stringify({ query: userQuery, lang })
  });
  return response.json();
}
```

```python
# backend/routes/legal.py — FastAPI + Amazon Bedrock Nova Pro
import boto3, json
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

class LegalRequest(BaseModel):
    query: str
    lang: str

@router.post("/legal")
async def analyze_legal(req: LegalRequest):
    system_prompt = f"""You are a legal advisor for Indian citizens. Respond in {req.lang} language.
    
    Analyze the user's legal problem and return a JSON with:
    {{
      "issue_type": "Labour Law / Consumer Rights / Property / Criminal / Family / RTI / etc.",
      "applicable_law": "Name of relevant Act",
      "jurisdiction": "Labour Court / Consumer Forum / High Court / Police / etc.",
      "explanation": "Simple explanation of their rights (2-3 sentences)",
      "immediate_steps": ["Step 1", "Step 2", "Step 3"],
      "helplines": [{{"name": "National Legal Aid", "number": "15100"}}],
      "can_file_rti": true,
      "urgency": "low/medium/high"
    }}
    
    Use simple language. Always recommend consulting a lawyer for complex matters."""

    response = bedrock.invoke_model(
        modelId="amazon.nova-pro-v1:0",
        body=json.dumps({
            "system": [{"text": system_prompt}],
            "messages": [{"role": "user", "content": [{"text": req.query}]}]
        })
    )
    result = json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]
    return json.loads(result)
```

### 8.4 Key Legal Categories to Support

| Category | Acts Covered | Helpline |
|---|---|---|
| Labour Rights | Industrial Disputes Act, Payment of Wages | 1800-11-1363 |
| Consumer Rights | Consumer Protection Act 2019 | 1800-11-4000 |
| Property Disputes | Transfer of Property Act, RERA | State RERA helpline |
| Family Law | Hindu Marriage Act, Domestic Violence Act | 181 (Women Helpline) |
| RTI Filing | Right to Information Act 2005 | rtionline.gov.in |
| Criminal Matters | IPC / BNS, CrPC / BNSS | 112 |
| Land Rights | Land Acquisition Act | Tehsildar office |
| Legal Aid | NALSA Act | 15100 |

---

## 9. Educational Services — Scholarships & Exam Forms

### 9.1 Scholarship Finder

```javascript
// JS/education.js
const scholarships = [
  {
    name: "National Scholarship Portal (NSP)",
    provider: "Central Government",
    categories: ["Pre-Matric", "Post-Matric", "Merit-cum-Means"],
    eligibility: { income_max: 250000, type: "student" },
    amount: "₹500–₹20,000/year",
    deadline: "October 31",
    apply_url: "https://scholarships.gov.in",
    documents: ["Aadhaar", "Bank Account", "Income Certificate", "Marksheet", "Caste Certificate"]
  },
  {
    name: "PM Yasasvi Scholarship",
    provider: "Central Government",
    categories: ["OBC", "EBC", "DNT students"],
    eligibility: { income_max: 250000, class: ["9", "11"] },
    amount: "₹75,000–₹1,25,000/year",
    apply_url: "https://yet.nta.ac.in"
  },
  {
    name: "Begum Hazrat Mahal National Scholarship",
    provider: "Maulana Azad Education Foundation",
    categories: ["Minority Girls"],
    eligibility: { gender: "female", minority: true, class: ["9", "10", "11", "12"] },
    amount: "₹5,000–₹6,000/year"
  },
  {
    name: "Inspire Scholarship",
    provider: "DST, Central Government",
    categories: ["Science Students"],
    amount: "₹80,000/year",
    apply_url: "https://online-inspire.gov.in"
  }
  // Add 50+ scholarships
];
```

### 9.2 Exam Forms Tracker

```html
<!-- education.html — Exam Calendar -->
<section class="exam-section">
  <h2>📝 Upcoming Exam Forms</h2>

  <div class="exam-filters">
    <button class="exam-filter active" data-type="all">All</button>
    <button class="exam-filter" data-type="board">Board Exams</button>
    <button class="exam-filter" data-type="entrance">Entrance Tests</button>
    <button class="exam-filter" data-type="govt-jobs">Govt Jobs</button>
    <button class="exam-filter" data-type="scholarship">Scholarship</button>
  </div>

  <div class="exam-grid" id="examGrid">
    <!-- Dynamically filled from exams.js -->
  </div>
</section>
```

```javascript
// data/exams.js
const upcomingExams = [
  { name: "NEET UG 2026",        type: "entrance",    deadline: "2026-03-31", exam_date: "2026-05-04", url: "https://neet.nta.nic.in" },
  { name: "JEE Main 2026",       type: "entrance",    deadline: "2026-03-15", exam_date: "2026-04-01", url: "https://jeemain.nta.nic.in" },
  { name: "NSP Scholarship",     type: "scholarship", deadline: "2026-10-31", url: "https://scholarships.gov.in" },
  { name: "SSC CGL 2026",        type: "govt-jobs",   deadline: "2026-04-20", url: "https://ssc.nic.in" },
  { name: "UPSC CSE 2026",       type: "govt-jobs",   deadline: "2026-04-02", url: "https://upsc.gov.in" },
  { name: "IBPS PO 2026",        type: "govt-jobs",   deadline: "2026-08-01", url: "https://ibps.in" },
  { name: "CBSE Board 10th/12th",type: "board",       deadline: "N/A",        exam_date: "2026-02-15", url: "https://cbse.gov.in" },
  { name: "Maharashtra HSC",     type: "board",       deadline: "N/A",        exam_date: "2026-02-21", url: "https://mahahsscboard.in" },
];
```

### 9.3 AI Scholarship Matcher

```javascript
// When user asks "Which scholarships am I eligible for?"
async function findMatchingScholarships(userProfile) {
  const systemPrompt = `
    Match the user to relevant Indian scholarships based on their profile.
    Return the top 5 most relevant scholarships with eligibility match score.
    Respond in ${userProfile.lang} language.
    User profile: ${JSON.stringify(userProfile)}
    Available scholarships: ${JSON.stringify(scholarships)}
  `;
  const response = await fetch("/api/ai/scholarships", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("saarthi_token")}`
    },
    body: JSON.stringify({ profile: userProfile })
  });
  return (await response.json()).matches;
}
```

---

## 10. Mobile Responsive Design

### 10.1 CSS Mobile Breakpoints

```css
/* CSS/responsive.css */

/* Base: Mobile First */
* { box-sizing: border-box; }

body {
  font-size: 16px;
  overflow-x: hidden;
}

.container {
  width: 100%;
  padding: 0 16px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Navigation — Mobile */
@media (max-width: 768px) {
  .nav-links {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100vh;
    background: var(--bg-dark);
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 32px;
    z-index: 999;
  }
  .nav-links.open { display: flex; }

  .hamburger {
    display: flex;
    flex-direction: column;
    gap: 5px;
    cursor: pointer;
  }
  .hamburger span {
    width: 24px; height: 2px;
    background: white;
    transition: all 0.3s;
  }
}

/* Hero Section */
@media (max-width: 768px) {
  .hero { padding: 80px 16px 40px; }
  .hero h1 { font-size: 28px; line-height: 1.3; }
  .hero p { font-size: 15px; }
  .mic-circle { width: 80px; height: 80px; }
  .mic-button-large { font-size: 32px; }
}

/* Schemes Grid */
@media (max-width: 768px) {
  .schemes-grid { grid-template-columns: 1fr; gap: 16px; }
  .category-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
}

/* Chat Interface */
@media (max-width: 768px) {
  .chat-only-view { padding: 0; }
  .lang-dropdown {
    width: 100vw;
    left: 0;
    right: 0;
    border-radius: 16px 16px 0 0;
    position: fixed;
    bottom: 0;
    max-height: 60vh;
    overflow-y: auto;
  }
  .input-container {
    padding: 8px 12px;
    padding-bottom: env(safe-area-inset-bottom); /* iPhone notch */
  }
  .text-input { font-size: 16px; } /* Prevents iOS zoom on focus */
}

/* Language Tags */
@media (max-width: 768px) {
  .language-tags { gap: 8px; }
  .language-tag {
    font-size: 13px;
    padding: 6px 12px;
  }
}

/* Legal & Education Sections */
@media (max-width: 768px) {
  .legal-results { flex-direction: column; }
  .legal-card { width: 100%; }
  .exam-grid { grid-template-columns: 1fr; }
}

/* Feature Grid */
@media (max-width: 768px) {
  .feature-grid { grid-template-columns: 1fr; }
}

/* Touch targets — minimum 44px for accessibility */
button, a, input[type="button"] {
  min-height: 44px;
  min-width: 44px;
}

/* Sticky bottom action bar on mobile */
.mobile-action-bar {
  display: none;
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: var(--bg-card);
  border-top: 1px solid rgba(255,255,255,0.1);
  padding: 12px 16px;
  padding-bottom: env(safe-area-inset-bottom);
  gap: 12px;
  z-index: 100;
}
@media (max-width: 768px) {
  .mobile-action-bar { display: flex; }
  body { padding-bottom: 70px; }
}
```

### 10.2 Add Hamburger Menu to index.html nav

```html
<!-- Add inside <nav> after logo -->
<button class="hamburger" id="hamburger" aria-label="Menu">
  <span></span><span></span><span></span>
</button>
```

```javascript
// JS/mobile.js
document.getElementById("hamburger")?.addEventListener("click", () => {
  document.querySelector(".nav-links")?.classList.toggle("open");
});

// Close menu on link click
document.querySelectorAll(".nav-links a").forEach(link => {
  link.addEventListener("click", () => {
    document.querySelector(".nav-links")?.classList.remove("open");
  });
});
```

---

## 11. Folder Structure

```
saarthi-ai/
├── index.html               ← Main landing page
├── login.html               ← Login / OTP page
├── register.html            ← New user registration
├── dashboard.html           ← User dashboard
├── schemes.html             ← All schemes browser
├── legal.html               ← Legal advice module
├── education.html           ← Scholarships & exams
├── profile.html             ← User profile
│
├── CSS/
│   ├── main.css             ← Global styles
│   ├── auth.css             ← Login/register styles
│   ├── responsive.css       ← Mobile breakpoints
│   ├── tts.css              ← Voice button styles
│   └── legal.css            ← Legal module styles
│
├── JS/
│   ├── main.js              ← App initialization
│   ├── api.js               ← FastAPI backend calls
│   ├── language.js          ← i18n translations
│   ├── languages.js         ← All 22 language configs
│   ├── voice.js             ← STT (Speech to Text)
│   ├── tts.js               ← TTS (Text to Speech)
│   ├── auth.js              ← Login / token management
│   ├── schemes.js           ← Schemes filter & display
│   ├── legal.js             ← Legal advice logic
│   ├── education.js         ← Scholarship matcher
│   └── mobile.js            ← Hamburger, PWA helpers
│
├── data/
│   ├── central_schemes.js   ← All central gov schemes
│   ├── state_schemes/       ← One file per state
│   │   ├── maharashtra.js
│   │   ├── uttar_pradesh.js
│   │   └── ...
│   ├── exams.js             ← Upcoming exam dates
│   └── scholarships.js      ← Scholarship database
│
├── backend/                 ← Python FastAPI backend
│   ├── main.py              ← FastAPI app entry point
│   ├── requirements.txt     ← Python dependencies
│   ├── .env                 ← Environment variables
│   ├── core/
│   │   ├── config.py        ← Settings & env loader
│   │   └── supabase.py      ← Supabase client setup
│   ├── routes/
│   │   ├── auth.py          ← OTP login endpoints
│   │   ├── ai.py            ← Bedrock chat & intent
│   │   ├── schemes.py       ← Supabase scheme queries
│   │   └── legal.py         ← Legal analysis via Bedrock
│   ├── rag/
│   │   ├── pipeline.py      ← OCR + chunking + pgvector
│   │   └── autoform.py      ← Form field extraction
│   ├── seed/
│   │   └── schemes.py       ← Seed Supabase with schemes
│   └── middleware/
│       └── auth.py          ← Supabase JWT verification
│
└── manifest.json            ← PWA manifest for "Add to Home Screen"
```

---

## 12. Deployment Checklist

### Environment Variables (.env)

```env
# Amazon Bedrock (AWS)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
BEDROCK_INTENT_MODEL=amazon.nova-lite-v1:0
BEDROCK_SCHEME_MODEL=amazon.nova-pro-v1:0
BEDROCK_EMBED_MODEL=amazon.titan-embed-text-v2:0

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key


# AWS SNS (OTP SMS delivery — uses same AWS credentials above)
# No extra keys needed — SNS is accessed via boto3 with AWS_ACCESS_KEY_ID above

# FastAPI
PORT=8080
JWT_SECRET=your-long-secret-here
```

### Pre-launch Checklist

- [ ] All 22 language buttons tested in chat dropdown
- [ ] TTS working for Hindi, Tamil, Bengali at minimum
- [ ] OTP login working end-to-end
- [ ] Schemes database seeded (central + state)
- [ ] RAG pipeline tested with Aadhaar/income cert upload
- [ ] Legal module tested with 5+ scenarios
- [ ] Scholarship finder tested with student profiles
- [ ] Mobile layout tested on 320px, 375px, 414px widths
- [ ] iOS Safari voice input tested (webkit prefix)
- [ ] Android Chrome voice input tested
- [ ] PWA manifest added for "Add to Home Screen"
- [ ] All helpline numbers verified
- [ ] Offline fallback page added

### Useful APIs & Resources

| Service | URL | Purpose |
|---|---|---|
| MyScheme | myscheme.gov.in/api | Official scheme data |
| National Scholarship Portal | scholarships.gov.in | Scholarship data |
| PM-KISAN | pmkisan.gov.in | Farmer scheme |
| NALSA (Legal Aid) | nalsa.gov.in | Legal aid centers |
| NTA (Exams) | nta.ac.in | Entrance exam forms |

---

*Built with ❤️ for Digital India — Saarthi AI © 2026*
