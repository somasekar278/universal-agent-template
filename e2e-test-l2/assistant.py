"""
e2e-test-l2 - Context-Aware Assistant (L2)

An intelligent assistant with conversation memory powered by Lakebase.

Features:
- Persistent conversation history (PostgreSQL via Lakebase)
- Session-based memory
- MLflow tracing
- Batch and streaming modes
- Databricks Model Serving integration

Learning Goals (L2):
- Manage conversation state across sessions
- Use Lakebase for persistent memory
- Build context-aware responses
- Handle long conversations with context windows
"""

import os
import sys
import asyncio
import uuid
from typing import List, Dict, Any
import yaml

try:
    from databricks_agent_toolkit.integrations import DatabricksLLM
    import mlflow
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False
    print("❌ databricks-agent-toolkit not installed")
    print("   Install with: pip install databricks-agent-toolkit")
    sys.exit(1)

from memory_manager import MemoryManager
from rag_manager import RAGManager


# ============================================================================
# Configuration
# ============================================================================

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


# ============================================================================
# Assistant Logic
# ============================================================================

class Assistant:
    """Context-aware assistant with memory."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize assistant with config."""
        self.config = config
        self.model_config = config["model"]
        self.memory_config = config["memory"]
        self.rag_config = config.get("rag", {})
        self.mlflow_config = config.get("mlflow", {})
        
        # Initialize LLM
        self.llm = DatabricksLLM(
            endpoint=self.model_config["endpoint"],
            auto_trace=self.mlflow_config.get("auto_trace", True)
        )
        
        # Initialize memory
        self.memory = MemoryManager(
            host=self.memory_config.get("host"),
            database=self.memory_config.get("database"),
            user=self.memory_config.get("user"),
            password=self.memory_config.get("password"),
            max_history=self.memory_config.get("max_history", 20)
        )
        
        # Initialize database
        self.memory.initialize()
        
        # Initialize RAG (optional)
        self.rag_enabled = self.rag_config.get("enabled", False)
        self.rag = None
        if self.rag_enabled:
            try:
                self.rag = RAGManager(
                    config=self.rag_config,
                    lakebase_client=self.memory.lakebase,
                    workspace_client=None
                )
            except Exception as e:
                print(f"⚠️  RAG initialization failed: {e}")
                print("   Assistant will work without RAG")
                self.rag_enabled = False
        
        # Streaming mode
        self.streaming = self.model_config.get("streaming", False)
        
        # MLflow
        if self.mlflow_config.get("auto_trace"):
            mlflow.set_experiment(self.mlflow_config.get("experiment", "/Shared/e2e-test-l2"))
    
    async def chat(self, session_id: str, user_message: str) -> str:
        """
        Process user message with conversation history and RAG.
        
        Args:
            session_id: Unique session identifier
            user_message: User's message
        
        Returns:
            Assistant's response
        """
        # Store user message
        self.memory.store_message(
            session_id=session_id,
            role="user",
            content=user_message
        )
        
        # Get conversation history
        history = self.memory.get_messages_for_llm(session_id)
        
        # Retrieve relevant documents (RAG)
        context = ""
        if self.rag_enabled and self.rag:
            try:
                docs = self.rag.retrieve(user_message)
                if docs:
                    context = "\n\n".join([
                        f"[Source: {doc['source']}]\n{doc['content']}"
                        for doc in docs
                    ])
            except Exception as e:
                print(f"⚠️  RAG retrieval failed: {e}")
        
        # Build system prompt with context
        system_prompt = self.model_config.get("system_prompt", "You are a helpful assistant.")
        if context:
            system_prompt = f"""You are a helpful assistant. Use the following context to answer questions accurately.

Context:
{context}

{system_prompt}"""
        
        # Add system prompt
        messages = []
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add history + current message
        messages.extend(history)
        
        # Get response
        if self.streaming:
            response = await self._chat_stream(messages)
        else:
            response = await self._chat_batch(messages)
        
        # Store assistant response
        self.memory.store_message(
            session_id=session_id,
            role="assistant",
            content=response
        )
        
        return response
    
    async def _chat_batch(self, messages: List[Dict[str, str]]) -> str:
        """Batch mode - single response."""
        response = await self.llm.chat(messages)
        return response["content"]
    
    async def _chat_stream(self, messages: List[Dict[str, str]]) -> str:
        """Streaming mode - token-by-token."""
        full_response = ""
        async for chunk in self.llm.stream(messages):
            content = chunk.get("content", "")
            print(content, end="", flush=True)
            full_response += content
        print()  # Newline after streaming
        return full_response
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics."""
        return self.memory.get_session_summary(session_id)
    
    def clear_session(self, session_id: str):
        """Clear session history."""
        self.memory.clear_conversation(session_id)
    
    def close(self):
        """Cleanup resources."""
        self.memory.close()


# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """Run assistant in CLI mode."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   e2e-test-l2 - Context-Aware Assistant (L2)              ║
    ║                                                           ║
    ║   Powered by Databricks + Lakebase Memory                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    This assistant remembers your conversation across the session.
    Type 'exit' to quit, 'clear' to clear history, 'info' for session stats.
    Type 'refresh' to re-index documents (if RAG enabled).
    """)
    
    # Load config
    config = load_config()
    
    # Initialize assistant
    assistant = Assistant(config)
    
    # Generate or load session ID
    session_id = os.getenv("SESSION_ID", str(uuid.uuid4()))
    print(f"📝 Session ID: {session_id}")
    print(f"💾 Memory: Lakebase (PostgreSQL)")
    print(f"🤖 Model: {config['model']['endpoint']}")
    if config.get('rag', {}).get('enabled'):
        print(f"📚 RAG: Enabled ({config['rag'].get('backend', 'pgvector')})")
    print(f"📊 MLflow: {config['mlflow'].get('experiment', '/Shared/e2e-test-l2')}")
    print()
    
    # Start MLflow run
    if config["mlflow"].get("auto_trace"):
        mlflow.start_run()
    
    try:
        turn_count = 0
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() == "exit":
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == "clear":
                assistant.clear_session(session_id)
                print("✅ Conversation history cleared\n")
                continue
            
            if user_input.lower() == "info":
                info = assistant.get_session_info(session_id)
                print(f"\n📊 Session Info:")
                print(f"   Messages: {info['message_count']}")
                print(f"   First: {info['first_message']}")
                print(f"   Last: {info['last_message']}\n")
                continue
            
            if user_input.lower() == "refresh":
                if assistant.rag_enabled and assistant.rag:
                    assistant.rag.refresh()
                else:
                    print("⚠️  RAG not enabled\n")
                continue
            
            # Get assistant response
            print("Assistant: ", end="" if config["model"].get("streaming") else "")
            response = await assistant.chat(session_id, user_input)
            
            if not config["model"].get("streaming"):
                print(response)
            
            print()
            
            turn_count += 1
            
            # Periodic assessment collection
            if config["mlflow"].get("assessments", {}).get("enabled", False):
                frequency = config["mlflow"]["assessments"].get("frequency", 5)
                if turn_count % frequency == 0:
                    print("\n📊 How was that response? (👍 good / 👎 bad / skip)")
                    feedback = input("Feedback: ").strip().lower()
                    if feedback in ["👍", "good", "g"]:
                        print("✅ Positive feedback recorded")
                    elif feedback in ["👎", "bad", "b"]:
                        print("✅ Negative feedback recorded")
                    print()
    
    finally:
        # Cleanup
        assistant.close()
        
        if config["mlflow"].get("auto_trace"):
            mlflow.end_run()
            
            # Show MLflow URL if enabled
            if config["mlflow"].get("show_url", False):
                run_info = mlflow.active_run()
                if run_info:
                    experiment_id = run_info.info.experiment_id
                    run_id = run_info.info.run_id
                    workspace_url = os.getenv("DATABRICKS_HOST", "https://your-workspace.cloud.databricks.com")
                    mlflow_url = f"{workspace_url}/ml/experiments/{experiment_id}/runs/{run_id}"
                    print(f"\n📊 MLflow Trace: {mlflow_url}")
            else:
                print("\n✅ Thanks for chatting!")


if __name__ == "__main__":
    asyncio.run(main())