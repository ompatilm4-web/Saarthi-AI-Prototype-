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
        eligible = check_eligibility(scheme, req.user_profile.dict())
    except Exception:
        raise HTTPException(status_code=500, detail="Eligibility check failed")
    return {
        "success": True, "scheme_id": req.scheme_id,
        "eligible": eligible, "scheme_name": scheme.get("name_en"),
        "apply_url": scheme.get("apply_url") if eligible else None,
    }
