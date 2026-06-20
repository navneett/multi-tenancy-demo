"""
Customer-facing chat routes.

GET  /chat       -> serves the chat UI (also surfaces a Drive connect button)
POST /api/chat   -> proxies a message to the deployed agent, scoped to the
                    CURRENT verified user only

Every call here goes through Depends(get_current_user) - there is no path
in this router that accepts a customer/tenant identifier from the request
body. The only identity in play is the one FastAPI resolved from the
session cookie.
"""

import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ..agent_client import ask_agent
from ..auth import CurrentUser, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/chat")
async def chat_page(request: Request, user: CurrentUser = Depends(get_current_user)):
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "user_email": user.email},
    )


class ChatMessage(BaseModel):
    message: str
    session_id: str | None = None


@router.post("/api/chat")
async def post_chat(
    body: ChatMessage,
    user: CurrentUser = Depends(get_current_user),
):
    """Streams the agent's response back to the browser as newline-delimited JSON.

    `user` is injected by FastAPI from the verified session cookie - it is
    NOT constructed from anything in `body`. This is the structural
    enforcement point for tenant isolation on the frontend side: even if a
    malicious client sent {"user_id": "customerB-bob"} in the request body,
    there's no code path here that reads it.
    """

    async def event_stream():
        async for event in ask_agent(user, body.message, body.session_id):
            yield json.dumps(event) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")
