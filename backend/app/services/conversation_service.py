"""Conversation storage and retrieval service using SQLite."""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import structlog

logger = structlog.get_logger()


class ConversationService:
    """Service for managing conversation persistence."""
    
    def __init__(self, db_path: str = "conversations.db"):
        """Initialize the conversation service with SQLite database."""
        self.db_path = Path(db_path)
        self._ensure_initialized = False
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema."""
        if self._ensure_initialized:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_updated 
                ON conversations(updated_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation 
                ON messages(conversation_id, timestamp)
            """)
            
            conn.commit()
            conn.close()
            
            self._ensure_initialized = True
            logger.info("Conversation database initialized", db_path=str(self.db_path))
            
        except Exception as e:
            logger.error("Failed to initialize conversation database", error=str(e))
            raise RuntimeError(f"Database initialization failed: {str(e)}") from e
    
    def create_conversation(self, title: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Create a new conversation and return its ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            metadata_json = json.dumps(metadata or {})
            
            cursor.execute("""
                INSERT INTO conversations (title, created_at, updated_at, message_count, metadata)
                VALUES (?, ?, ?, 0, ?)
            """, (title, now, now, metadata_json))
            
            conversation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info("Created conversation", conversation_id=conversation_id, title=title)
            return conversation_id
            
        except Exception as e:
            logger.error("Failed to create conversation", error=str(e))
            raise
    
    def add_message(self, conversation_id: int, role: str, content: str, 
                   sources: Optional[List[Dict[str, Any]]] = None) -> int:
        """Add a message to a conversation."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            sources_json = json.dumps(sources or [])
            
            # Insert message
            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content, sources, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, role, content, sources_json, now))
            
            message_id = cursor.lastrowid
            
            # Update conversation metadata
            cursor.execute("""
                UPDATE conversations 
                SET updated_at = ?, message_count = message_count + 1
                WHERE id = ?
            """, (now, conversation_id))
            
            conn.commit()
            conn.close()
            
            logger.debug("Added message", conversation_id=conversation_id, message_id=message_id, role=role)
            return message_id
            
        except Exception as e:
            logger.error("Failed to add message", error=str(e), conversation_id=conversation_id)
            raise
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """Get a conversation with all its messages."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get conversation metadata
            cursor.execute("""
                SELECT id, title, created_at, updated_at, message_count, metadata
                FROM conversations WHERE id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None
            
            conversation = {
                "id": row["id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "message_count": row["message_count"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            }
            
            # Get messages
            cursor.execute("""
                SELECT id, role, content, sources, timestamp
                FROM messages WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """, (conversation_id,))
            
            messages = []
            for msg_row in cursor.fetchall():
                messages.append({
                    "id": msg_row["id"],
                    "role": msg_row["role"],
                    "content": msg_row["content"],
                    "sources": json.loads(msg_row["sources"]) if msg_row["sources"] else [],
                    "timestamp": msg_row["timestamp"]
                })
            
            conversation["messages"] = messages
            conn.close()
            
            return conversation
            
        except Exception as e:
            logger.error("Failed to get conversation", error=str(e), conversation_id=conversation_id)
            raise
    
    def list_conversations(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List conversations ordered by most recent."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, created_at, updated_at, message_count, metadata
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    "id": row["id"],
                    "title": row["title"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "message_count": row["message_count"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                })
            
            conn.close()
            return conversations
            
        except Exception as e:
            logger.error("Failed to list conversations", error=str(e))
            raise
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation and all its messages."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if deleted:
                logger.info("Deleted conversation", conversation_id=conversation_id)
            
            return deleted
            
        except Exception as e:
            logger.error("Failed to delete conversation", error=str(e), conversation_id=conversation_id)
            raise
    
    def update_conversation_title(self, conversation_id: int, title: str) -> bool:
        """Update the title of a conversation."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE conversations SET title = ?, updated_at = ?
                WHERE id = ?
            """, (title, datetime.utcnow().isoformat(), conversation_id))
            
            updated = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return updated
            
        except Exception as e:
            logger.error("Failed to update conversation title", error=str(e))
            raise


# Singleton instance
conversation_service = ConversationService()
