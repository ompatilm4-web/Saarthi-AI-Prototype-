import boto3, json, os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("BEDROCK_REGION", "us-east-1"))

class LegalRequest(BaseModel):
    query: str
    lang: str

@router.post("/legal")
async def analyze_legal(req: LegalRequest):
    system_prompt = f"""You are a legal advisor for Indian citizens. Respond in {req.lang} language.
    
    Analyze the user's legal problem and return a JSON with:
    {{
      "issue_type": "Labour Law / Consumer Rights / Property / Criminal / Family / RTI / etc.",
      "applicable_law": "Name of relevant Act",
      "jurisdiction": "Labour Court / Consumer Forum / High Court / Police / etc.",
      "explanation": "Simple explanation of their rights (2-3 sentences)",
      "immediate_steps": ["Step 1", "Step 2", "Step 3"],
      "helplines": [{{"name": "National Legal Aid", "number": "15100"}}],
      "can_file_rti": true,
      "urgency": "low/medium/high"
    }}
    
    Use simple language. Always recommend consulting a lawyer for complex matters."""

    response = bedrock.invoke_model(
        modelId=os.getenv("BEDROCK_SCHEME_MODEL", "amazon.nova-pro-v1:0"),
        body=json.dumps({
            "system": [{"text": system_prompt}],
            "messages": [{"role": "user", "content": [{"text": req.query}]}]
        })
    )
    result = json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]
    return json.loads(result)
