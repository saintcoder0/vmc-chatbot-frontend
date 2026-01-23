from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import random
import string

from app.core.config import Settings, get_settings
from app.core.db import get_db
from app.integrations.whatsapp import send_whatsapp_text
from app.services.complaints import create_complaint_from_text, get_complaint_status


class SendMessageRequest(BaseModel):
    to: str
    body: str


class SendComplaintReplyRequest(BaseModel):
    phone: str
    complaint_id: int
    message: str


class SendStatusReplyRequest(BaseModel):
    phone: str
    complaint_id: int


class SendGreetingRequest(BaseModel):
    phone: str
    greeting: str


class SendFallbackRequest(BaseModel):
    phone: str


router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
def verify_webhook(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
    settings: Settings = Depends(get_settings),
):
    """
    Verification endpoint required by WhatsApp Cloud API.
    Meta will call this with hub.* query params.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        # Respond with plain challenge string.
        return Response(content=hub_challenge or "", media_type="text/plain")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed"
    )


@router.post("/send_message")
def send_message(request: SendMessageRequest):
    """
    Endpoint to send a WhatsApp message.
    """
    send_whatsapp_text(request.to, request.body)
    return {"success": True}


@router.post("/send_complaint_reply")
def send_complaint_reply(request: SendComplaintReplyRequest, db: Session = Depends(get_db)):
    """
    Send a reply to a user after they register a complaint.
    """
    reply = (
        "✅ Your complaint has been registered.\n"
        f"Complaint ID: {request.complaint_id}\n"
        f"{request.message}\n"
        f"You can track it anytime by sending: 'status: {request.complaint_id}'."
    )
    send_whatsapp_text(request.phone, reply)
    return {"success": True}


@router.post("/send_status_reply")
def send_status_reply(request: SendStatusReplyRequest, db: Session = Depends(get_db)):
    """
    Send the status of a complaint to the user.
    """
    complaint = get_complaint_status(db, request.complaint_id)
    if not complaint:
        send_whatsapp_text(
            request.phone,
            f"No complaint found with ID {request.complaint_id}. "
            "Please check the ID and try again.",
        )
        return {"success": False, "error": "Complaint not found"}

    reply = (
        f"📄 Complaint ID: {complaint.id}\n"
        f"Status: {complaint.status.value}\n"
        f"Category: {complaint.category.value}\n"
        f"Description: {complaint.description}"
    )
    send_whatsapp_text(request.phone, reply)
    return {"success": True}


@router.post("/send_greeting")
def send_greeting(request: SendGreetingRequest):
    """
    Send a greeting/slang reply to the user.
    """
    slang_replies = ["yo", "sup", "hey", "hiya", "yo!", "what's up"]
    reply = random.choice(slang_replies)
    send_whatsapp_text(request.phone, reply)
    return {"success": True}


@router.post("/send_fallback")
def send_fallback(request: SendFallbackRequest):
    """
    Send a fallback/help message to the user.
    """
    reply = (
        "I'm your VMC WhatsApp assistant.\n"
        "Ask me about garbage collection, water supply, tax, or send 'complaint' to register an issue."
    )
    send_whatsapp_text(request.phone, reply)
    return {"success": True}


@router.post("/send_format_error")
def send_format_error(request: SendMessageRequest):
    """
    Send a format error message when user sends wrong format.
    """
    reply = "Please send status in this format: 'status: <complaint_id>'."
    send_whatsapp_text(request.to, reply)
    return {"success": True}


@router.post("/webhook")
async def receive_message(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Incoming message webhook from WhatsApp Cloud API.
    Minimal parsing to extract text messages and respond.
    """
    payload = await request.json()

    entry_list = payload.get("entry", [])
    for entry in entry_list:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            for message in messages:
                if message.get("type") != "text":
                    continue
                from_number = message.get("from")
                text = message.get("text", {}).get("body", "")
                if not (from_number and text):
                    continue

                lower = text.lower().strip()

                # 1) New complaint
                if lower.startswith("complaint:"):
                    complaint = create_complaint_from_text(db, from_number, text)
                    reply = (
                        "✅ Your complaint has been registered.\n"
                        f"Complaint ID: {complaint.id}\n"
                        f"Category: {complaint.category.value}\n"
                        "You can track it anytime by sending: "
                        f"'status: {complaint.id}'."
                    )
                    send_whatsapp_text(from_number, reply)
                    continue

                # 2) Status check
                if lower.startswith("status:"):
                    try:
                        cid_str = text.split(":", 1)[1].strip()
                        cid = int(cid_str)
                    except Exception:
                        send_whatsapp_text(
                            from_number,
                            "Please send status in this format: 'status: <complaint_id>'.",
                        )
                        continue

                    complaint = get_complaint_status(db, cid)
                    if not complaint:
                        send_whatsapp_text(
                            from_number,
                            f"No complaint found with ID {cid}. "
                            "Please check the ID and try again.",
                        )
                        continue

                    reply = (
                        f"📄 Complaint ID: {complaint.id}\n"
                        f"Status: {complaint.status.value}\n"
                        f"Category: {complaint.category.value}\n"
                        f"Description: {complaint.description}"
                    )
                    send_whatsapp_text(from_number, reply)
                    continue

                # 3) Get command
                if lower.startswith("get/"):
                    reply = "Get command received. System status: OK."
                    send_whatsapp_text(from_number, reply)
                    continue

                # 4) Fallback to generic chatbot
                # 3a) Simple greetings -> slang reply (short single-phrase)
                first_word = (text.lower().strip().split() or [""])[0].strip(string.punctuation)
                if first_word in {"hi", "hello", "hey", "yo", "hiya", "sup"}:
                    slang_replies = ["yo", "sup", "hey", "hiya", "yo!"]
                    send_whatsapp_text(from_number, random.choice(slang_replies))
                    continue

                # 3b) Fallback reply
                reply = (
                    "I'm your VMC WhatsApp assistant.\n"
                    "Ask me about garbage collection, water supply, tax, or send 'complaint' to register an issue."
                )
                send_whatsapp_text(from_number, reply)

    # WhatsApp expects a 200 OK quickly.
    return {"success": True}


    # Fallback root router: expose same handlers at `/webhook` for gateways
    # or dashboard callback URLs that expect the webhook at the root path.
    root_router = APIRouter()
    root_router.add_api_route("/webhook", verify_webhook, methods=["GET"]) 
    root_router.add_api_route("/webhook", receive_message, methods=["POST"]) 

