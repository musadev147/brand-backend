from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, WebSocket
from datetime import datetime, timezone
import json

from app.models.chat import ChatThread, ChatMessage, ContractStatus
from app.models.user import User
from app.schemas.chat import ChatThreadCreate, ChatMessageSend, ContractSend

class ConnectionManager:
    def __init__(self):
        # Maps user_id (int) to list of active WebSockets
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()

def create_chat_thread(db: Session, client_id: int, schema: ChatThreadCreate) -> ChatThread:
    # Check if thread already exists for client & creator under this campaign or gig
    query = db.query(ChatThread).filter(
        ChatThread.client_user_id == client_id,
        ChatThread.creator_user_id == schema.creator_user_id
    )
    if schema.campaign_id:
        query = query.filter(ChatThread.campaign_id == schema.campaign_id)
    if schema.gig_id:
        query = query.filter(ChatThread.gig_id == schema.gig_id)
        
    existing = query.first()
    if existing:
        return existing
        
    # Generate unique key
    import uuid
    chat_key = f"t_{uuid.uuid4().hex[:10]}"
    
    thread = ChatThread(
        chat_key=chat_key,
        client_user_id=client_id,
        creator_user_id=schema.creator_user_id,
        campaign_id=schema.campaign_id,
        gig_id=schema.gig_id
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread

def get_user_threads(db: Session, user_id: int) -> List[ChatThread]:
    return db.query(ChatThread).filter(
        (ChatThread.client_user_id == user_id) | (ChatThread.creator_user_id == user_id)
    ).order_by(ChatThread.last_message_at.desc().nullslast()).all()

def get_thread_messages(db: Session, thread_id: int, page: int = 1, limit: int = 50) -> List[ChatMessage]:
    offset = (page - 1) * limit
    return db.query(ChatMessage).filter(
        ChatMessage.chat_thread_id == thread_id
    ).order_by(ChatMessage.created_at.asc()).offset(offset).limit(limit).all()

async def send_message(db: Session, sender: User, schema: ChatMessageSend) -> ChatMessage:
    thread = db.query(ChatThread).filter(ChatThread.id == schema.thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="থ্রেড পাওয়া যায়নি (Thread not found)")
        
    if sender.id not in [thread.client_user_id, thread.creator_user_id]:
        raise HTTPException(status_code=403, detail="আপনি এই চ্যাটের সদস্য নন (Not member of this chat)")
        
    role = "client" if sender.id == thread.client_user_id else "creator"
    
    message = ChatMessage(
        chat_thread_id=schema.thread_id,
        sender_user_id=sender.id,
        sender_role=role,
        text=schema.text,
        is_contract=False
    )
    
    thread.last_message_at = datetime.now(timezone.utc)
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Broadcast to recipient in real-time
    recipient_id = thread.creator_user_id if sender.id == thread.client_user_id else thread.client_user_id
    from app.schemas.chat import ChatMessageResponse
    msg_data = ChatMessageResponse.model_validate(message).model_dump(mode="json")
    
    await manager.broadcast_to_user(recipient_id, {"event": "message", "data": msg_data})
    
    return message

async def send_contract(db: Session, sender: User, schema: ContractSend) -> ChatMessage:
    thread = db.query(ChatThread).filter(ChatThread.id == schema.thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="থ্রেড পাওয়া যায়নি (Thread not found)")
        
    if sender.id != thread.client_user_id:
        raise HTTPException(status_code=403, detail="শুধুমাত্র ক্লায়েন্টরা চুক্তি প্রস্তাব পাঠাতে পারেন (Only clients can send contract offers)")
        
    message = ChatMessage(
        chat_thread_id=schema.thread_id,
        sender_user_id=sender.id,
        sender_role="client",
        text=f"📋 Contract Proposed: {schema.contract_title} - ${schema.contract_budget}",
        is_contract=True,
        contract_title=schema.contract_title,
        contract_budget=schema.contract_budget,
        contract_deadline=schema.contract_deadline,
        contract_status=ContractStatus.PENDING
    )
    
    thread.last_message_at = datetime.now(timezone.utc)
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Broadcast to creator
    from app.schemas.chat import ChatMessageResponse
    msg_data = ChatMessageResponse.model_validate(message).model_dump(mode="json")
    await manager.broadcast_to_user(thread.creator_user_id, {"event": "contract", "data": msg_data})
    
    return message

async def respond_to_contract(db: Session, user: User, message_id: int, new_status: ContractStatus) -> ChatMessage:
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id, ChatMessage.is_contract == True).first()
    if not message:
        raise HTTPException(status_code=404, detail="চুক্তির মেসেজটি পাওয়া যায়নি (Contract message not found)")
        
    thread = db.query(ChatThread).filter(ChatThread.id == message.chat_thread_id).first()
    
    # Check permissions
    if new_status in [ContractStatus.ACCEPTED, ContractStatus.REJECTED]:
        # Creators respond to client proposals
        if user.id != thread.creator_user_id:
            raise HTTPException(status_code=403, detail="শুধুমাত্র ক্রিয়েটর এই চুক্তি প্রস্তাব গ্রহণ বা বাতিল করতে পারেন (Only creator can accept/reject)")
    elif new_status == ContractStatus.PAID:
        # Clients pay to activate the escrow/contract
        if user.id != thread.client_user_id:
            raise HTTPException(status_code=403, detail="শুধুমাত্র ক্লায়েন্ট পেমেন্ট করতে পারেন (Only client can pay)")
            
    message.contract_status = new_status
    db.commit()
    db.refresh(message)
    
    # Broadcast to other party
    other_party_id = thread.client_user_id if user.id == thread.creator_user_id else thread.creator_user_id
    from app.schemas.chat import ChatMessageResponse
    msg_data = ChatMessageResponse.model_validate(message).model_dump(mode="json")
    await manager.broadcast_to_user(other_party_id, {"event": "contract_updated", "data": msg_data})
    
    return message

def star_thread(db: Session, user_id: int, thread_id: int) -> ChatThread:
    thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="থ্রেড পাওয়া যায়নি (Thread not found)")
        
    if user_id == thread.client_user_id:
        thread.is_starred_by_client = not thread.is_starred_by_client
    elif user_id == thread.creator_user_id:
        thread.is_starred_by_creator = not thread.is_starred_by_creator
    else:
        raise HTTPException(status_code=403, detail="অ্যাকশনটি অনুমোদিত নয় (Unauthorized)")
        
    db.commit()
    db.refresh(thread)
    return thread
