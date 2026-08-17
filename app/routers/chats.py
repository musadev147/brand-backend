from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.utils.security import decode_access_token
from app.schemas.chat import (
    ChatThreadCreate,
    ChatThreadResponse,
    ChatMessageSend,
    ChatMessageResponse,
    ContractSend,
    ContractRespond,
)
from app.services import chat_service
from app.services.chat_service import manager

router = APIRouter(prefix="/chats", tags=["💬 Chat & Messaging"])

@router.get(
    "/threads",
    response_model=List[ChatThreadResponse],
    summary="আমার সব Chat Threads",
    description="লগইন করা ইউজারের সকল সক্রিয় চ্যাট থ্রেডের তালিকা রিটার্ন করে।",
)
def get_my_threads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat_service.get_user_threads(db, current_user.id)

@router.get(
    "/threads/{thread_id}/messages",
    response_model=List[ChatMessageResponse],
    summary="Thread এর Messages",
    description="নির্দিষ্ট চ্যাট থ্রেডের সকল মেসেজ পেজিনেশনসহ রিটার্ন করে।",
)
def get_thread_messages(
    thread_id: int,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify member
    thread = db.query(chat_service.ChatThread).filter(chat_service.ChatThread.id == thread_id).first()
    if not thread or current_user.id not in [thread.client_user_id, thread.creator_user_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="আপনি এই চ্যাটের সদস্য নন (Not member of this chat)",
        )
    return chat_service.get_thread_messages(db, thread_id, page, limit)

@router.post(
    "/threads/create",
    response_model=ChatThreadResponse,
    summary="নতুন Chat শুরু",
    description="ক্রিয়েটরের সাথে নতুন চ্যাট থ্রেড শুরু করে।",
)
def create_thread(
    request: ChatThreadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="শুধুমাত্র ক্লায়েন্টরা চ্যাট শুরু করতে পারেন (Only clients can start threads)",
        )
    return chat_service.create_chat_thread(db, current_user.id, request)

@router.post(
    "/messages/send",
    response_model=ChatMessageResponse,
    summary="মেসেজ পাঠাও",
    description="চ্যাট থ্রেডে মেসেজ পাঠায় এবং রিয়েল-টাইমে রিসিভারের কাছে ব্রডকাস্ট করে।",
)
async def send_new_message(
    request: ChatMessageSend,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await chat_service.send_message(db, current_user, request)

@router.post(
    "/contracts/send",
    response_model=ChatMessageResponse,
    summary="Contract/Escrow Message পাঠাও",
    description="চ্যাট থ্রেডে চুক্তির প্রস্তাব পাঠায়। (শুধুমাত্র ক্লায়েন্ট পাঠাতে পারবে)",
)
async def send_new_contract(
    request: ContractSend,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await chat_service.send_contract(db, current_user, request)

@router.put(
    "/contracts/{message_id}/respond",
    response_model=ChatMessageResponse,
    summary="Contract Accept/Reject/Pay",
    description="চুক্তি প্রস্তাব গ্রহণ, বর্জন অথবা পে করে একটিভ করে।",
)
async def respond_contract(
    message_id: int,
    request: ContractRespond,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await chat_service.respond_to_contract(db, current_user, message_id, request.status)

@router.put(
    "/threads/{thread_id}/star",
    response_model=ChatThreadResponse,
    summary="Star/Unstar Chat",
    description="চ্যাট থ্রেড স্টার করে চিহ্নিত করে।",
)
def toggle_star(
    thread_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat_service.star_thread(db, current_user.id, thread_id)


# ── WebSocket Endpoint ───────────────────────────────────────
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Real-time messaging WebSocket connection.
    Authenticates user using JWT passed as token query parameter: ws://localhost:8000/api/chats/ws?token=<JWT>
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Authenticate user
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id_str = payload.get("sub")
    if not user_id_str:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = int(user_id_str)
    
    # Accept connection and register user
    await manager.connect(user_id, websocket)
    
    try:
        while True:
            # Keep connection alive or listen for direct text/JSON messages from client
            data = await websocket.receive_text()
            try:
                # Handle incoming messages via WebSocket if client prefers
                event_data = json.loads(data)
                if event_data.get("event") == "send_message":
                    payload = event_data.get("data", {})
                    thread_id = payload.get("thread_id")
                    text = payload.get("text")
                    if thread_id and text:
                        # Find sender User
                        sender = db.query(User).filter(User.id == user_id).first()
                        if sender:
                            await chat_service.send_message(
                                db=db, 
                                sender=sender, 
                                schema=ChatMessageSend(thread_id=thread_id, text=text)
                            )
            except Exception:
                # If invalid JSON, ignore or log
                pass
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
