# Saarthi AI — Complete Codebase & Architecture Guide

## Project Structure

```
TA prototype/
├── Backend/
│   ├── main.py
│   ├── .env
│   ├── requirements.txt
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── ai.py
│   │   ├── auth.py
│   │   ├── schemes.py
│   │   ├── recommendations.py
│   │   └── admin.py
│   ├── core/
│   │   ├── supabase_client.py
│   │   ├── supabase_bedrock.py
│   │   ├── recommendation_engine.py
│   │   └── bedrock_client.py
│   └── models/
│       └── scheme.py
└── Frontend/
    ├── index.html
    ├── login.html
    ├── my-schemes.html
    ├── apply-scheme.html
    ├── dashboard.html
    ├── JS/
    │   ├── api.js
    │   ├── main.js
    │   └── login.js
    └── CSS/
        └── login.css
```

---

## Supabase Tables (Run in Supabase SQL Editor)

```sql
-- Schemes
create table schemes (
    scheme_id text primary key,
    name_en text,
    name_hi text,
    category text,
    state text default 'central',
    description text,
    benefits jsonb default '{}',
    eligibility jsonb default '{}',
    target_group jsonb default '[]',
    apply_url text,
    is_active boolean default true,
    priority text default 'normal',
    is_flagship boolean default false,
    source_query text,
    created_at timestamptz default now()
);

-- Users
create table users (
    id uuid primary key default gen_random_uuid(),
    mobile text unique,
    name text,
    profile jsonb default '{}',
    created_at timestamptz default now()
);

-- User Queries (Search History)
create table user_queries (
    query_id uuid primary key default gen_random_uuid(),
    mobile text,
    query_text text,
    lang_detected text default 'en',
    intent text,
    schemes_returned jsonb default '[]',
    timestamp timestamptz default now()
);

-- Applications
create table applications (
    application_id uuid primary key default gen_random_uuid(),
    user_id text,
    scheme_id text,
    scheme_name text,
    status text default 'submitted',
    user_details jsonb default '{}',
    submitted_at timestamptz default now()
);
```

---

## .env File

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
BEDROCK_REGION=us-east-1
BEDROCK_SUMMARIZE_MODEL=amazon.nova-pro-v1:0
BEDROCK_SCHEME_MODEL=amazon.nova-pro-v1:0
PORT=8080
DEV_MODE=true
```

---

## Backend Files

### `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import uvicorn, os

load_dotenv()

from routes.schemes import router as schemes_router
from routes.ai import router as ai_router
from routes.auth import router as auth_router
from routes.recommendations import router as recommendations_router
from routes.admin import router as admin_router

app = FastAPI(title="Saarthi AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(schemes_router)
app.include_router(ai_router)
app.include_router(auth_router)
app.include_router(recommendations_router)
app.include_router(admin_router)

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return FileResponse(status_code=204)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Saarthi AI API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)), reload=True)
```

---

### `core/supabase_client.py`

```python
import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

_client: Client = None

def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client
```

---

### `core/supabase_bedrock.py`

```python
import os, json, uuid, boto3
from datetime import datetime
from core.supabase_client import get_supabase

BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

_INFERENCE_PROFILE_MAP = {
    "amazon.nova-pro-v1:0":   "us.amazon.nova-pro-v1:0",
    "amazon.nova-lite-v1:0":  "us.amazon.nova-lite-v1:0",
    "amazon.nova-micro-v1:0": "us.amazon.nova-micro-v1:0",
}

def _resolve_model_id(model_id):
    return _INFERENCE_PROFILE_MAP.get(model_id, model_id)

SCHEME_MODEL = _resolve_model_id(os.getenv("BEDROCK_SCHEME_MODEL", "us.amazon.nova-pro-v1:0"))

SCHEME_PROMPT = """You are an expert on Indian government schemes.
Return a JSON array of matching schemes.
STRICT JSON RULES:
- Return ONLY a raw JSON array, no markdown fences.
- Return maximum 5 schemes.
Fields: scheme_id, name_en, name_hi, category, state, description,
benefits (amount), apply_url, is_active (bool), eligibility (age_min, income_max)."""

INTENT_MAP = {
    "kisan": "agriculture", "farmer": "agriculture", "crop": "agriculture",
    "fasal": "agriculture", "खेती": "agriculture", "किसान": "agriculture",
    "health": "health", "hospital": "health", "ayushman": "health",
    "medical": "health", "स्वास्थ्य": "health",
    "scholarship": "education", "education": "education", "student": "education",
    "छात्रवृत्ति": "education", "पढ़ाई": "education",
    "house": "housing", "awas": "housing", "pmay": "housing", "घर": "housing",
    "business": "business", "loan": "business", "mudra": "business",
    "rozgar": "business", "रोजगार": "business", "job": "business",
    "women": "women", "mahila": "women", "महिला": "women", "beti": "women",
    "pension": "social_welfare", "ration": "social_welfare", "bpl": "social_welfare",
    "disability": "social_welfare", "divyang": "social_welfare", "गरीब": "social_welfare",
}

def _repair_json(raw):
    raw = raw.strip()
    if not raw.startswith("["):
        raw = ("[" + raw) if raw.startswith("{") else raw
    depth, last_ok, in_str, esc = 0, -1, False, False
    for i, ch in enumerate(raw):
        if esc:        esc = False; continue
        if ch == "\\": esc = True;  continue
        if ch == '"':  in_str = not in_str; continue
        if in_str:     continue
        if   ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: last_ok = i
    if last_ok == -1: return raw
    return raw[:last_ok + 1].rstrip(", \n\r") + "\n]"

def fetch_schemes_from_bedrock(query, category=None, keywords=None):
    search_query = f"Schemes for {query}"
    if category: search_query += f" (Category: {category})"
    if keywords: search_query += f" (Keywords: {', '.join(keywords)})"
    try:
        client = boto3.client(
            "bedrock-runtime",
            region_name=BEDROCK_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        response = client.converse(
            modelId=SCHEME_MODEL,
            system=[{"text": SCHEME_PROMPT}],
            messages=[{"role": "user", "content": [{"text": search_query}]}],
            inferenceConfig={"maxTokens": 2000, "temperature": 0.1},
        )
        raw = response["output"]["message"]["content"][0]["text"].strip()
        if "```" in raw:
            raw = raw.split("```")[1].strip("json \n")
        raw = _repair_json(raw)
        schemes = json.loads(raw)
        if isinstance(schemes, list) and schemes:
            save_schemes_to_supabase(schemes, source_query=search_query)
        return schemes if isinstance(schemes, list) else []
    except Exception as e:
        print(f"[Bedrock Fetch Error]: {e}")
        return []

def save_schemes_to_supabase(schemes, source_query=""):
    db = get_supabase()
    for scheme in schemes:
        try:
            item = dict(scheme)
            if source_query:
                item["source_query"] = source_query.lower().strip()
            for field in ["benefits", "eligibility"]:
                if isinstance(item.get(field), str):
                    try: item[field] = json.loads(item[field])
                    except: item[field] = {}
            if "target_group" in item and isinstance(item["target_group"], str):
                item["target_group"] = [item["target_group"]]
            db.table("schemes").upsert(item, on_conflict="scheme_id").execute()
        except Exception as e:
            print(f"[Supabase Save Error]: {e}")

def get_scheme_by_id(scheme_id):
    try:
        db = get_supabase()
        res = db.table("schemes").select("*").eq("scheme_id", scheme_id).single().execute()
        if res.data: return res.data
    except Exception: pass
    schemes = fetch_schemes_from_bedrock(scheme_id)
    return schemes[0] if schemes else None

def get_schemes_by_category(category, state=None):
    try:
        db = get_supabase()
        q = db.table("schemes").select("*").eq("category", category).eq("is_active", True)
        if state and state != "central":
            q = q.eq("state", state)
        res = q.execute()
        if res.data: return res.data
    except Exception: pass
    return fetch_schemes_from_bedrock(category, category=category)

def get_all_schemes():
    try:
        db = get_supabase()
        res = db.table("schemes").select("*").eq("is_active", True).execute()
        if res.data: return res.data
    except Exception: pass
    return fetch_schemes_from_bedrock("popular government welfare schemes")

def search_schemes_by_keyword(keyword):
    kl = keyword.lower().strip()
    try:
        db = get_supabase()
        res = db.table("schemes").select("*").eq("is_active", True).or_(
            f"name_en.ilike.%{kl}%,name_hi.ilike.%{kl}%,description.ilike.%{kl}%,category.ilike.%{kl}%"
        ).execute()
        items = res.data or []
        if items:
            def _score(s):
                name = s.get("name_en", "").lower()
                score = 0
                if name.strip() == kl: score += 50
                elif kl in name: score += 15
                if kl in s.get("description", "").lower(): score += 5
                if kl in s.get("category", "").lower(): score += 8
                return score
            scored = sorted(items, key=_score, reverse=True)
            relevant = [s for s in scored if _score(s) > 0]
            return relevant if relevant else scored[:3]
    except Exception as e:
        print(f"[Supabase Search Error]: {e}")
    return fetch_schemes_from_bedrock(keyword, keywords=[keyword])

def check_eligibility(scheme, user_profile):
    e = scheme.get("eligibility", {})
    if not e: return True
    try:
        u_age = int(user_profile.get("age", 0))
        if "age_min" in e and u_age < int(e["age_min"]): return False
        if "age_max" in e and u_age > int(e["age_max"]): return False
        u_income = int(user_profile.get("income", 0))
        if "income_max" in e and u_income > int(e["income_max"]): return False
        if "gender" in e and e["gender"] != "all":
            if user_profile.get("gender", "").lower() != str(e["gender"]).lower(): return False
    except Exception: pass
    return True

def log_query(mobile, query_text, lang="en", intent="", scheme_ids=[]):
    try:
        db = get_supabase()
        db.table("user_queries").insert({
            "mobile": mobile,
            "query_text": query_text.lower().strip(),
            "lang_detected": lang,
            "intent": intent,
            "schemes_returned": scheme_ids,
            "timestamp": datetime.utcnow().isoformat(),
        }).execute()
    except Exception as e:
        print(f"[Query Log Error]: {e}")

def get_search_history(mobile, limit=20):
    try:
        db = get_supabase()
        res = db.table("user_queries").select("*")\
            .eq("mobile", mobile)\
            .order("timestamp", desc=True)\
            .limit(limit)\
            .execute()
        return res.data or []
    except Exception as e:
        print(f"[Search History Error]: {e}")
        return []

def extract_intent_from_history(history):
    category_counts = {}
    keyword_counts = {}
    lang_counts = {}
    for item in history:
        query = item.get("query_text", "").lower()
        lang = item.get("lang_detected", "en")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
        for keyword, category in INTENT_MAP.items():
            if keyword in query:
                category_counts[category] = category_counts.get(category, 0) + 1
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    if not category_counts:
        return {"category_weights": {}, "top_keywords": [], "preferred_lang": "en"}
    max_count = max(category_counts.values())
    category_weights = {cat: count / max_count for cat, count in category_counts.items()}
    top_keywords = sorted(keyword_counts, key=keyword_counts.get, reverse=True)[:5]
    preferred_lang = max(lang_counts, key=lang_counts.get) if lang_counts else "en"
    return {"category_weights": category_weights, "top_keywords": top_keywords, "preferred_lang": preferred_lang}

def create_user(mobile, name="", profile={}):
    try:
        db = get_supabase()
        db.table("users").upsert({"mobile": mobile, "name": name, "profile": profile}, on_conflict="mobile").execute()
    except Exception as e:
        print(f"[Create User Error]: {e}")

def get_user_by_mobile(mobile):
    try:
        db = get_supabase()
        res = db.table("users").select("*").eq("mobile", mobile).single().execute()
        return res.data
    except Exception: return None

def submit_application(user_id, scheme_id, scheme_name, user_details={}):
    try:
        db = get_supabase()
        res = db.table("applications").insert({
            "user_id": user_id, "scheme_id": scheme_id,
            "scheme_name": scheme_name, "status": "submitted",
            "user_details": user_details,
            "submitted_at": datetime.utcnow().isoformat(),
        }).execute()
        return res.data[0].get("application_id") if res.data else None
    except Exception as e:
        print(f"[Submit Application Error]: {e}")
        return None

def get_user_applications(user_id):
    try:
        db = get_supabase()
        res = db.table("applications").select("*").eq("user_id", user_id).execute()
        return res.data or []
    except Exception: return []
```

---

### `core/recommendation_engine.py`

```python
import logging
from typing import Optional
from dataclasses import dataclass, field
from core.bedrock_client import rerank_schemes, explain_recommendation as ai_explain
from core.supabase_bedrock import get_search_history, extract_intent_from_history

logger = logging.getLogger(__name__)
INTERNAL_APPLY_URL = "apply-scheme.html"
BPL_INCOME_THRESHOLD = 120000

WEIGHTS = {
    "eligibility":    0.25,
    "category":       0.20,
    "state":          0.12,
    "demographic":    0.18,
    "priority":       0.08,
    "search_history": 0.17,
}

OCCUPATION_CATEGORY_MAP = {
    "farmer":     ["agriculture", "social_welfare"],
    "student":    ["education", "social_welfare"],
    "business":   ["business", "social_welfare"],
    "unemployed": ["social_welfare", "business", "education"],
    "salaried":   ["health", "housing", "social_welfare"],
    "homemaker":  ["women", "health", "social_welfare"],
    "daily_wage": ["social_welfare", "housing", "health"],
    "artisan":    ["business", "social_welfare"],
    "fisherman":  ["agriculture", "social_welfare"],
}

@dataclass
class UserProfile:
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[int] = None
    caste_category: Optional[str] = None
    education_level: Optional[str] = None
    family_size: Optional[int] = None
    is_bpl: Optional[bool] = None
    has_disability: Optional[bool] = None
    preferred_lang: str = "hi"
    mobile: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        def clean(val):
            if val is None: return None
            s = str(val).lower().strip()
            return s if s else None
        state = clean(data.get("state"))
        if state: state = state.replace(" ", "_")
        return cls(
            age=data.get("age"),
            gender=clean(data.get("gender")),
            state=state,
            occupation=clean(data.get("occupation")),
            annual_income=data.get("income") or data.get("annual_income"),
            caste_category=clean(data.get("caste_category") or data.get("caste")),
            education_level=clean(data.get("education_level")),
            family_size=data.get("family_size"),
            is_bpl=data.get("is_bpl"),
            has_disability=data.get("has_disability"),
            preferred_lang=data.get("preferred_lang", "hi"),
            mobile=data.get("mobile"),
        )

@dataclass
class ScoredScheme:
    scheme: dict
    score: float = 0.0
    match_reasons: list = field(default_factory=list)
    eligibility_passed: bool = True

    def to_dict(self):
        scheme_copy = dict(self.scheme)
        scheme_id = scheme_copy.get("scheme_id", "")
        return {
            **scheme_copy,
            "recommendation_score": round(float(self.score or 0), 3),
            "match_reasons": self.match_reasons,
            "apply_url": f"{INTERNAL_APPLY_URL}?scheme_id={scheme_id}",
        }

class RecommendationEngine:

    def recommend(self, user_profile, all_schemes, query_intent=None, top_n=10, use_llm_rerank=True, lang="en"):
        if not all_schemes: return []
        profile = UserProfile.from_dict(user_profile) if isinstance(user_profile, dict) else user_profile
        if profile.annual_income and int(profile.annual_income) < BPL_INCOME_THRESHOLD:
            profile.is_bpl = True

        history_intent = {}
        if profile.mobile:
            try:
                history = get_search_history(profile.mobile, limit=30)
                history_intent = extract_intent_from_history(history)
            except Exception as e:
                logger.warning(f"Could not fetch search history: {e}")

        scored = []
        for scheme in all_schemes:
            result = self._score_scheme(scheme, profile, query_intent, lang, history_intent)
            if result.eligibility_passed:
                scored.append(result)

        scored.sort(key=lambda x: x.score, reverse=True)
        top_results = scored[:top_n]

        if use_llm_rerank and len(top_results) > 1:
            try:
                plain = [s.to_dict() for s in top_results]
                query_text = (query_intent or {}).get("query", "")
                reranked = rerank_schemes(plain, profile.__dict__, query_text)
                return reranked[:top_n]
            except Exception as e:
                logger.warning(f"Bedrock re-ranking failed: {e}")

        return [s.to_dict() for s in top_results]

    def explain_recommendation(self, scheme, user_profile, lang="en"):
        try:
            return ai_explain(scheme, user_profile, lang)
        except Exception:
            name = scheme.get("name_en", "Scheme")
            if lang == "hi":
                return f"**{name}** आपके लिए उपयुक्त है।"
            return f"**{name}** matches your profile."

    def _score_scheme(self, scheme, profile, query_intent, lang, history_intent):
        result = ScoredScheme(scheme=scheme)
        if (scheme.get("status") or "active").lower() != "active":
            result.eligibility_passed = False
            return result
        reasons = []
        total = 0.0

        elig_score, elig_reasons, passed = self._score_eligibility(scheme, profile, lang)
        if not passed:
            result.eligibility_passed = False
            return result
        total += elig_score * WEIGHTS["eligibility"]
        reasons.extend(elig_reasons)

        cat_score, cat_reasons = self._score_category(scheme, profile, query_intent or {}, lang)
        total += cat_score * WEIGHTS["category"]
        reasons.extend(cat_reasons)

        state_score, state_reasons = self._score_state(scheme, profile, lang)
        total += state_score * WEIGHTS["state"]
        reasons.extend(state_reasons)

        demo_score, demo_reasons = self._score_demographics(scheme, profile, lang)
        total += demo_score * WEIGHTS["demographic"]
        reasons.extend(demo_reasons)

        total += self._score_priority(scheme) * WEIGHTS["priority"]

        hist_score, hist_reasons = self._score_search_history(scheme, history_intent, lang)
        total += hist_score * WEIGHTS["search_history"]
        reasons.extend(hist_reasons)

        result.score = min(total, 1.0)
        result.match_reasons = reasons
        return result

    def _score_search_history(self, scheme, history_intent, lang):
        if not history_intent or not history_intent.get("category_weights"):
            return 0.5, []
        scheme_cat = (scheme.get("category") or "").lower()
        category_weights = history_intent.get("category_weights", {})
        top_keywords = history_intent.get("top_keywords", [])
        score = 0.0
        reasons = []
        if scheme_cat in category_weights:
            weight = category_weights[scheme_cat]
            score += weight
            if weight > 0.5:
                reasons.append("आपकी खोज इतिहास से मेल" if lang == "hi" else "Matches your search history")
        scheme_text = (
            scheme.get("name_en", "") + " " +
            scheme.get("name_hi", "") + " " +
            scheme.get("description", "")
        ).lower()
        keyword_hits = sum(1 for kw in top_keywords if kw in scheme_text)
        if keyword_hits > 0:
            score = min(score + keyword_hits * 0.15, 1.0)
            if keyword_hits >= 2:
                reasons.append("आपकी रुचि के अनुसार" if lang == "hi" else "Based on your interests")
        return min(score, 1.0), reasons

    def _score_eligibility(self, scheme, profile, lang):
        eligibility = scheme.get("eligibility", {})
        if not eligibility: return 1.0, [], True
        reasons = []
        if profile.age is not None:
            try:
                p_age = int(profile.age)
                a_min = eligibility.get("age_min")
                a_max = eligibility.get("age_max")
                if a_min is not None and p_age < int(a_min): return 0, [], False
                if a_max is not None and p_age > int(a_max): return 0, [], False
                if a_min or a_max:
                    reasons.append("आयु पात्रता" if lang == "hi" else "Age eligible")
            except (ValueError, TypeError): pass
        req_gender = eligibility.get("gender")
        if req_gender and str(req_gender).lower() != "all":
            if profile.gender and str(profile.gender).lower() != str(req_gender).lower():
                return 0, [], False
            reasons.append("महिला योजना" if lang == "hi" else "Gender match")
        m_income = eligibility.get("max_income") or eligibility.get("income_max")
        if m_income is not None and profile.annual_income is not None:
            try:
                if int(profile.annual_income) > int(m_income): return 0, [], False
                reasons.append("आय पात्र" if lang == "hi" else "Income eligible")
            except (ValueError, TypeError): pass
        req_caste = eligibility.get("caste_category") or eligibility.get("caste")
        if req_caste and profile.caste_category:
            allowed = [str(c).lower() for c in (req_caste if isinstance(req_caste, list) else [req_caste]) if c]
            if str(profile.caste_category).lower() not in allowed and "all" not in allowed:
                return 0, [], False
            reasons.append("वर्ग पात्र" if lang == "hi" else "Category match")
        return 1.0, reasons, True

    def _score_category(self, scheme, profile, intent, lang):
        scheme_cat = (scheme.get("category") or "").lower()
        reasons = []
        score = 0.5
        intent_cat = str(intent.get("category") or "").lower()
        if intent_cat and intent_cat == scheme_cat:
            return 1.0, ["आपकी खोज से मेल" if lang == "hi" else "Matches your query"]
        if profile.occupation:
            preferred = OCCUPATION_CATEGORY_MAP.get(profile.occupation, [])
            if scheme_cat in preferred:
                score = 0.9
                reasons.append("आपके पेशे से संबंधित" if lang == "hi" else "Relevant to your occupation")
        targets = scheme.get("target_group", [])
        if isinstance(targets, str): targets = [targets.lower()]
        elif isinstance(targets, list): targets = [str(t).lower() for t in targets]
        if profile.occupation and profile.occupation in targets:
            score = min(score + 0.1, 1.0)
            reasons.append("लक्षित समूह में" if lang == "hi" else "In target group")
        return score, reasons

    def _score_state(self, scheme, profile, lang):
        s_state = (scheme.get("state") or "central").lower()
        if s_state == "central": return 0.8, []
        if profile.state and profile.state.lower().replace(" ", "_") == s_state.replace(" ", "_"):
            return 1.0, ["आपके राज्य की योजना" if lang == "hi" else "Scheme for your state"]
        return 0.3, []

    def _score_demographics(self, scheme, profile, lang):
        score = 0.5
        reasons = []
        text = (scheme.get("description", "") + " " + scheme.get("name_en", "")).lower()
        if profile.is_bpl or (profile.annual_income and profile.annual_income < BPL_INCOME_THRESHOLD):
            if any(kw in text for kw in ["bpl", "poor", "below poverty", "garib", "गरीब"]):
                score += 0.2
                reasons.append("BPL परिवार के लिए" if lang == "hi" else "For BPL family")
        if profile.age and profile.age >= 60:
            if any(kw in text for kw in ["senior", "elderly", "pension", "वृद्ध"]):
                score += 0.2
                reasons.append("वरिष्ठ नागरिकों के लिए" if lang == "hi" else "For senior citizens")
        if profile.occupation == "student" or (profile.age and profile.age <= 25):
            if any(kw in text for kw in ["student", "scholarship", "education", "छात्रवृत्ति"]):
                score += 0.2
                reasons.append("विद्यार्थियों के लिए" if lang == "hi" else "For students")
        if profile.has_disability:
            if any(kw in text for kw in ["disability", "divyang", "handicap", "दिव्यांग"]):
                score += 0.3
                reasons.append("दिव्यांगों के लिए" if lang == "hi" else "For disabled citizens")
        return min(score, 1.0), reasons

    def _score_priority(self, scheme):
        p = (scheme.get("priority") or "normal").lower()
        if p == "high" or scheme.get("is_flagship"): return 1.0
        if p == "medium": return 0.6
        return 0.4
```

---

### `routes/auth.py`

```python
import os, random, time, uuid
from fastapi import APIRouter, HTTPException
from supabase import create_client
from pydantic import BaseModel

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

router = APIRouter()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

otp_store: dict[str, dict] = {}
DEV_MODE = os.environ.get("DEV_MODE", "true").lower() == "true"

class OTPRequest(BaseModel):
    mobile: str

class OTPVerify(BaseModel):
    mobile: str
    otp: str

@router.post("/send-otp")
async def send_otp(req: OTPRequest):
    otp = str(random.randint(100000, 999999))
    otp_store[req.mobile] = {"otp": otp, "expires": time.time() + 300}
    print(f"[DEV] OTP for {req.mobile}: {otp}")
    return {"success": True}

@router.post("/verify-otp")
async def verify_otp(req: OTPVerify):
    if not DEV_MODE:
        stored = otp_store.get(req.mobile)
        if not stored or stored["otp"] != req.otp or time.time() > stored["expires"]:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        del otp_store[req.mobile]
    try:
        result = supabase.table("users").upsert(
            {"mobile": req.mobile}, on_conflict="mobile"
        ).execute()
        user = result.data[0] if result.data else {"mobile": req.mobile}
    except Exception:
        user = {"mobile": req.mobile, "id": str(uuid.uuid4())}
    token = str(uuid.uuid4())
    return {"success": True, "token": token, "user": user}
```

---

### `routes/ai.py`

```python
import boto3, json, os
from fastapi import APIRouter
from pydantic import BaseModel
from core.supabase_bedrock import log_query

router = APIRouter()
bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("BEDROCK_REGION", "us-east-1"))

class ChatRequest(BaseModel):
    message: str
    lang: str
    profile: dict

class DocChatRequest(BaseModel):
    message: str
    lang: str
    profile: dict
    document: str
    document_name: str
    is_pdf: bool = False

def get_system_prompt(lang, profile):
    return f"""You are Saarthi AI, a helpful assistant for Indian government schemes and legal matters.
Always respond in {lang} language.
User profile: State={profile.get('state')}, Income={profile.get('income')}, Age={profile.get('age')}
When asked about schemes: identify relevant schemes, explain eligibility simply,
list documents needed, provide application steps and helpline.
Keep responses clear, short, and actionable."""

@router.post("/chat")
async def chat(req: ChatRequest):
    system_prompt = get_system_prompt(req.lang, req.profile)
    response = bedrock.invoke_model(
        modelId=os.getenv("BEDROCK_SUMMARIZE_MODEL", "amazon.nova-pro-v1:0"),
        body=json.dumps({
            "system": [{"text": system_prompt}],
            "messages": [{"role": "user", "content": [{"text": req.message}]}]
        })
    )
    reply = json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]
    mobile = req.profile.get("mobile", "")
    if mobile:
        log_query(mobile, req.message, req.lang, "", [])
    return {"reply": reply}

@router.post("/chat-with-doc")
async def chat_with_doc(req: DocChatRequest):
    system_prompt = f"""You are Saarthi AI, a legal document analyst for Indian citizens.
Always respond in {req.lang} language. The user uploaded: "{req.document_name}"
1. Identify document type
2. Explain in simple language
3. Identify legal issues or rights
4. Suggest immediate action steps
5. Mention relevant laws or helplines
6. Flag any deadlines
Always end with: "For legal advice: National Legal Aid helpline 15100 (free)." """
    if req.is_pdf:
        content = [
            {"document": {"format": "pdf", "name": req.document_name, "source": {"bytes": req.document}}},
            {"text": req.message}
        ]
    else:
        ext = req.document_name.split(".")[-1].lower()
        fmt = "jpeg" if ext in ["jpg", "jpeg"] else "png"
        content = [
            {"image": {"format": fmt, "source": {"bytes": req.document}}},
            {"text": req.message}
        ]
    response = bedrock.invoke_model(
        modelId=os.getenv("BEDROCK_SUMMARIZE_MODEL", "amazon.nova-pro-v1:0"),
        body=json.dumps({
            "system": [{"text": system_prompt}],
            "messages": [{"role": "user", "content": content}]
        })
    )
    reply = json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]
    return {"reply": reply}
```

---

### `routes/schemes.py`

```python
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import asyncio, functools, time, hashlib, logging
from concurrent.futures import ThreadPoolExecutor
from core.supabase_bedrock import (
    get_scheme_by_id, get_schemes_by_category,
    get_all_schemes, search_schemes_by_keyword, check_eligibility,
)
from models.scheme import EligibilityCheckRequest

router = APIRouter(prefix="/api/v1/schemes", tags=["Schemes"])
logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=4)

def _run_sync(fn, *args):
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(_executor, functools.partial(fn, *args))

_scheme_cache: dict = {}
_SCHEME_CACHE_TTL = 600

def _sc_key(*parts):
    return hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest()

def _sc_get(key):
    entry = _scheme_cache.get(key)
    if entry and (time.time() - entry["ts"]) < _SCHEME_CACHE_TTL:
        return entry["data"]
    return None

def _sc_set(key, data):
    _scheme_cache[key] = {"data": data, "ts": time.time()}
    now = time.time()
    for k in [k for k, v in _scheme_cache.items() if now - v["ts"] >= _SCHEME_CACHE_TTL]:
        del _scheme_cache[k]

_CATEGORIES_RESPONSE = JSONResponse(content={"categories": [
    {"id": "agriculture",    "label_en": "Agriculture & Farming",    "label_hi": "कृषि और खेती"},
    {"id": "education",      "label_en": "Education & Scholarships", "label_hi": "शिक्षा और छात्रवृत्ति"},
    {"id": "health",         "label_en": "Health & Insurance",       "label_hi": "स्वास्थ्य और बीमा"},
    {"id": "women",          "label_en": "Women & Child Welfare",    "label_hi": "महिला और बाल कल्याण"},
    {"id": "housing",        "label_en": "Housing",                  "label_hi": "आवास"},
    {"id": "business",       "label_en": "Business & Employment",    "label_hi": "व्यवसाय और रोजगार"},
    {"id": "social_welfare", "label_en": "Social Welfare",           "label_hi": "सामाजिक कल्याण"},
]})

@router.get("/")
async def list_schemes(category: Optional[str] = Query(None), state: Optional[str] = Query(None), target_group: Optional[str] = Query(None)):
    cache_key = _sc_key("list", category, state, target_group)
    cached = _sc_get(cache_key)
    if cached: return cached
    try:
        schemes = await _run_sync(get_schemes_by_category, category, state) if category else await _run_sync(get_all_schemes)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch schemes")
    if target_group:
        schemes = [s for s in schemes if target_group in s.get("target_group", [])]
    result = {"success": True, "total": len(schemes), "data": schemes}
    _sc_set(cache_key, result)
    return result

@router.get("/categories")
async def list_categories():
    return _CATEGORIES_RESPONSE

@router.get("/search")
async def search_schemes(q: str = Query(..., min_length=2)):
    cache_key = _sc_key("search", q.lower().strip())
    cached = _sc_get(cache_key)
    if cached: return cached
    try:
        results = await _run_sync(search_schemes_by_keyword, q)
    except Exception:
        raise HTTPException(status_code=500, detail="Search failed")
    result = {"success": True, "total": len(results), "data": results}
    _sc_set(cache_key, result)
    return result

@router.get("/{scheme_id}")
async def get_scheme(scheme_id: str):
    cache_key = _sc_key("scheme", scheme_id)
    cached = _sc_get(cache_key)
    if cached: return cached
    try:
        scheme = await _run_sync(get_scheme_by_id, scheme_id)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch scheme")
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    result = {"success": True, "data": scheme}
    _sc_set(cache_key, result)
    return result

@router.post("/eligibility")
async def check_scheme_eligibility(req: EligibilityCheckRequest):
    try:
        scheme = await _run_sync(get_scheme_by_id, req.scheme_id)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch scheme")
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    try:
        eligible = check_eligibility(scheme, req.user_profile.model_dump())
    except Exception:
        raise HTTPException(status_code=500, detail="Eligibility check failed")
    return {
        "success": True, "scheme_id": req.scheme_id,
        "eligible": eligible, "scheme_name": scheme.get("name_en"),
        "apply_url": scheme.get("apply_url") if eligible else None,
    }
```

---

### `routes/recommendations.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from core.recommendation_engine import RecommendationEngine
from core.supabase_bedrock import get_all_schemes, get_schemes_by_category, get_scheme_by_id, log_query

router = APIRouter(prefix="/api/v1/recommendations", tags=["Recommendations"])
logger = logging.getLogger(__name__)
engine = RecommendationEngine()

class RecommendRequest(BaseModel):
    user_profile: Dict[str, Any]
    query_intent: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    top_n: int = 10
    lang: str = "en"
    use_llm_rerank: bool = True

class ExplainRequest(BaseModel):
    scheme_id: str
    user_profile: Dict[str, Any]
    lang: str = "en"

@router.post("/")
async def get_recommendations(req: RecommendRequest):
    try:
        schemes = get_schemes_by_category(req.category) if req.category else get_all_schemes()
        if not schemes:
            return {"success": True, "total": 0, "recommendations": [], "message": "No schemes found."}
        results = engine.recommend(
            user_profile=req.user_profile, all_schemes=schemes,
            query_intent=req.query_intent, top_n=req.top_n,
            use_llm_rerank=req.use_llm_rerank, lang=req.lang,
        )
        mobile = req.user_profile.get("mobile", "")
        if mobile and req.query_intent:
            query_text = req.query_intent.get("query", "")
            scheme_ids = [r.get("scheme_id") for r in results if r.get("scheme_id")]
            log_query(mobile, query_text, req.lang, req.category or "", scheme_ids)
        return {
            "success": True, "total": len(results), "recommendations": results,
            "message": f"{len(results)} schemes recommended." if req.lang == "en"
            else f"आपके लिए {len(results)} योजनाएं अनुशंसित हैं।",
        }
    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@router.post("/explain")
async def explain_recommendation(req: ExplainRequest):
    try:
        scheme = get_scheme_by_id(req.scheme_id)
        if not scheme:
            raise HTTPException(status_code=404, detail="Scheme not found")
        explanation = engine.explain_recommendation(scheme=scheme, user_profile=req.user_profile, lang=req.lang)
        return {
            "success": True, "scheme_id": req.scheme_id,
            "scheme_name": scheme.get("name_en"), "explanation": explanation,
            "apply_url": f"apply-scheme.html?scheme_id={scheme.get('scheme_id','')}",
        }
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar")
async def get_similar_schemes(scheme_id: str, top_n: int = 5, lang: str = "en"):
    try:
        base_scheme = get_scheme_by_id(scheme_id)
        if not base_scheme:
            raise HTTPException(status_code=404, detail="Scheme not found")
        category = base_scheme.get("category")
        target_groups = base_scheme.get("target_group", [])
        similar_pool = get_schemes_by_category(category) if category else get_all_schemes()
        similar_pool = [s for s in similar_pool if s.get("scheme_id") != scheme_id]
        def overlap_score(scheme):
            s_groups = scheme.get("target_group", [])
            if isinstance(s_groups, str): s_groups = [s_groups]
            tg = [target_groups] if isinstance(target_groups, str) else target_groups
            return len(set(s_groups) & set(tg))
        similar_pool.sort(key=overlap_score, reverse=True)
        top_similar = similar_pool[:top_n]
        for s in top_similar:
            s["apply_url"] = f"apply-scheme.html?scheme_id={s.get('scheme_id','')}"
        return {"success": True, "base_scheme": base_scheme.get("name_en"), "similar_schemes": top_similar}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### `routes/admin.py`

```python
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import Counter
import uuid, logging
from core.supabase_client import get_supabase

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])
logger = logging.getLogger(__name__)

class SchemeCreate(BaseModel):
    name_en: str
    name_hi: str
    category: str
    state: str = "central"
    description: str
    benefits: Dict[str, Any] = {}
    eligibility: Dict[str, Any] = {}
    is_active: bool = True
    target_group: List[str] = []

@router.get("/dashboard")
async def get_dashboard_stats():
    try:
        db = get_supabase()
        total_schemes = db.table("schemes").select("scheme_id", count="exact").execute().count or 0
        total_users = db.table("users").select("id", count="exact").execute().count or 0
        all_queries = db.table("user_queries").select("*").execute().data or []
        failed = [q for q in all_queries if not q.get("schemes_returned")]
        lang_counts = Counter(q.get("lang_detected", "unknown") for q in all_queries)
        total_apps = db.table("applications").select("application_id", count="exact").execute().count or 0
        return {
            "success": True,
            "stats": {
                "total_schemes": total_schemes, "total_users": total_users,
                "total_queries": len(all_queries), "failed_queries": len(failed),
                "total_applications": total_apps,
            },
            "language_distribution": dict(lang_counts),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schemes")
async def list_schemes(category: Optional[str] = Query(None), limit: int = Query(100)):
    try:
        db = get_supabase()
        q = db.table("schemes").select("*").limit(limit)
        if category: q = q.eq("category", category)
        items = q.execute().data or []
        return {"success": True, "total": len(items), "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schemes")
async def create_scheme(scheme: SchemeCreate):
    try:
        db = get_supabase()
        scheme_id = f"scheme_{uuid.uuid4().hex[:12]}"
        item = {"scheme_id": scheme_id, "created_at": datetime.utcnow().isoformat(), **scheme.model_dump()}
        db.table("schemes").insert(item).execute()
        return {"success": True, "scheme_id": scheme_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/schemes/{scheme_id}")
async def delete_scheme(scheme_id: str):
    try:
        db = get_supabase()
        db.table("schemes").delete().eq("scheme_id", scheme_id).execute()
        return {"success": True, "message": "Scheme deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def list_users(limit: int = Query(100)):
    try:
        db = get_supabase()
        items = db.table("users").select("*").limit(limit).execute().data or []
        return {"success": True, "total": len(items), "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/failed-queries")
async def get_failed_queries(limit: int = Query(50)):
    try:
        db = get_supabase()
        all_q = db.table("user_queries").select("*").execute().data or []
        failed = [q for q in all_q if not q.get("schemes_returned")]
        return {"success": True, "total": len(failed), "data": failed[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/applications")
async def list_applications(limit: int = Query(100)):
    try:
        db = get_supabase()
        items = db.table("applications").select("*").limit(limit).execute().data or []
        return {"success": True, "total": len(items), "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Frontend Files

### `JS/api.js`

```javascript
const API_BASE = "http://localhost:8080";

function getUser() {
    try { return JSON.parse(localStorage.getItem("saarthi_user") || "{}"); }
    catch { return {}; }
}

async function sendOtp(mobile) {
    const res = await fetch(`${API_BASE}/send-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mobile })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to send OTP");
    return data;
}

async function verifyOtp(mobile, otp) {
    const res = await fetch(`${API_BASE}/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mobile, otp })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "OTP verification failed");
    if (data.token) localStorage.setItem("saarthi_token", data.token);
    if (data.user) localStorage.setItem("saarthi_user", JSON.stringify(data.user));
    return { access_token: data.token, user: data.user, ...data };
}

function saveToken(token) { localStorage.setItem("saarthi_token", token); }
function saveUser(user) { localStorage.setItem("saarthi_user", JSON.stringify(user)); }
function getToken() { return localStorage.getItem("saarthi_token"); }
function logout() {
    localStorage.removeItem("saarthi_token");
    localStorage.removeItem("saarthi_user");
    window.location.href = "login.html";
}

async function askSaarthi(userMessage, lang, userProfile) {
    const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${getToken()}` },
        body: JSON.stringify({ message: userMessage, lang, profile: userProfile })
    });
    const data = await response.json();
    return data.reply;
}

async function fetchAllSchemes() {
    const res = await fetch(`${API_BASE}/api/v1/schemes/`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

async function apiFetch(path, options = {}) {
    const res = await fetch(`${API_BASE}/api/v1${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

async function fetchRecommendations(userProfile) {
    return apiFetch("/recommendations/", {
        method: "POST",
        body: JSON.stringify({ user_profile: userProfile, top_n: 10, lang: "en" })
    });
}

async function fetchRecommendationExplanation(schemeId, userProfile, lang = "en") {
    return apiFetch("/recommendations/explain", {
        method: "POST",
        body: JSON.stringify({ scheme_id: schemeId, user_profile: userProfile, lang })
    });
}
```

---

## How to Run

### Terminal 1 — Backend
```powershell
cd "C:\Users\ROHAN\OneDrive\Desktop\TA prototype\Backend"
.\venv\Scripts\activate
python main.py
```

### Terminal 2 — Frontend
```powershell
cd "C:\Users\ROHAN\OneDrive\Desktop\TA prototype\Frontend"
python -m http.server 8000
```

Then open: **http://127.0.0.1:8000**

---

## How Search History Recommendations Work

1. User chats → every message saved to `user_queries` table in Supabase
2. On recommendations request → last 30 queries fetched for that user
3. Keywords extracted → mapped to categories (e.g. "kisan" → agriculture)
4. Category weights calculated (normalized 0–1)
5. Each scheme gets a **17% score boost** based on history match
6. Result: schemes matching user's interests surface higher

