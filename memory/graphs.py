"""
Memory graphs for relationship tracking.

Represents memories as a knowledge graph with:
- Nodes: Individual memories
- Edges: Relationships between memories
- Graph traversal: Find connected memories
- Pattern detection: Identify memory clusters
"""

from typing import List, Dict, Set, Optional, Any
from enum import Enum
from dataclasses import dataclass, field


class RelationType(str, Enum):
    """Types of relationships between memories."""
    RELATED_TO = "related_to"          # General relationship
    CAUSED_BY = "caused_by"            # Causal relationship
    FOLLOWS = "follows"                # Temporal sequence
    CONTRADICTS = "contradicts"        # Conflicting information
    SUPPORTS = "supports"              # Supporting evidence
    SUMMARIZES = "summarizes"          # Summary relationship
    DERIVED_FROM = "derived_from"      # Derived insight
    SIMILAR_TO = "similar_to"          # Semantic similarity


@dataclass
class MemoryRelation:
    """Relationship between two memories."""
    from_memory_id: str
    to_memory_id: str
    relation_type: RelationType
    strength: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryGraph:
    """
    Memory graph for relationship tracking.

    Represents memories as nodes and relationships as edges.

    Usage:
        graph = MemoryGraph()

        # Add memories
        graph.add_node(memory1)
        graph.add_node(memory2)

        # Add relationship
        graph.add_relation(
            memory1.id,
            memory2.id,
            RelationType.CAUSED_BY,
            strength=0.8
        )

        # Find related
        related = graph.get_related(memory1.id, depth=2)
    """

    def __init__(self):
        """Initialize memory graph."""
        self._nodes: Dict[str, Any] = {}  # memory_id -> memory
        self._edges: Dict[str, List[MemoryRelation]] = {}  # from_id -> [relations]
        self._reverse_edges: Dict[str, List[MemoryRelation]] = {}  # to_id -> [relations]

    def add_node(self, memory: Any):
        """Add memory as node."""
        self._nodes[memory.id] = memory
        if memory.id not in self._edges:
            self._edges[memory.id] = []
        if memory.id not in self._reverse_edges:
            self._reverse_edges[memory.id] = []

    def add_relation(
        self,
        from_id: str,
        to_id: str,
        relation_type: RelationType,
        strength: float = 1.0,
        metadata: Optional[Dict] = None
    ):
        """Add relationship between memories."""
        relation = MemoryRelation(
            from_memory_id=from_id,
            to_memory_id=to_id,
            relation_type=relation_type,
            strength=strength,
            metadata=metadata or {}
        )

        # Add to forward edges
        if from_id not in self._edges:
            self._edges[from_id] = []
        self._edges[from_id].append(relation)

        # Add to reverse edges
        if to_id not in self._reverse_edges:
            self._reverse_edges[to_id] = []
        self._reverse_edges[to_id].append(relation)

    def get_node(self, memory_id: str) -> Optional[Any]:
        """Get memory node by ID."""
        return self._nodes.get(memory_id)

    def get_relations(
        self,
        memory_id: str,
        direction: str = "outgoing",
        relation_type: Optional[RelationType] = None
    ) -> List[MemoryRelation]:
        """
        Get relations for a memory.

        Args:
            memory_id: Memory ID
            direction: "outgoing", "incoming", or "both"
            relation_type: Filter by relation type

        Returns:
            List of relations
        """
        relations = []

        if direction in ("outgoing", "both"):
            relations.extend(self._edges.get(memory_id, []))

        if direction in ("incoming", "both"):
            relations.extend(self._reverse_edges.get(memory_id, []))

        # Filter by type if specified
        if relation_type:
            relations = [r for r in relations if r.relation_type == relation_type]

        return relations

    def get_related(
        self,
        memory_id: str,
        depth: int = 1,
        min_strength: float = 0.0,
        relation_types: Optional[List[RelationType]] = None
    ) -> List[Any]:
        """
        Get related memories up to specified depth.

        Args:
            memory_id: Starting memory ID
            depth: How many hops to traverse
            min_strength: Minimum relationship strength
            relation_types: Filter by relation types

        Returns:
            List of related memories
        """
        visited = set()
        queue = [(memory_id, 0)]
        related = []

        while queue:
            current_id, current_depth = queue.pop(0)

            if current_id in visited or current_depth > depth:
                continue

            visited.add(current_id)

            # Get outgoing relations
            relations = self.get_relations(current_id, direction="outgoing")

            for relation in relations:
                # Filter by strength
                if relation.strength < min_strength:
                    continue

                # Filter by type
                if relation_types and relation.relation_type not in relation_types:
                    continue

                # Add related memory
                to_id = relation.to_memory_id
                if to_id not in visited:
                    memory = self.get_node(to_id)
                    if memory:
                        related.append(memory)

                    # Add to queue for further traversal
                    if current_depth < depth:
                        queue.append((to_id, current_depth + 1))

        return related

    def find_paths(
        self,
        from_id: str,
        to_id: str,
        max_depth: int = 3
    ) -> List[List[str]]:
        """
        Find all paths between two memories.

        Args:
            from_id: Start memory ID
            to_id: End memory ID
            max_depth: Maximum path length

        Returns:
            List of paths (each path is a list of memory IDs)
        """
        paths = []

        def dfs(current: str, target: str, path: List[str], depth: int):
            if depth > max_depth:
                return

            if current == target:
                paths.append(path.copy())
                return

            relations = self.get_relations(current, direction="outgoing")
            for relation in relations:
                next_id = relation.to_memory_id
                if next_id not in path:  # Avoid cycles
                    dfs(next_id, target, path + [next_id], depth + 1)

        dfs(from_id, to_id, [from_id], 0)
        return paths

    def find_clusters(self, min_cluster_size: int = 3) -> List[Set[str]]:
        """
        Find memory clusters (strongly connected components).

        Args:
            min_cluster_size: Minimum cluster size

        Returns:
            List of clusters (sets of memory IDs)
        """
        visited = set()
        clusters = []

        def explore(node_id: str, cluster: Set[str]):
            """DFS to explore cluster."""
            if node_id in visited:
                return

            visited.add(node_id)
            cluster.add(node_id)

            # Explore connected nodes
            relations = self.get_relations(node_id, direction="both")
            for relation in relations:
                other_id = (
                    relation.to_memory_id
                    if relation.from_memory_id == node_id
                    else relation.from_memory_id
                )
                if other_id not in visited:
                    explore(other_id, cluster)

        # Find all clusters
        for node_id in self._nodes:
            if node_id not in visited:
                cluster = set()
                explore(node_id, cluster)
                if len(cluster) >= min_cluster_size:
                    clusters.append(cluster)

        return clusters

    def get_most_connected(self, top_k: int = 10) -> List[tuple]:
        """
        Get most connected memories (highest degree).

        Args:
            top_k: Number of results

        Returns:
            List of (memory_id, connection_count) tuples
        """
        connections = {}

        for node_id in self._nodes:
            count = (
                len(self._edges.get(node_id, [])) +
                len(self._reverse_edges.get(node_id, []))
            )
            connections[node_id] = count

        sorted_nodes = sorted(
            connections.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_nodes[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        total_edges = sum(len(edges) for edges in self._edges.values())

        # Count by relation type
        by_type = {}
        for edges in self._edges.values():
            for edge in edges:
                rel_type = edge.relation_type.value
                by_type[rel_type] = by_type.get(rel_type, 0) + 1

        return {
            "total_nodes": len(self._nodes),
            "total_edges": total_edges,
            "avg_degree": total_edges / len(self._nodes) if self._nodes else 0,
            "by_relation_type": by_type
        }


class AutoRelationDetector:
    """
    Automatically detects relationships between memories.

    Uses:
    - Temporal proximity (FOLLOWS)
    - Semantic similarity (SIMILAR_TO, RELATED_TO)
    - Causal patterns (CAUSED_BY)
    - Contradiction detection (CONTRADICTS)
    """

    def __init__(self, similarity_threshold: float = 0.75):
        """
        Initialize auto detector.

        Args:
            similarity_threshold: Threshold for SIMILAR_TO relation
        """
        self.similarity_threshold = similarity_threshold

    async def detect_relations(
        self,
        memory: Any,
        existing_memories: List[Any],
        embedder: Optional[Any] = None
    ) -> List[MemoryRelation]:
        """
        Detect relationships between new memory and existing ones.

        Args:
            memory: New memory
            existing_memories: Existing memories to compare
            embedder: Optional embedding provider for semantic similarity

        Returns:
            List of detected relations
        """
        relations = []

        for existing in existing_memories:
            # Temporal proximity (FOLLOWS)
            time_diff = (
                memory.metadata.created_at - existing.metadata.created_at
            ).total_seconds()

            if 0 < time_diff < 300:  # Within 5 minutes
                relations.append(MemoryRelation(
                    from_memory_id=existing.id,
                    to_memory_id=memory.id,
                    relation_type=RelationType.FOLLOWS,
                    strength=max(0, 1.0 - time_diff / 300)
                ))

            # Semantic similarity (if embedder available)
            if embedder and memory.metadata.embedding and existing.metadata.embedding:
                from .embeddings import SemanticMemorySearch
                similarity = SemanticMemorySearch._cosine_similarity(
                    memory.metadata.embedding,
                    existing.metadata.embedding
                )

                if similarity >= self.similarity_threshold:
                    relations.append(MemoryRelation(
                        from_memory_id=existing.id,
                        to_memory_id=memory.id,
                        relation_type=RelationType.SIMILAR_TO,
                        strength=similarity
                    ))

            # Check for explicit relationships in metadata
            if existing.id in memory.metadata.related_memories:
                relations.append(MemoryRelation(
                    from_memory_id=existing.id,
                    to_memory_id=memory.id,
                    relation_type=RelationType.RELATED_TO,
                    strength=1.0
                ))

        return relations
