from sqlalchemy.orm import Session
from app.database import Message
from app.models.schemas import MessageCreate


def create_message(message_data: MessageCreate, db: Session) -> Message:
    """Create a new message from contact form"""
    message = Message(
        name=message_data.name,
        email=message_data.email,
        subject=message_data.subject,
        message=message_data.message,
        is_read=0
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_all_messages(db: Session, unread_only: bool = False):
    """Get all messages, optionally filter by unread"""
    query = db.query(Message)
    if unread_only:
        query = query.filter(Message.is_read == 0)
    return query.order_by(Message.created_at.desc()).all()


def get_message_by_id(message_id: int, db: Session):
    """Get a specific message by ID"""
    return db.query(Message).filter(Message.id == message_id).first()


def mark_message_as_read(message_id: int, db: Session):
    """Mark a message as read"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if message:
        message.is_read = 1
        db.commit()
        db.refresh(message)
    return message


def get_unread_count(db: Session) -> int:
    """Get count of unread messages"""
    return db.query(Message).filter(Message.is_read == 0).count()


def delete_message(message_id: int, db: Session):
    """Delete a message"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if message:
        db.delete(message)
        db.commit()
        return True
    return False
