from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import uvicorn, os

load_dotenv()

from routes.schemes import router as schemes_router
from routes.ai import router as ai_router
from routes.auth import router as auth_router
from routes.recommendations import router as recommendations_router
from routes.admin import router as admin_router

app = FastAPI(title="Saarthi AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(schemes_router)
app.include_router(ai_router)
app.include_router(auth_router)
app.include_router(recommendations_router)
app.include_router(admin_router)

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return FileResponse(status_code=204)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Saarthi AI API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)), reload=True)
