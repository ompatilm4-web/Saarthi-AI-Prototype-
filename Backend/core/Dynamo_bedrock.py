import os
import json
import uuid
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime

AWS_REGION     = os.getenv("AWS_REGION", "ap-south-1")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

schemes_table = dynamodb.Table(os.getenv("DYNAMODB_TABLE_SCHEMES", "Schemes"))
queries_table = dynamodb.Table(os.getenv("DYNAMODB_TABLE_QUERIES", "UserQueries"))
users_table   = dynamodb.Table(os.getenv("DYNAMODB_TABLE_USERS", "Users"))
apps_table    = dynamodb.Table(os.getenv("DYNAMODB_TABLE_APPLICATIONS", "Applications"))

_INFERENCE_PROFILE_MAP = {
    "amazon.nova-pro-v1:0":   "us.amazon.nova-pro-v1:0",
    "amazon.nova-lite-v1:0":  "us.amazon.nova-lite-v1:0",
    "amazon.nova-micro-v1:0": "us.amazon.nova-micro-v1:0",
}

def _resolve_model_id(model_id: str) -> str:
    return _INFERENCE_PROFILE_MAP.get(model_id, model_id)

SCHEME_MODEL = _resolve_model_id(os.getenv("BEDROCK_SCHEME_MODEL", "us.amazon.nova-pro-v1:0"))

SCHEME_PROMPT = """You are an expert on Indian government schemes.
Return a JSON array of matching schemes.
STRICT JSON RULES:
- Return ONLY a raw JSON array — no markdown fences.
- Return maximum 5 schemes.
Fields: scheme_id, name_en, name_hi, category, state, description, benefits (amount), apply_url, is_active (bool), eligibility (age_min, income_max)."""

def sanitize_item(item):
    if isinstance(item, list):
        return [sanitize_item(i) for i in item]
    if isinstance(item, dict):
        return {k: sanitize_item(v) for k, v in item.items()}
    if isinstance(item, decimal.Decimal):
        return int(item) if item % 1 == 0 else float(item)
    return item

def save_schemes_to_dynamo(schemes: list, source_query: str = ""):
    for scheme in schemes:
        try:
            item = dict(scheme)
            if source_query:
                item["source_query"] = source_query.lower().strip()
            schemes_table.put_item(Item=item)
        except Exception as e:
            print(f"[DynamoDB Save Error]: {e}")

def _repair_json(raw: str) -> str:
    raw = raw.strip()
    if not raw.startswith("["):
        raw = ("[" + raw) if raw.startswith("{") else raw
    depth, last_ok, in_str, esc = 0, -1, False, False
    for i, ch in enumerate(raw):
        if esc:            esc = False; continue
        if ch == "\\":     esc = True;  continue
        if ch == '"':      in_str = not in_str; continue
        if in_str:         continue
        if   ch == "{":    depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: last_ok = i
    if last_ok == -1: return raw
    return raw[:last_ok + 1].rstrip(", \n\r") + "\n]"

def fetch_schemes_from_bedrock(query: str, category: str = None, keywords: list = None) -> list:
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
            save_schemes_to_dynamo(schemes, source_query=search_query)
        return schemes if isinstance(schemes, list) else []
    except Exception as e:
        print(f"[Bedrock Fetch Error]: {e}")
        return []

def get_scheme_by_id(scheme_id: str):
    try:
        response = schemes_table.get_item(Key={"scheme_id": scheme_id})
        item = response.get("Item")
        if item: return sanitize_item(item)
    except Exception: pass
    schemes = fetch_schemes_from_bedrock(scheme_id)
    return schemes[0] if schemes else None

def get_schemes_by_category(category: str, state: str = None):
    try:
        if state and state != "central":
            response = schemes_table.query(
                IndexName="category-state-index",
                KeyConditionExpression=Key("category").eq(category) & Key("state").eq(state),
                FilterExpression=Attr("is_active").eq(True),
            )
        else:
            response = schemes_table.query(
                IndexName="category-state-index",
                KeyConditionExpression=Key("category").eq(category),
                FilterExpression=Attr("is_active").eq(True),
            )
        items = response.get("Items", [])
        if items: return sanitize_item(items)
    except Exception: pass
    return [sanitize_item(s) for s in fetch_schemes_from_bedrock(category, category=category)]

def get_all_schemes():
    try:
        response = schemes_table.scan(FilterExpression=Attr("is_active").eq(True))
        items = response.get("Items", [])
        if items: return sanitize_item(items)
    except Exception: pass
    return fetch_schemes_from_bedrock("popular government welfare schemes")

def search_schemes_by_keyword(keyword: str):
    kl = keyword.lower().strip()
    kt = keyword.title().strip()
    try:
        filter_exp = Attr("is_active").eq(True) & (
            Attr("name_en").contains(keyword) |
            Attr("name_en").contains(kl) |
            Attr("name_en").contains(kt) |
            Attr("name_hi").contains(keyword) |
            Attr("description").contains(keyword) |
            Attr("description").contains(kl)
        )
        response = schemes_table.scan(FilterExpression=filter_exp)
        items = response.get("Items", [])
        if items:
            def _score(s: dict) -> int:
                name = s.get("name_en", "").lower()
                name_hi = s.get("name_hi", "").lower()
                desc = s.get("description", "").lower()
                score = 0
                if name.strip() == kl or name_hi.strip() == kl:
                    score += 50
                elif f" {kl} " in f" {name} ":
                    score += 30
                elif kl in name or kl in name_hi:
                    score += 15
                if kl in desc:
                    score += 5
                if kl in s.get("category", "").lower():
                    score += 8
                return score
            scored_items = sorted(items, key=_score, reverse=True)
            relevant = [s for s in scored_items if _score(s) > 0]
            return sanitize_item(relevant if relevant else scored_items[:3])
    except Exception as e:
        print(f"[DynamoDB Scan Error]: {e}")
    return [sanitize_item(s) for s in fetch_schemes_from_bedrock(keyword, keywords=[keyword])]

def check_eligibility(scheme: dict, user_profile: dict) -> bool:
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

def log_query(query_id: str, query_text: str, lang: str, intent: str, scheme_ids: list):
    try:
        queries_table.put_item(Item={
            "query_id": query_id, "query_text": query_text,
            "lang_detected": lang, "intent": intent,
            "schemes_returned": scheme_ids, "timestamp": datetime.utcnow().isoformat(),
        })
    except Exception: pass

def create_user(user_id: str, phone: str, name: str = "", profile: dict = {}):
    try:
        users_table.put_item(Item={
            "user_id": user_id, "phone": phone, "name": name,
            "profile": profile, "created_at": datetime.utcnow().isoformat(),
        })
    except Exception: pass

def get_user(user_id: str):
    try:
        response = users_table.get_item(Key={"user_id": user_id})
        return sanitize_item(response.get("Item"))
    except Exception: return None

def submit_application(user_id: str, scheme_id: str, scheme_name: str, user_details: dict = {}):
    application_id = str(uuid.uuid4())
    try:
        apps_table.put_item(Item={
            "application_id": application_id, "user_id": user_id,
            "scheme_id": scheme_id, "scheme_name": scheme_name,
            "status": "submitted", "user_details": user_details,
            "submitted_at": datetime.utcnow().isoformat(),
        })
        return application_id
    except Exception: return None

def get_user_applications(user_id: str):
    try:
        response = apps_table.query(
            IndexName="user-id-index",
            KeyConditionExpression=Key("user_id").eq(user_id),
        )
        return sanitize_item(response.get("Items", []))
    except Exception: return []
