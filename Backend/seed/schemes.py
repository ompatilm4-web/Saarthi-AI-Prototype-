from supabase import create_client
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

central_schemes = [
  {
    "name_en": "PM-KISAN Samman Nidhi",
    "name_hi": "पीएम किसान सम्मान निधि",
    "category": "Agriculture",
    "level": "central",
    "ministry": "Ministry of Agriculture",
    "benefit": "₹6,000 per year in 3 installments",
    "eligibility": {"occupation": "farmer", "land": "any"},
    "documents": ["Aadhaar", "Bank Passbook", "Land Records"],
    "apply_url": "https://pmkisan.gov.in",
    "tags": ["farmer", "income support", "kisaan"]
  },
  {
    "name_en": "Ayushman Bharat PM-JAY",
    "name_hi": "आयुष्मान भारत पीएम-जेएवाई",
    "category": "Health",
    "level": "central",
    "ministry": "Ministry of Health",
    "benefit": "₹5 lakh health insurance per family per year",
    "eligibility": {"income_max": 200000, "secc_listed": True},
    "documents": ["Aadhaar", "Ration Card", "SECC document"],
    "apply_url": "https://pmjay.gov.in",
    "tags": ["health", "insurance", "hospital", "treatment"]
  },
  # ... add all 50+ central schemes
]

supabase.table("schemes").upsert(central_schemes, on_conflict="name_en").execute()
print("\u2705 Schemes seeded successfully")
