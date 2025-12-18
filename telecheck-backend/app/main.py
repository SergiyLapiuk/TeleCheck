from fastapi import FastAPI
from app.routers import analyze
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
app = FastAPI(
    title="TeleCheck API",
    description="Аналіз шкідливості постів у Telegram-каналах",
    version="0.1.0",
)

app.include_router(analyze.router, prefix="/analyze", tags=["Аналіз"])

app.mount("/static", StaticFiles(directory="C:/Users/Dream Store/Desktop/TeleCheckAI/telecheck-backend/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)