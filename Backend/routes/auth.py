import os, random, time, uuid
from fastapi import APIRouter, HTTPException
from supabase import create_client
from pydantic import BaseModel
from typing import Optional

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

class ProfileUpdate(BaseModel):
    # Supabase column names (exact match required)
    full_name:  Optional[str] = None   # column: full_name
    name:       Optional[str] = None   # column: name (fallback display name)
    age:        Optional[int] = None   # column: age
    gender:     Optional[str] = None   # column: gender
    state:      Optional[str] = None   # column: state
    occupation: Optional[str] = None   # column: occupation
    income:     Optional[int] = None   # column: income
    category:   Optional[str] = None   # column: category
    # These have no dedicated column — stored in profile jsonb
    email:      Optional[str] = None
    aadhaar:    Optional[str] = None

@router.post("/send-otp")
async def send_otp(req: OTPRequest):
    otp = str(random.randint(100000, 999999))
    otp_store[req.mobile] = {"otp": otp, "expires": time.time() + 300}
    print(f"[DEV] OTP for {req.mobile}: {otp}")
    return {"success": True}

@router.put("/profile")
async def update_profile(mobile: str, data: ProfileUpdate):
    if not mobile:
        raise HTTPException(status_code=400, detail="Mobile number required")
    try:
        raw = data.dict()

        # Build payload for direct columns only
        # Supabase schema columns: full_name, name, age, gender, state, occupation, income, category
        direct_cols = ["full_name", "name", "age", "gender", "state", "occupation", "income", "category"]
        payload = {k: v for k, v in raw.items() if k in direct_cols and v is not None}

        # If full_name provided, also set name column (used by some profile reads)
        if payload.get("full_name") and not payload.get("name"):
            payload["name"] = payload["full_name"]

        # Store email + aadhaar inside profile jsonb (no dedicated columns)
        extra = {k: v for k, v in raw.items() if k in ("email", "aadhaar") and v is not None}
        if extra:
            # Fetch existing profile jsonb first so we merge not overwrite
            try:
                existing = supabase.table("users").select("profile").eq("mobile", mobile).single().execute()
                existing_profile = existing.data.get("profile") or {}
            except Exception:
                existing_profile = {}
            payload["profile"] = {**existing_profile, **extra}

        if not payload:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Upsert user row (creates if not exists, updates if exists)
        supabase.table("users").upsert(
            {"mobile": mobile, **payload}, on_conflict="mobile"
        ).execute()

        # Fetch full updated row to return
        result = supabase.table("users").select("*").eq("mobile", mobile).single().execute()
        updated_user = result.data if result.data else {"mobile": mobile, **payload}

        # Flatten profile jsonb fields into user object for frontend
        if updated_user.get("profile"):
            updated_user = {**updated_user, **updated_user["profile"]}

        return {"success": True, "user": updated_user}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Profile Update Error]: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.post("/verify-otp")
async def verify_otp(req: OTPVerify):
    if not DEV_MODE:
        stored = otp_store.get(req.mobile)
        if not stored or stored["otp"] != req.otp or time.time() > stored["expires"]:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        del otp_store[req.mobile]
    else:
        otp_store.pop(req.mobile, None)

    try:
        # Try to fetch existing row first (avoids overwriting data with blank upsert)
        existing = None
        try:
            existing_result = (
                supabase.table("users")
                .select("*")
                .eq("mobile", req.mobile)
                .single()
                .execute()
            )
            existing = existing_result.data
        except Exception:
            existing = None

        if not existing:
            # Row doesn't exist yet — create it
            supabase.table("users").insert({"mobile": req.mobile}).execute()
            fetch_result = (
                supabase.table("users")
                .select("*")
                .eq("mobile", req.mobile)
                .single()
                .execute()
            )
            user = fetch_result.data if fetch_result.data else {"mobile": req.mobile}
        else:
            user = existing

        # Flatten profile jsonb into top-level so frontend gets email, aadhaar etc.
        if user.get("profile"):
            user = {**user, **user["profile"]}

    except Exception as e:
        print(f"[verify-otp DB error]: {e}")
        user = {"mobile": req.mobile, "id": str(uuid.uuid4())}

    token = str(uuid.uuid4())
    return {"success": True, "token": token, "user": user}