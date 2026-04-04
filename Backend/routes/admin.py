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
        item = {"scheme_id": scheme_id, "created_at": datetime.utcnow().isoformat(), **scheme.dict()}
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
