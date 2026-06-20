"""
App entrypoint. Run locally with:
    uvicorn app.main:app --reload --port 8080
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routers import admin_router, auth_router, chat_router, oauth_router

app = FastAPI(title="Contract Analyst Agent - Frontend")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(admin_router.router)
app.include_router(oauth_router.router)
