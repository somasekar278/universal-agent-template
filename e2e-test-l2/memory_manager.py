"""
Memory Manager for e2e-test-l2

Handles conversation history using Lakebase (Databricks PostgreSQL).
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from databricks_agent_toolkit.integrations import Lakebase
    LAKEBASE_AVAILABLE = True
except ImportError:
    LAKEBASE_AVAILABLE = False
    print("⚠️  Lakebase integration not available. Install with: pip install databricks-agent-toolkit[databricks]")


class MemoryManager:
    """
    Manages conversation memory using Lakebase (PostgreSQL).
    
    Features:
    - Persistent conversation history
    - Session-based memory
    - Automatic table creation
    - Context window management
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        max_history: int = 20
    ):
        """
        Initialize memory manager.
        
        Args:
            host: Lakebase host (or LAKEBASE_HOST env var)
            database: Database name (or LAKEBASE_DATABASE env var)
            user: Username (or LAKEBASE_USER env var)
            password: Password (or LAKEBASE_PASSWORD env var)
            max_history: Maximum number of messages to keep in context
        """
        if not LAKEBASE_AVAILABLE:
            raise ImportError(
                "Lakebase integration required for assistant. "
                "Install with: pip install databricks-agent-toolkit[databricks]"
            )
        
        self.lakebase = Lakebase(
            host=host,
            database=database,
            user=user,
            password=password
        )
        self.max_history = max_history
        self._initialized = False
    
    def initialize(self):
        """Initialize database table (run once)."""
        if self._initialized:
            return
        
        try:
            self.lakebase.create_conversations_table()
            self._initialized = True
            print("✅ Memory initialized")
        except Exception as e:
            print(f"⚠️  Could not initialize memory: {e}")
            print("   Conversation history will not be saved")
    
    def store_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store a message in conversation history.
        
        Args:
            session_id: Unique session identifier
            role: "user" or "assistant"
            content: Message content
            metadata: Optional metadata (e.g., model, tokens)
        """
        try:
            self.lakebase.store_message(
                session_id=session_id,
                role=role,
                content=content,
                metadata=metadata
            )
        except Exception as e:
            print(f"⚠️  Could not store message: {e}")
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Max messages to return (defaults to max_history)
        
        Returns:
            List of messages in chronological order
        """
        try:
            limit = limit or self.max_history
            return self.lakebase.get_conversation_history(
                session_id=session_id,
                limit=limit
            )
        except Exception as e:
            print(f"⚠️  Could not retrieve history: {e}")
            return []
    
    def get_messages_for_llm(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for LLM chat API.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of messages in format: [{"role": "user", "content": "..."}]
        """
        history = self.get_conversation_history(session_id)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]
    
    def clear_conversation(self, session_id: str):
        """
        Clear all messages for a session.
        
        Args:
            session_id: Session identifier
        """
        try:
            self.lakebase.clear_conversation(session_id)
            print(f"✅ Cleared conversation: {session_id}")
        except Exception as e:
            print(f"⚠️  Could not clear conversation: {e}")
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dictionary with message count, first/last message times
        """
        try:
            history = self.get_conversation_history(session_id)
            if not history:
                return {
                    "message_count": 0,
                    "first_message": None,
                    "last_message": None
                }
            
            return {
                "message_count": len(history),
                "first_message": history[0]["timestamp"],
                "last_message": history[-1]["timestamp"]
            }
        except Exception as e:
            print(f"⚠️  Could not get session summary: {e}")
            return {"message_count": 0, "first_message": None, "last_message": None}
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'lakebase'):
            self.lakebase.close()