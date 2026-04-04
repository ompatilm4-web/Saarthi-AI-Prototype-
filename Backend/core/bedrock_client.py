import os
import json
import re
import boto3
from botocore.exceptions import ClientError

AWS_REGION     = os.getenv("AWS_REGION", "ap-south-1")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

_INFERENCE_PROFILE_MAP = {
    "amazon.nova-pro-v1:0":   "us.amazon.nova-pro-v1:0",
    "amazon.nova-lite-v1:0":  "us.amazon.nova-lite-v1:0",
    "amazon.nova-micro-v1:0": "us.amazon.nova-micro-v1:0",
}

def _resolve_model_id(model_id: str) -> str:
    return _INFERENCE_PROFILE_MAP.get(model_id, model_id)

INTENT_MODEL    = _resolve_model_id(os.getenv("BEDROCK_INTENT_MODEL",    "us.amazon.nova-lite-v1:0"))
SUMMARIZE_MODEL = _resolve_model_id(os.getenv("BEDROCK_SUMMARIZE_MODEL", "us.amazon.nova-pro-v1:0"))
SCHEME_MODEL    = _resolve_model_id(os.getenv("BEDROCK_SCHEME_MODEL",    "us.amazon.nova-pro-v1:0"))

LANG_NAMES = {
    "hi": "Hindi",   "mr": "Marathi",   "ta": "Tamil",    "te": "Telugu",
    "kn": "Kannada", "ml": "Malayalam", "bn": "Bengali",
    "gu": "Gujarati","pa": "Punjabi",   "en": "English",
    "ur": "Urdu",    "or": "Odia",      "as": "Assamese",
}

_bedrock = None

def _get_bedrock():
    global _bedrock
    if _bedrock is None:
        _bedrock = boto3.client(
            "bedrock-runtime",
            region_name=BEDROCK_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
    return _bedrock

def _invoke(model_id: str, system_prompt: str, user_message: str,
            max_tokens: int = 1000, temperature: float = 0.3) -> str:
    model_id = _resolve_model_id(model_id)
    try:
        response = _get_bedrock().converse(
            modelId=model_id,
            system=[{"text": system_prompt}],
            messages=[{"role": "user", "content": [{"text": user_message}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": temperature, "topP": 0.9},
        )
        return response["output"]["message"]["content"][0]["text"].strip()
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "ThrottlingException":
            import time; time.sleep(2)
            try:
                response = _get_bedrock().converse(
                    modelId=model_id,
                    system=[{"text": system_prompt}],
                    messages=[{"role": "user", "content": [{"text": user_message}]}],
                    inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
                )
                return response["output"]["message"]["content"][0]["text"].strip()
            except Exception:
                return ""
        print(f"[Bedrock {code}] {e}")
        return ""
    except Exception as e:
        print(f"[Bedrock Error] {e}")
        return ""

def extract_intent_and_filters(query: str) -> dict:
    system_prompt = (
        "You extract search keywords for Indian government scheme database queries.\n"
        "Rules:\n"
        "1. ALWAYS include the exact scheme name in English as the FIRST keyword.\n"
        "2. Include the full official English name and common abbreviations.\n"
        "3. Translate Indic-script scheme names to English.\n"
        "intent options: find_schemes | explain_scheme | how_to_apply | check_eligibility | chat\n"
        "category options: agriculture | education | health | women | housing | business | social_welfare\n\n"
        "Respond with ONLY raw JSON, no markdown:\n"
        '{"intent":"...","category":"...","state":"central","keywords":["..."],"target_group":""}'
    )
    raw = _invoke(INTENT_MODEL, system_prompt, "Query: " + query, max_tokens=250, temperature=0.0)
    _default = {"intent": "find_schemes", "keywords": [], "state": "central"}
    if not raw:
        return _default
    try:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(m.group()) if m else json.loads(raw)
    except Exception:
        return _default

def summarize_schemes(schemes: list, lang: str = "en", user_query: str = "") -> str:
    if not schemes:
        return ""
    lang_name = LANG_NAMES.get(lang, "English")
    s = schemes[0]
    context = {
        "name_en":      s.get("name_en", ""),
        "name_local":   s.get(f"name_{lang}") or s.get("name_hi") or s.get("name_en", ""),
        "description":  s.get("description", "")[:500],
        "benefits":     s.get("benefits", {}),
        "eligibility":  s.get("eligibility", {}),
        "how_to_apply": s.get("how_to_apply", ""),
        "apply_url":    s.get("apply_url", "https://india.gov.in"),
        "documents":    s.get("documents_required", []),
        "category":     s.get("category", ""),
    }
    system_prompt = (
        "You are Saarthi, a friendly assistant for Indian government schemes.\n"
        "Respond ONLY in " + lang_name + ".\n"
        "Return ONLY a single <div class='scheme-card'> HTML snippet. NO <!DOCTYPE>, NO <html>, NO <head>, NO <body>, NO <style> tags.\n"
        "Structure:\n"
        "<div class='scheme-card'>\n"
        "<h3>Scheme Name</h3>\n"
        "<p><b>Benefits:</b> ...</p>\n"
        "<p><b>About:</b> ...</p>\n"
        "<p><b>Eligibility:</b> ...</p>\n"
        "<p><b>How to Apply:</b></p><ol><li>Step 1</li><li>Step 2</li><li>Step 3</li></ol>\n"
        "<p><b>Documents:</b></p><ul><li>Doc 1</li><li>Doc 2</li></ul>\n"
        "<p><b>Official Link:</b> <a href='URL'>URL</a></p>\n"
        "</div>\n"
        "RULES: No full HTML page. No markdown. No code fences. Start directly with <div."
    )
    user_msg = "User searched for: " + (user_query or context["name_en"]) + "\n\nScheme data:\n" + json.dumps(context, ensure_ascii=False)
    result = _invoke(SUMMARIZE_MODEL, system_prompt, user_msg, max_tokens=1200)
    if result:
        import re
        result = result.strip()
        result = re.sub(r"^[`]{3}[a-zA-Z]*", "", result).strip()
        result = re.sub(r"[`]{3}$", "", result).strip()
    return result if result and len(result.strip()) > 60 else ""

def chat_with_assistant(query: str, lang: str = "en") -> str:
    lang_name = LANG_NAMES.get(lang, "English")
    system_prompt = (
        "You are Saarthi, a helpful Indian government services assistant. "
        "Respond ONLY in " + lang_name + ". "
        "Be concise and friendly. Guide users to the right scheme."
    )
    return _invoke(SUMMARIZE_MODEL, system_prompt, "User: " + query, max_tokens=350)

def explain_scheme(scheme: dict, lang: str = "en") -> str:
    lang_name = LANG_NAMES.get(lang, "English")
    return _invoke(SUMMARIZE_MODEL,
        "Explain this Indian government scheme in " + lang_name + ". Max 100 words. Focus on benefits.",
        json.dumps(scheme), max_tokens=350)

def rerank_schemes(schemes: list, user_profile: dict, query: str) -> list:
    if len(schemes) <= 1:
        return schemes
    subset = [{"id": s["scheme_id"], "name": s["name_en"]} for s in schemes[:6]]
    raw = _invoke(INTENT_MODEL,
        "Rank these schemes for the user. Return ONLY a JSON list of IDs.",
        f"Query: {query}\nUser: {json.dumps(user_profile)}\nSchemes: {json.dumps(subset)}",
        max_tokens=200, temperature=0)
    try:
        m = re.search(r'\[.*\]', raw, re.DOTALL)
        order = json.loads(m.group() if m else raw)
        id_map = {s["scheme_id"]: s for s in schemes}
        return [id_map[i] for i in order if i in id_map] + [s for s in schemes if s["scheme_id"] not in order]
    except Exception:
        return schemes

def get_legal_advice(query: str, lang: str = "en") -> str:
    lang_name = LANG_NAMES.get(lang, "English")
    return _invoke(SUMMARIZE_MODEL,
        "You are Saarthi Legal Assistant. Respond in " + lang_name + " with HTML. "
        "Cover: Topic, Relevant Indian Law, Steps, Helpline. "
        "End: 'This is for awareness, not legal advice.'",
        query, max_tokens=800)

def detect_legal_query(text: str) -> str | None:
    kws = ["law","court","police","fir","legal","advocate","crime",
           "divorce","zameen","property","kanoon","vakeel","case"]
    tl = text.lower()
    for k in kws:
        if k in tl: return k
    return None

def explain_recommendation(scheme: dict, user_profile: dict, lang: str = "en") -> str:
    lang_name = LANG_NAMES.get(lang, "English")
    return _invoke(SUMMARIZE_MODEL,
        "In " + lang_name + ", explain why this scheme suits the user. Max 80 words. "
        "Tell them to apply via our portal.",
        f"Scheme: {scheme.get('name_en')}\nProfile: {json.dumps(user_profile)}",
        max_tokens=400)
