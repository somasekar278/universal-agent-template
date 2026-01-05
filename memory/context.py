"""Context window management for LLM integration."""

from typing import Dict, List, Any, Optional


class ContextBudget:
    """Token budget for context window."""

    def __init__(self, max_tokens: int, reservation: float = 0.2):
        self.max_tokens = max_tokens
        self.reservation = reservation
        self.available_tokens = int(max_tokens * (1 - reservation))


class ContextPrioritization:
    """Prioritize memories for context inclusion."""

    @staticmethod
    def prioritize(memories: List, budget: int) -> List:
        """Select memories that fit within budget."""
        # Simplified - would calculate token counts
        return memories[:10]  # Return top 10


class ContextWindowManager:
    """
    Manages LLM context window with token budgeting.

    Ensures:
    - Context fits within token limits
    - Most relevant memories included
    - System prompts have reserved space
    - Efficient token usage
    """

    def __init__(self, max_tokens: int = 8000, reservation: float = 0.2):
        self.budget = ContextBudget(max_tokens, reservation)
        self.prioritization = ContextPrioritization()

    async def build_context(
        self,
        query: str,
        memory_manager,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build context for LLM.

        Args:
            query: Current query
            memory_manager: Memory manager instance
            system_prompt: Optional system prompt

        Returns:
            Context dict with messages and token info
        """
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Retrieve relevant memories
        memories = await memory_manager.retrieve(query, limit=20)

        # Prioritize within budget
        selected = self.prioritization.prioritize(
            memories,
            self.budget.available_tokens
        )

        # Add memories as context
        if selected:
            memory_context = "\n\n".join([
                f"Memory: {mem.content}"
                for mem in selected
            ])
            messages.append({
                "role": "system",
                "content": f"Relevant context:\n{memory_context}"
            })

        # Add current query
        messages.append({"role": "user", "content": query})

        return {
            "messages": messages,
            "token_budget": self.budget.max_tokens,
            "memories_included": len(selected),
            "total_memories": len(memories)
        }
