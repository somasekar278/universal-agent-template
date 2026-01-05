"""Shared memory coordination between agents."""

from typing import Dict, Set, List, Optional
from enum import Enum
from .manager import MemoryEntry


class MemoryAccess(str, Enum):
    """Memory access levels."""
    PRIVATE = "private"    # Only owner can access
    SHARED = "shared"      # All agents can access
    READ_ONLY = "read_only"  # Others can read, owner can write


class PrivateMemory:
    """Private memory space for a single agent."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._memories: Dict[str, MemoryEntry] = {}

    async def add(self, memory: MemoryEntry):
        """Add to private memory."""
        self._memories[memory.id] = memory

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get from private memory."""
        return self._memories.get(memory_id)

    async def list(self) -> List[MemoryEntry]:
        """List all private memories."""
        return list(self._memories.values())


class SharedMemory:
    """Shared memory space accessible by multiple agents."""

    def __init__(self):
        self._memories: Dict[str, MemoryEntry] = {}
        self._access_control: Dict[str, Set[str]] = {}  # memory_id -> set of agent_ids

    async def add(self, memory: MemoryEntry, owner: str, access: MemoryAccess = MemoryAccess.SHARED):
        """Add to shared memory."""
        self._memories[memory.id] = memory
        memory.metadata.source = owner

        if access == MemoryAccess.PRIVATE:
            self._access_control[memory.id] = {owner}
        else:
            self._access_control[memory.id] = set()  # Empty means all can access

    async def get(self, memory_id: str, requester: str) -> Optional[MemoryEntry]:
        """Get from shared memory with access control."""
        if memory_id not in self._memories:
            return None

        # Check access
        if memory_id in self._access_control:
            allowed = self._access_control[memory_id]
            if allowed and requester not in allowed:
                return None  # Access denied

        return self._memories[memory_id]

    async def list(self, requester: str) -> List[MemoryEntry]:
        """List accessible shared memories."""
        accessible = []
        for mem_id, memory in self._memories.items():
            if mem_id in self._access_control:
                allowed = self._access_control[mem_id]
                if allowed and requester not in allowed:
                    continue
            accessible.append(memory)
        return accessible


class SharedMemoryCoordinator:
    """
    Coordinates memory sharing between agents.

    Manages:
    - Private memory spaces per agent
    - Shared memory accessible to multiple agents
    - Access control
    - Memory synchronization
    """

    def __init__(self):
        self._private_spaces: Dict[str, PrivateMemory] = {}
        self._shared_space = SharedMemory()

    def get_private_space(self, agent_id: str) -> PrivateMemory:
        """Get or create private memory space for agent."""
        if agent_id not in self._private_spaces:
            self._private_spaces[agent_id] = PrivateMemory(agent_id)
        return self._private_spaces[agent_id]

    def get_shared_space(self) -> SharedMemory:
        """Get shared memory space."""
        return self._shared_space

    async def share_memory(
        self,
        memory: MemoryEntry,
        owner: str,
        access: MemoryAccess = MemoryAccess.SHARED
    ):
        """Share a memory from private to shared space."""
        await self._shared_space.add(memory, owner, access)

    async def retrieve_for_agent(
        self,
        agent_id: str,
        include_shared: bool = True
    ) -> List[MemoryEntry]:
        """Retrieve all accessible memories for an agent."""
        memories = []

        # Get private memories
        private_space = self.get_private_space(agent_id)
        memories.extend(await private_space.list())

        # Get shared memories
        if include_shared:
            shared = await self._shared_space.list(agent_id)
            memories.extend(shared)

        return memories
