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
