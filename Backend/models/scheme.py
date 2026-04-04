from pydantic import BaseModel
from typing import Optional, List

class UserProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    income: Optional[int] = None
    occupation: Optional[str] = None
    caste: Optional[str] = None
    state: Optional[str] = None

class AIQueryRequest(BaseModel):
    text: str
    lang: Optional[str] = "auto"
    user_profile: Optional[UserProfile] = None

class EligibilityCheckRequest(BaseModel):
    scheme_id: str
    user_profile: UserProfile
