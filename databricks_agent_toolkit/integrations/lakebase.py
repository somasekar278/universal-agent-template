"""
Lakebase - Databricks Managed PostgreSQL Integration

Lakebase is Databricks' fully managed PostgreSQL offering, perfect for:
- Conversational memory (chat history, sessions)
- Structured agent data (configurations, user profiles)
- OLTP workloads
- pgvector for embeddings (if needed)

For large-scale RAG/vector search, use DatabricksVectorSearch (Delta Lake-based) instead.

Documentation: https://docs.databricks.com/lakebase/
"""

from typing import List, Dict, Any, Optional
import os

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None
    RealDictCursor = None


class Lakebase:
    """
    Client for Databricks Lakebase (Managed PostgreSQL).
    
    Perfect for agent memory, sessions, and structured data.
    
    Example:
        ```python
        from databricks_agent_toolkit.integrations import Lakebase
        
        # Initialize
        lakebase = Lakebase(
            host="your-lakebase.cloud.databricks.com",
            database="agents",
            user="your_user",
            password="your_password"
        )
        
        # Store conversation
        lakebase.execute(
            \"\"\"
            INSERT INTO conversations (session_id, role, content, timestamp)
            VALUES (%s, %s, %s, NOW())
            \"\"\",
            ("session_123", "user", "Hello!")
        )
        
        # Retrieve conversation history
        history = lakebase.query(
            \"\"\"
            SELECT role, content, timestamp 
            FROM conversations 
            WHERE session_id = %s 
            ORDER BY timestamp
            \"\"\",
            ("session_123",)
        )
        ```
    
    For pgvector integration:
        ```python
        # Enable pgvector extension (one-time)
        lakebase.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Create table with vector column
        lakebase.execute(\"\"\"
            CREATE TABLE embeddings (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding vector(1536)
            )
        \"\"\")
        
        # Vector similarity search
        results = lakebase.query(\"\"\"
            SELECT content, embedding <-> %s AS distance
            FROM embeddings
            ORDER BY distance
            LIMIT 5
        \"\"\", (query_embedding,))
        ```
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 5432,
        sslmode: Optional[str] = None,
        channel_binding: Optional[str] = None
    ):
        """
        Initialize Lakebase (PostgreSQL) connection.
        
        Args:
            host: Lakebase host (env: LAKEBASE_HOST or PGHOST)
            database: Database name (env: LAKEBASE_DATABASE or PGDATABASE)
            user: Username (env: LAKEBASE_USER or PGUSER)
            password: Password (env: LAKEBASE_PASSWORD or PGPASSWORD)
            port: Port (default: 5432)
            sslmode: SSL mode (env: PGSSLMODE) - 'require', 'prefer', etc.
            channel_binding: Channel binding (env: PGCHANNELBINDING) - 'require', 'prefer', 'disable'
        
        Raises:
            ImportError: If psycopg2 is not installed
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "psycopg2 is required for Lakebase integration. "
                "Install with: pip install psycopg2-binary"
            )
        
        # Support both LAKEBASE_* and PG* environment variables
        self.host = host or os.getenv("LAKEBASE_HOST") or os.getenv("PGHOST")
        self.database = database or os.getenv("LAKEBASE_DATABASE") or os.getenv("PGDATABASE")
        self.user = user or os.getenv("LAKEBASE_USER") or os.getenv("PGUSER")
        self.password = password or os.getenv("LAKEBASE_PASSWORD") or os.getenv("PGPASSWORD")
        self.port = port
        self.sslmode = sslmode or os.getenv("PGSSLMODE", "prefer")
        self.channel_binding = channel_binding or os.getenv("PGCHANNELBINDING", "prefer")
        
        if not all([self.host, self.database, self.user, self.password]):
            raise ValueError(
                "Missing Lakebase credentials. Provide via arguments or environment variables:\n"
                "LAKEBASE_HOST/PGHOST, LAKEBASE_DATABASE/PGDATABASE, LAKEBASE_USER/PGUSER, LAKEBASE_PASSWORD/PGPASSWORD"
            )
        
        self.connection = None
    
    def connect(self):
        """Establish connection to Lakebase."""
        if self.connection is None or self.connection.closed:
            # Build connection parameters
            conn_params = {
                "host": self.host,
                "database": self.database,
                "user": self.user,
                "password": self.password,
                "port": self.port,
                "sslmode": self.sslmode,
            }
            
            # Add channel_binding if specified
            # Note: channel_binding support requires psycopg2 2.8+
            if self.channel_binding and self.channel_binding != "prefer":
                # Only set if explicitly required/disabled, not for 'prefer' (default)
                try:
                    conn_params["channel_binding"] = self.channel_binding
                except Exception:
                    # Older psycopg2 versions don't support this parameter
                    pass
            
            self.connection = psycopg2.connect(**conn_params)
            print(f"✅ Connected to Lakebase: {self.host}/{self.database}")
    
    def close(self):
        """Close connection to Lakebase."""
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("✅ Closed Lakebase connection")
    
    def execute(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute a SQL command (INSERT, UPDATE, DELETE, CREATE, etc.).
        
        Args:
            query: SQL query
            params: Query parameters (for parameterized queries)
        
        Returns:
            Number of rows affected
        """
        self.connect()
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
    
    def query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_one: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL SELECT query
            params: Query parameters
            fetch_one: If True, return only first result
        
        Returns:
            List of result dictionaries (or single dict if fetch_one=True)
        """
        self.connect()
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            if fetch_one:
                result = cursor.fetchone()
                return dict(result) if result else None
            return [dict(row) for row in cursor.fetchall()]
    
    def create_conversations_table(self):
        """
        Create a standard conversations table for agent memory.
        
        Schema:
        - session_id: Unique identifier for conversation session
        - role: "user" or "assistant"
        - content: Message content
        - timestamp: When message was sent
        - metadata: Additional data (JSONB)
        """
        self.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW(),
                metadata JSONB
            )
        """)
        
        # Create indexes separately (PostgreSQL syntax)
        try:
            self.execute("CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)")
            self.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)")
        except Exception:
            # Indexes might already exist, that's okay
            pass
        
        print("✅ Created conversations table")
    
    def store_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store a conversation message.
        
        Args:
            session_id: Session identifier
            role: "user" or "assistant"
            content: Message content
            metadata: Optional metadata
        """
        import json
        self.execute(
            """
            INSERT INTO conversations (session_id, role, content, metadata)
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, role, content, json.dumps(metadata) if metadata else None)
        )
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return (most recent)
        
        Returns:
            List of messages with role, content, timestamp, metadata
        """
        query = """
            SELECT role, content, timestamp, metadata
            FROM conversations
            WHERE session_id = %s
            ORDER BY timestamp DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        results = self.query(query, (session_id,))
        return list(reversed(results))  # Return chronological order
    
    def clear_conversation(self, session_id: str):
        """Delete all messages for a session."""
        self.execute(
            "DELETE FROM conversations WHERE session_id = %s",
            (session_id,)
        )
        print(f"✅ Cleared conversation: {session_id}")
    
    def enable_pgvector(self):
        """
        Enable pgvector extension for vector operations.
        
        Run this once to enable vector similarity search.
        """
        self.execute("CREATE EXTENSION IF NOT EXISTS vector")
        print("✅ Enabled pgvector extension")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# ============================================================================
# Helper Functions
# ============================================================================

def get_lakebase_connection_string(
    host: Optional[str] = None,
    database: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    port: int = 5432
) -> str:
    """
    Generate PostgreSQL connection string for Lakebase.
    
    Useful for SQLAlchemy, Django, or other ORMs.
    
    Returns:
        Connection string in format: postgresql://user:pass@host:port/db
    """
    host = host or os.getenv("LAKEBASE_HOST")
    database = database or os.getenv("LAKEBASE_DATABASE")
    user = user or os.getenv("LAKEBASE_USER")
    password = password or os.getenv("LAKEBASE_PASSWORD")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"
