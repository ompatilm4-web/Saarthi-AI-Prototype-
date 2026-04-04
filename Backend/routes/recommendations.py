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

@router.post("/for-user")
async def get_recommendations_for_user(req: RecommendRequest):
    """
    Smart recommendations based on user occupation and profile.
    Farmers get agriculture schemes, students get education schemes, etc.
    """
    try:
        occupation = req.user_profile.get("occupation", "").lower()

        # Map occupation to priority categories
        OCCUPATION_CATEGORY_PRIORITY = {
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

        priority_cats = OCCUPATION_CATEGORY_PRIORITY.get(occupation, [])

        # Fetch schemes from priority categories first
        if priority_cats:
            schemes = []
            for cat in priority_cats:
                cat_schemes = get_schemes_by_category(cat)
                schemes.extend(cat_schemes)
            # Remove duplicates
            seen = set()
            unique_schemes = []
            for s in schemes:
                sid = s.get("scheme_id")
                if sid and sid not in seen:
                    seen.add(sid)
                    unique_schemes.append(s)
            schemes = unique_schemes
        else:
            schemes = get_all_schemes()

        if not schemes:
            # Fallback to all schemes from Bedrock
            schemes = get_all_schemes()

        if not schemes:
            return {"success": True, "total": 0, "recommendations": [], "message": "No schemes found."}

        results = engine.recommend(
            user_profile=req.user_profile,
            all_schemes=schemes,
            query_intent=req.query_intent,
            top_n=req.top_n,
            use_llm_rerank=False,  # faster, no LLM reranking
            lang=req.lang,
        )

        return {
            "success": True,
            "total": len(results),
            "recommendations": results,
            "occupation": occupation,
            "message": f"{len(results)} schemes matched to your profile.",
        }
    except Exception as e:
        logger.error(f"For-user recommendation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))