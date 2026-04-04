import os
import boto3
import json
from supabase import create_client
from PIL import Image
import pytesseract

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("BEDROCK_REGION", "us-east-1"))

# Step 1: OCR \u2014 extract text from uploaded document
def extract_text_from_document(file_path: str, lang: str = "hin") -> str:
    image = Image.open(file_path)
    return pytesseract.image_to_string(image, lang=lang)

# Step 2: Chunk the extracted text
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

# Step 3: Generate embeddings via Amazon Bedrock Titan
def get_embedding(text: str) -> list[float]:
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text})
    )
    return json.loads(response["body"].read())["embedding"]

# Step 4: Store chunks in Supabase pgvector
def index_document(user_id: str, doc_id: str, text: str):
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        supabase.table("document_chunks").insert({
            "id": f"{doc_id}_chunk_{i}",
            "user_id": user_id,
            "doc_id": doc_id,
            "content": chunk,
            "embedding": embedding
        }).execute()

# Step 5: Semantic search via Supabase pgvector
def query_rag(user_id: str, user_query: str) -> str:
    query_embedding = get_embedding(user_query)
    result = supabase.rpc("match_documents", {
        "query_embedding": query_embedding,
        "match_count": 5,
        "user_id_filter": user_id
    }).execute()
    return "\n\n".join([row["content"] for row in result.data])

# Step 6: Generate answer using Amazon Bedrock Nova Pro
def generate_answer(context: str, user_query: str, lang: str = "hi") -> str:
    prompt = f"Context from user's documents:\n{context}\n\nUser question (answer in {lang}): {user_query}"
    response = bedrock.invoke_model(
        modelId=os.getenv("BEDROCK_SUMMARIZE_MODEL", "amazon.nova-pro-v1:0"),
        body=json.dumps({
            "messages": [{"role": "user", "content": [{"text": prompt}]}]
        })
    )
    return json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]
