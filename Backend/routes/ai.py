import boto3, json, os, re, base64, tempfile
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from core.supabase_bedrock import log_query
from datetime import datetime
import uuid

router = APIRouter()
bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("BEDROCK_REGION", "us-east-1"))

VOICE_MAP = {
    "hi": "hi-IN-SwaraNeural",
    "en": "en-IN-NeerjaNeural",
    "mr": "mr-IN-AarohiNeural",
    "bn": "bn-IN-TanishaaNeural",
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "gu": "gu-IN-DhwaniNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "pa": "pa-IN-OjasNeural",
    "or": "or-IN-SubhasiniNeural",
    "as": "as-IN-PriyomNeural",
    "ur": "ur-IN-GulNeural",
    "ne": "ne-IN-HemkalaNeural",
    "sd": "sd-IN-WiqarNeural",
}

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    lang: str
    profile: dict
    history: Optional[List[ChatMessage]] = [] # Stores conversation context
    session_id: Optional[str] = None

class DocChatRequest(BaseModel):
    message: str
    lang: str
    profile: dict
    document: str
    document_name: str
    is_pdf: bool = False
    history: Optional[List[ChatMessage]] = []
    session_id: Optional[str] = None

def clean_for_tts(text: str) -> str:
    """Strip formatting but keep all content for TTS."""
    return re.sub(r'\s+', ' ',
        re.sub(r'https?://\S+', '',
        re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1',
        re.sub(r'\*\*(.+?)\*\*', r'\1',
        re.sub(r'\*(.+?)\*', r'\1',
        re.sub(r'#{1,3}\s+', '',
        re.sub(r'[•\-]\s+', ', ',
        text.replace('\n', ' ')))))))).strip()

async def generate_tts(text: str, lang: str) -> str:
    """Generate Edge TTS for full text in chunks, return base64 MP3."""
    try:
        import edge_tts
        # Extract base lang (e.g., 'hi' from 'hi-IN') to match VOICE_MAP keys
        base_lang = lang.split('-')[0]
        voice = VOICE_MAP.get(base_lang, VOICE_MAP["hi"])
        clean = clean_for_tts(text)

        chunks = []
        while len(clean) > 0:
            if len(clean) <= 500:
                chunks.append(clean)
                break
            cut = 500
            while cut > 400 and clean[cut] != ' ':
                cut -= 1
            chunks.append(clean[:cut].strip())
            clean = clean[cut:].strip()

        all_audio = b""
        for chunk in chunks:
            if not chunk:
                continue
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name
            communicate = edge_tts.Communicate(chunk, voice, rate="-5%")
            await communicate.save(tmp_path)
            with open(tmp_path, "rb") as f:
                all_audio += f.read()
            os.unlink(tmp_path)

        return base64.b64encode(all_audio).decode("utf-8")
    except Exception as e:
        print(f"[Edge TTS Error]: {e}")
        return ""

def get_system_prompt(lang, profile):
    return f"""You are Saarthi AI, a helpful assistant for Indian government schemes and legal matters.
Respond in {lang} language.
User profile: State={profile.get('state', 'Unknown')}, Income={profile.get('income', 'Unknown')}, Age={profile.get('age', 'Unknown')}

When the user asks about any government scheme, ALWAYS provide ALL of these sections:

**1. Scheme Overview** - What the scheme is and its purpose
**2. Eligibility Criteria** - Who can apply (bullet points for each criterion)
**3. Benefits** - Exact financial or other benefits
**4. How to Apply** - Numbered step-by-step application process
**5. Required Documents** - Bullet list of all documents needed
**6. Official Website & Helpline** - Website URL and helpline number

Formatting rules:
- Use bullet points with • for lists
- Use 1. 2. 3. for numbered steps
- Use **bold** for headings
- Use actual {lang} script characters throughout
- Do NOT return JSON - plain text only"""

def store_message(mobile: str, role: str, message: str, lang: str):
    """Store a single message (user or assistant) in chat_history table."""
    try:
        from core.supabase_client import get_supabase
        db = get_supabase()
        db.table("chat_history").insert({
            "mobile": mobile,
            "role": role,
            "message": message,
            "lang": lang,
        }).execute()
    except Exception as e:
        print(f"[Store Message Error]: {e}")

@router.get("/chat-history")
async def get_chat_history(mobile: str, limit: int = 50):
    """Return the last `limit` messages for this user, oldest first."""
    try:
        from core.supabase_client import get_supabase
        supabase = get_supabase()
        result = (
            supabase.table("chat_history")
            .select("role, message, lang, created_at")
            .eq("mobile", mobile)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return {"history": result.data or []}
    except Exception as e:
        print(f"[Fetch History Error]: {e}")
        return {"history": []}

@router.post("/chat")
async def chat(req: ChatRequest):
    system_prompt = get_system_prompt(req.lang, req.profile)
    
    # Generate session ID if not provided
    if not req.session_id:
        req.session_id = str(uuid.uuid4())
    
    # Construct message thread including history
    messages = []
    if req.history:
        for msg in req.history:
            messages.append({
                "role": msg.role,
                "content": [{"text": msg.content}]
            })
    
    # Add the latest user message
    messages.append({
        "role": "user",
        "content": [{"text": req.message}]
    })

    # Limit history to last 10 messages to avoid token limits
    if len(messages) > 10:
        messages = messages[-10:]

    response = bedrock.invoke_model(
        modelId=os.getenv("BEDROCK_SUMMARIZE_MODEL", "amazon.nova-pro-v1:0"),
        body=json.dumps({
            "system": [{"text": system_prompt}],
            "messages": messages
        })
    )
    
    reply = json.loads(response["body"].read())["output"]["message"]["content"][0]["text"].strip()

    # If LLM still returns JSON (failsafe), extract reply field
    if reply.startswith("{"):
        try:
            parsed = json.loads(reply)
            reply = parsed.get("reply", reply)
        except Exception:
            pass

    tts_audio = await generate_tts(reply, req.lang)

    # Database logging
    mobile = req.profile.get("mobile", "")
    if mobile:
        try:
    # Log query to existing log_query function
            log_query(mobile, req.message, req.lang, "", [])

            # Store user message then assistant reply as separate rows
            store_message(mobile, "user", req.message, req.lang)
            store_message(mobile, "assistant", reply, req.lang)
        except Exception as e:
            print(f"[Logging Error]: {e}")

    # Prepare updated history to return
    updated_history = req.history + [
        ChatMessage(role="user", content=req.message, timestamp=datetime.utcnow().isoformat()),
        ChatMessage(role="assistant", content=reply, timestamp=datetime.utcnow().isoformat())
    ]

    return {
        "reply": reply, 
        "tts_audio": tts_audio,
        "session_id": req.session_id,
        "history": updated_history
    }

@router.post("/chat-with-doc")
async def chat_with_doc(req: DocChatRequest):
    system_prompt = f"""You are Saarthi AI, a legal document analyst for Indian citizens.
Respond in {req.lang} language. Document: "{req.document_name}"

Give comprehensive analysis covering:
- Document type and purpose
- Key contents and meaning
- Legal rights and obligations
- Immediate action steps
- Relevant laws and helplines
- Any deadlines

Use actual {req.lang} characters. Plain text only, no JSON.
End with: National Legal Aid helpline 15100 (free)."""

    # Generate session ID if not provided
    if not req.session_id:
        req.session_id = str(uuid.uuid4())

    # Prepare content based on document type
    if req.is_pdf:
        content = [
            {"document": {"format": "pdf", "name": req.document_name, "source": {"bytes": req.document}}},
            {"text": req.message or "Analyze this document."}
        ]
    else:
        ext = req.document_name.split(".")[-1].lower()
        fmt = "jpeg" if ext in ["jpg", "jpeg"] else "png"
        content = [
            {"image": {"format": fmt, "source": {"bytes": req.document}}},
            {"text": req.message or "Analyze this document."}
        ]

    # Include history if available (for document chat context)
    messages = [{"role": "user", "content": content}]
    
    # If there's history, add previous context (limited to last 5)
    if req.history:
        prev_messages = []
        for msg in req.history[-5:]:  # Last 5 messages for context
            prev_messages.append({
                "role": msg.role,
                "content": [{"text": msg.content}]
            })
        messages = prev_messages + messages

    response = bedrock.invoke_model(
        modelId=os.getenv("BEDROCK_SUMMARIZE_MODEL", "amazon.nova-pro-v1:0"),
        body=json.dumps({
            "system": [{"text": system_prompt}],
            "messages": messages
        })
    )
    
    reply = json.loads(response["body"].read())["output"]["message"]["content"][0]["text"].strip()
    
    if reply.startswith("{"):
        try:
            parsed = json.loads(reply)
            reply = parsed.get("reply", reply)
        except Exception:
            pass

    tts_audio = await generate_tts(reply, req.lang)

    # Log document query
    mobile = req.profile.get("mobile", "")
    if mobile:
        try:
            store_message(mobile, "user", f"[DOC: {req.document_name}] {req.message}", req.lang)
            store_message(mobile, "assistant", reply, req.lang)
        except Exception as e:
            print(f"[Doc Logging Error]: {e}")

    # Prepare updated history
    updated_history = req.history + [
        ChatMessage(role="user", content=f"[Document: {req.document_name}] {req.message}", timestamp=datetime.utcnow().isoformat()),
        ChatMessage(role="assistant", content=reply, timestamp=datetime.utcnow().isoformat())
    ]

    return {
        "reply": reply, 
        "tts_audio": tts_audio,
        "session_id": req.session_id,
        "history": updated_history
    }