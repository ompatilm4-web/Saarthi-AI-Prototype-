import boto3
import json
import os

bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("BEDROCK_REGION", "us-east-1"))

def extract_form_fields(document_text: str) -> dict:
    prompt = f"""Extract the following fields from this document and return as JSON only:
    name, father_name, mother_name, date_of_birth, aadhaar_number, mobile,
    address, pincode, state, district, income, caste, bank_account, ifsc.
    
    Document text:
    {document_text}
    
    Return only valid JSON. Use null for missing fields."""

    response = bedrock.invoke_model(
        modelId=os.getenv("BEDROCK_SUMMARIZE_MODEL", "amazon.nova-pro-v1:0"),
        body=json.dumps({
            "messages": [{"role": "user", "content": [{"text": prompt}]}]
        })
    )
    result_text = json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]
    return json.loads(result_text)
