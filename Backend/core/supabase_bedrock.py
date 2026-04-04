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
