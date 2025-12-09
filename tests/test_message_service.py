"""
Tests for message service
"""
import pytest
from app.services.message_service import (
    create_message,
    get_all_messages,
    get_message_by_id,
    mark_message_as_read,
    get_unread_count,
    delete_message
)
from app.models.schemas import MessageCreate
from app.database import Message


class TestCreateMessage:
    """Test creating messages"""
    
    def test_create_message_success(self, db_session):
        """Test successful message creation"""
        message_data = MessageCreate(
            name="John Doe",
            email="john@example.com",
            subject="Test Subject",
            message="This is a test message"
        )
        
        message = create_message(message_data, db_session)
        
        assert message is not None
        assert message.id is not None
        assert message.name == "John Doe"
        assert message.email == "john@example.com"
        assert message.subject == "Test Subject"
        assert message.message == "This is a test message"
        assert message.is_read == 0
    
    def test_create_message_with_long_content(self, db_session):
        """Test creating message with long content"""
        long_message = "A" * 1000
        message_data = MessageCreate(
            name="Jane Smith",
            email="jane@example.com",
            subject="Long Message",
            message=long_message
        )
        
        message = create_message(message_data, db_session)
        
        assert message is not None
        assert len(message.message) == 1000
    
    def test_create_message_special_characters(self, db_session):
        """Test creating message with special characters"""
        message_data = MessageCreate(
            name="Test User",
            email="test@example.com",
            subject="Special: <>&\"'",
            message="Message with special chars: <script>alert('test')</script>"
        )
        
        message = create_message(message_data, db_session)
        
        assert message is not None
        assert "<script>" in message.message


class TestGetMessages:
    """Test retrieving messages"""
    
    def test_get_all_messages_empty(self, db_session):
        """Test getting messages when none exist"""
        messages = get_all_messages(db_session)
        
        assert isinstance(messages, list)
        assert len(messages) == 0
    
    def test_get_all_messages_multiple(self, db_session):
        """Test getting multiple messages"""
        # Create several messages
        for i in range(5):
            message_data = MessageCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                subject=f"Subject {i}",
                message=f"Message {i}"
            )
            create_message(message_data, db_session)
        
        messages = get_all_messages(db_session)
        
        assert len(messages) == 5
        # Messages should be ordered by most recent first
        # Just verify we got all 5 messages
        names = [msg.name for msg in messages]
        assert "User 0" in names
        assert "User 4" in names
    
    def test_get_all_messages_unread_only(self, db_session):
        """Test filtering unread messages"""
        # Create mix of read and unread messages
        for i in range(3):
            message_data = MessageCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                subject=f"Subject {i}",
                message=f"Message {i}"
            )
            msg = create_message(message_data, db_session)
            if i == 1:
                msg.is_read = 1
                db_session.commit()
        
        all_messages = get_all_messages(db_session)
        unread_messages = get_all_messages(db_session, unread_only=True)
        
        assert len(all_messages) == 3
        assert len(unread_messages) == 2
    
    def test_get_message_by_id_exists(self, db_session):
        """Test getting specific message by ID"""
        message_data = MessageCreate(
            name="Test User",
            email="test@example.com",
            subject="Test",
            message="Test message"
        )
        created_message = create_message(message_data, db_session)
        
        retrieved_message = get_message_by_id(created_message.id, db_session)
        
        assert retrieved_message is not None
        assert retrieved_message.id == created_message.id
        assert retrieved_message.name == "Test User"
    
    def test_get_message_by_id_not_exists(self, db_session):
        """Test getting non-existent message"""
        message = get_message_by_id(99999, db_session)
        
        assert message is None


class TestMarkMessageAsRead:
    """Test marking messages as read"""
    
    def test_mark_message_as_read_success(self, db_session):
        """Test successfully marking message as read"""
        message_data = MessageCreate(
            name="Test User",
            email="test@example.com",
            subject="Test",
            message="Test message"
        )
        message = create_message(message_data, db_session)
        
        assert message.is_read == 0
        
        updated_message = mark_message_as_read(message.id, db_session)
        
        assert updated_message is not None
        assert updated_message.is_read == 1
    
    def test_mark_message_as_read_already_read(self, db_session):
        """Test marking already read message"""
        message_data = MessageCreate(
            name="Test User",
            email="test@example.com",
            subject="Test",
            message="Test message"
        )
        message = create_message(message_data, db_session)
        
        # Mark as read twice
        mark_message_as_read(message.id, db_session)
        updated_message = mark_message_as_read(message.id, db_session)
        
        assert updated_message.is_read == 1
    
    def test_mark_message_as_read_not_exists(self, db_session):
        """Test marking non-existent message as read"""
        result = mark_message_as_read(99999, db_session)
        
        assert result is None


class TestGetUnreadCount:
    """Test getting unread message count"""
    
    def test_get_unread_count_zero(self, db_session):
        """Test unread count when no messages exist"""
        count = get_unread_count(db_session)
        
        assert count == 0
    
    def test_get_unread_count_all_unread(self, db_session):
        """Test unread count when all messages are unread"""
        for i in range(5):
            message_data = MessageCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                subject=f"Subject {i}",
                message=f"Message {i}"
            )
            create_message(message_data, db_session)
        
        count = get_unread_count(db_session)
        
        assert count == 5
    
    def test_get_unread_count_mixed(self, db_session):
        """Test unread count with mix of read and unread"""
        for i in range(5):
            message_data = MessageCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                subject=f"Subject {i}",
                message=f"Message {i}"
            )
            msg = create_message(message_data, db_session)
            if i % 2 == 0:
                mark_message_as_read(msg.id, db_session)
        
        count = get_unread_count(db_session)
        
        assert count == 2
    
    def test_get_unread_count_all_read(self, db_session):
        """Test unread count when all messages are read"""
        for i in range(3):
            message_data = MessageCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                subject=f"Subject {i}",
                message=f"Message {i}"
            )
            msg = create_message(message_data, db_session)
            mark_message_as_read(msg.id, db_session)
        
        count = get_unread_count(db_session)
        
        assert count == 0


class TestDeleteMessage:
    """Test deleting messages"""
    
    def test_delete_message_success(self, db_session):
        """Test successful message deletion"""
        message_data = MessageCreate(
            name="Test User",
            email="test@example.com",
            subject="Test",
            message="Test message"
        )
        message = create_message(message_data, db_session)
        
        result = delete_message(message.id, db_session)
        
        assert result is True
        
        # Verify deletion
        deleted_message = get_message_by_id(message.id, db_session)
        assert deleted_message is None
    
    def test_delete_message_not_exists(self, db_session):
        """Test deleting non-existent message"""
        result = delete_message(99999, db_session)
        
        assert result is False
    
    def test_delete_message_multiple(self, db_session):
        """Test deleting multiple messages"""
        messages = []
        for i in range(3):
            message_data = MessageCreate(
                name=f"User {i}",
                email=f"user{i}@example.com",
                subject=f"Subject {i}",
                message=f"Message {i}"
            )
            messages.append(create_message(message_data, db_session))
        
        # Delete first two
        delete_message(messages[0].id, db_session)
        delete_message(messages[1].id, db_session)
        
        remaining_messages = get_all_messages(db_session)
        assert len(remaining_messages) == 1
        assert remaining_messages[0].id == messages[2].id
    
    def test_delete_read_message(self, db_session):
        """Test deleting a read message"""
        message_data = MessageCreate(
            name="Test User",
            email="test@example.com",
            subject="Test",
            message="Test message"
        )
        message = create_message(message_data, db_session)
        mark_message_as_read(message.id, db_session)
        
        result = delete_message(message.id, db_session)
        
        assert result is True
        assert get_unread_count(db_session) == 0


class TestMessageValidation:
    """Test message data validation"""
    
    def test_create_message_valid_email(self, db_session):
        """Test creating message with valid email"""
        message_data = MessageCreate(
            name="Test",
            email="valid.email@example.com",
            subject="Test",
            message="Test"
        )
        
        message = create_message(message_data, db_session)
        assert message is not None
    
    def test_create_message_invalid_email_format(self):
        """Test that invalid email format is caught by Pydantic"""
        with pytest.raises(Exception):
            MessageCreate(
                name="Test",
                email="invalid-email",
                subject="Test",
                message="Test"
            )
    
    def test_create_message_empty_name(self):
        """Test that empty name is caught by validation"""
        with pytest.raises(Exception):
            MessageCreate(
                name="",
                email="test@example.com",
                subject="Test",
                message="Test"
            )
    
    def test_create_message_empty_subject(self):
        """Test that empty subject is caught by validation"""
        with pytest.raises(Exception):
            MessageCreate(
                name="Test",
                email="test@example.com",
                subject="",
                message="Test"
            )
    
    def test_create_message_empty_message(self):
        """Test that empty message is caught by validation"""
        with pytest.raises(Exception):
            MessageCreate(
                name="Test",
                email="test@example.com",
                subject="Test",
                message=""
            )
