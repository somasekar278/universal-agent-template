"""
Semantic embeddings integration for memory search.

Provides vector-based semantic similarity for intelligent memory retrieval.
"""

from typing import List, Optional, Dict, Any
import hashlib


class EmbeddingProvider:
    """
    Base class for embedding providers.

    Supports:
    - OpenAI embeddings
    - Sentence transformers
    - Databricks embeddings
    - Custom models
    """

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        raise NotImplementedError

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return [await self.embed(text) for text in texts]


class SentenceTransformerEmbeddings(EmbeddingProvider):
    """
    Sentence transformer embeddings (local).

    Usage:
        embedder = SentenceTransformerEmbeddings()
        vector = await embedder.embed("User prefers dark mode")
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize sentence transformer.

        Args:
            model_name: Model name (e.g., all-MiniLM-L6-v2, all-mpnet-base-v2)
        """
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Lazy load model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sota-agent-framework[semantic-search]"
                )

    async def embed(self, text: str) -> List[float]:
        """Generate embedding."""
        self._load_model()
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch."""
        self._load_model()
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


class OpenAIEmbeddings(EmbeddingProvider):
    """
    OpenAI embeddings (API-based).

    Usage:
        embedder = OpenAIEmbeddings(api_key="...")
        vector = await embedder.embed("text")
    """

    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        """
        Initialize OpenAI embeddings.

        Args:
            api_key: OpenAI API key
            model: Model name
        """
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        """Get OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai not installed. Install with: pip install openai")
        return self._client

    async def embed(self, text: str) -> List[float]:
        """Generate embedding."""
        client = self._get_client()
        response = client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch."""
        client = self._get_client()
        response = client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]


class DatabricksEmbeddings(EmbeddingProvider):
    """
    Databricks embeddings (Model Serving).

    Usage:
        embedder = DatabricksEmbeddings(endpoint_url="...")
        vector = await embedder.embed("text")
    """

    def __init__(self, endpoint_url: str, token: Optional[str] = None):
        """
        Initialize Databricks embeddings.

        Args:
            endpoint_url: Model serving endpoint URL
            token: Databricks token (uses env var if None)
        """
        self.endpoint_url = endpoint_url
        self.token = token

    async def embed(self, text: str) -> List[float]:
        """Generate embedding."""
        import httpx
        import os

        token = self.token or os.environ.get("DATABRICKS_TOKEN")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.endpoint_url,
                json={"input": text},
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()["embedding"]


class CachedEmbeddings(EmbeddingProvider):
    """
    Cached embeddings to avoid recomputing.

    Usage:
        base = SentenceTransformerEmbeddings()
        embedder = CachedEmbeddings(base)
    """

    def __init__(self, provider: EmbeddingProvider, max_cache_size: int = 10000):
        """
        Initialize cached embeddings.

        Args:
            provider: Base embedding provider
            max_cache_size: Max cache size
        """
        self.provider = provider
        self.max_cache_size = max_cache_size
        self._cache: Dict[str, List[float]] = {}

    def _cache_key(self, text: str) -> str:
        """Generate cache key."""
        return hashlib.md5(text.encode()).hexdigest()

    async def embed(self, text: str) -> List[float]:
        """Generate or retrieve cached embedding."""
        cache_key = self._cache_key(text)

        if cache_key in self._cache:
            return self._cache[cache_key]

        embedding = await self.provider.embed(text)

        # Add to cache
        if len(self._cache) < self.max_cache_size:
            self._cache[cache_key] = embedding

        return embedding


class SemanticMemorySearch:
    """
    Semantic search over memories using embeddings.

    Usage:
        search = SemanticMemorySearch(embedder)
        results = await search.find_similar(
            query="What does user prefer?",
            memories=all_memories,
            top_k=5
        )
    """

    def __init__(self, embedder: EmbeddingProvider):
        """
        Initialize semantic search.

        Args:
            embedder: Embedding provider
        """
        self.embedder = embedder

    async def find_similar(
        self,
        query: str,
        memories: List[Any],
        top_k: int = 10,
        min_similarity: float = 0.7
    ) -> List[tuple]:
        """
        Find semantically similar memories.

        Args:
            query: Query text
            memories: List of memory entries
            top_k: Number of results
            min_similarity: Minimum similarity threshold

        Returns:
            List of (memory, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = await self.embedder.embed(query)

        # Compute similarities
        similarities = []
        for memory in memories:
            # Get or generate memory embedding
            if memory.metadata.embedding is None:
                content_str = str(memory.content)
                memory.metadata.embedding = await self.embedder.embed(content_str)

            # Compute cosine similarity
            similarity = self._cosine_similarity(
                query_embedding,
                memory.metadata.embedding
            )

            if similarity >= min_similarity:
                similarities.append((memory, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity."""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    async def embed_memories_batch(self, memories: List[Any]):
        """
        Pre-compute embeddings for memories in batch.

        More efficient than one-by-one.
        """
        # Find memories without embeddings
        to_embed = [
            (i, mem) for i, mem in enumerate(memories)
            if mem.metadata.embedding is None
        ]

        if not to_embed:
            return

        # Extract texts
        texts = [str(mem.content) for _, mem in to_embed]

        # Generate embeddings in batch
        embeddings = await self.embedder.embed_batch(texts)

        # Assign back
        for (i, mem), embedding in zip(to_embed, embeddings):
            mem.metadata.embedding = embedding
