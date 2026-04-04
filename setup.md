# Saarthi AI - Quick Startup & Configuration Guide

Welcome to **Saarthi AI**! This guide will help you configure the environment and run both the frontend and backend servers.

## 1. Prerequisites
- **Python 3.9+**
- **Node.js** (optional, if you plan to use `npx` or npm in the future)
- **Supabase Account** (for Auth and pgvector Database)
- **AWS Account** (for Bedrock Models)
- **WhatsApp API Credentials** (if using WhatsApp integration)

## 2. Environment Configuration (`.env`)
In the `Backend/` directory, create or update your `.env` file with your credentials:

```ini
PORT=8080

# AWS & Bedrock Configurations
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=ap-south-1

BEDROCK_REGION=us-east-1
BEDROCK_INTENT_MODEL=amazon.nova-lite-v1:0
BEDROCK_SUMMARIZE_MODEL=amazon.nova-pro-v1:0
BEDROCK_SCHEME_MODEL=amazon.nova-pro-v1:0

# Supabase Configurations
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key

# Text-to-Speech Settings
TTS_DEFAULT_LANG=hi
TTS_CACHE_ENABLED=true
TTS_VOICE_SPEED=1.0
TTS_VOICE_VOLUME=0.9

# Third-Party API
WHATSAPP_TOKEN=your_whatsapp_token
PHONE_ID=your_phone_id
```

## 3. Backend Setup

1. Open a terminal and navigate to the `Backend` directory:
   ```bash
   cd Backend
   ```
2. Create and activate a Virtual Environment:
   ```bash
   # On Windows:
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI backend server:
   ```bash
   python main.py
   ```
   *The server will start on `http://127.0.0.1:8080/` with auto-reload enabled.*

## 4. Frontend Setup

1. Open a new terminal and navigate to the `Frontend` directory:
   ```bash
   cd Frontend
   ```
2. Start a simple HTTP server to serve the frontend files:
   ```bash
   <!-- python -m http.server 8000 --bind 127.0.0.1 -->
   ```
3. Open your browser and navigate to:
   [http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html)

---

## Testing Status & Known Issues

During the latest tests across all primary features (Login, Dashboard, Schemes, Profile, Legal, Education):
- **Backend Infrastructure**: Seamlessly connecting to Supabase and authenticating with AWS Bedrock via `boto3` utilizing the newly configured environment variables.
- **Legal Module**: Working perfectly. Analysis pipeline triggers correctly on User Prompts.
- **Profile Module**: Working perfectly. Clean UI mapping.
- **Auth Flow**: The OTP login flow (`sendOtp` call) might experience reference errors depending on whether `auth.js` or `api.js` loads in the correct order on the frontend.
- **Schemes / Education Feed**: Requires seeding the Supabase database with live data (or completing the JS mock fetchers) to populate the frontend grid UI.

*For further deployments, consider running the backend using Gunicorn and hosting the static frontend on Vercel or Netlify.*
