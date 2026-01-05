"""
Databricks Vector Search - Thin Wrapper for Delta Lake Vector Search

This is a convenience wrapper around Databricks SDK's vector search APIs.
All actual vector operations happen in Databricks Vector Search (Delta Lake-based).

For advanced usage, use the Databricks SDK directly:
https://databricks-sdk-py.readthedocs.io/en/latest/workspace/vector_search_indexes.html
"""

import os
from typing import Any, Dict, List, Optional

from databricks.sdk import WorkspaceClient

# Try to import VectorIndexType, but make it optional for older SDK versions
try:
    from databricks.sdk.service.catalog import VectorIndexType
except ImportError:
    VectorIndexType = None  # Will be checked at runtime if needed


class DatabricksVectorSearch:
    """
    Thin wrapper around Databricks Vector Search (Delta Lake-based).

    This is NOT a custom vector store - it just provides convenience
    methods for common operations. All storage and search happens in Delta Lake.

    Example:
        ```python
        from databricks_agent_toolkit.integrations import DatabricksVectorSearch

        client = DatabricksVectorSearch()

        # Create index (one-time setup)
        client.create_index(
            name="main.agents.knowledge_base",
            source_table="main.agents.documents",
            embedding_column="content"
        )

        # Search
        results = client.search(
            index_name="main.agents.knowledge_base",
            query="What is machine learning?",
            num_results=5
        )
        ```
    """

    def __init__(self, host: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize Databricks Vector Search client.

        Args:
            host: Databricks workspace URL (defaults to DATABRICKS_HOST env var)
            token: Databricks token (defaults to DATABRICKS_TOKEN env var)
        """
        self.client = WorkspaceClient(
            host=host or os.getenv("DATABRICKS_HOST"), token=token or os.getenv("DATABRICKS_TOKEN")
        )

    def create_index(
        self,
        name: str,
        source_table: str,
        embedding_column: str,
        endpoint_name: str = "default_vector_endpoint",
        primary_key: str = "id",
        embedding_model: str = "databricks-bge-large-en",
    ) -> Dict[str, Any]:
        """
        Create a vector search index in Databricks Vector Search (Delta Lake).

        This is a one-time setup operation. The index will automatically
        sync with the source Delta table.

        Args:
            name: Full name of index (e.g., "main.agents.knowledge_base")
            source_table: Full name of source Delta table
            embedding_column: Column to embed
            endpoint_name: Vector search endpoint name
            primary_key: Primary key column
            embedding_model: Databricks embedding model endpoint

        Returns:
            Index creation response
        """
        try:
            result = self.client.vector_search_indexes.create_index(
                name=name,
                endpoint_name=endpoint_name,
                primary_key=primary_key,
                index_type=VectorIndexType.DELTA_SYNC,
                delta_sync_index_spec={
                    "source_table": source_table,
                    "embedding_source_columns": [
                        {"name": embedding_column, "embedding_model_endpoint_name": embedding_model}
                    ],
                },
            )
            print(f"✅ Created Vector Search index: {name}")
            return result
        except Exception as e:
            print(f"❌ Failed to create index: {e}")
            raise

    def search(
        self, index_name: str, query: str, num_results: int = 10, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search vectors in Databricks Vector Search.

        Args:
            index_name: Full name of index
            query: Query text (will be embedded automatically)
            num_results: Number of results to return
            filters: Optional filters (e.g., {"agent_id": "fraud_detector"})

        Returns:
            List of search results with scores
        """
        try:
            result = self.client.vector_search_indexes.query_index(
                index_name=index_name, query_text=query, num_results=num_results, filters=filters
            )

            # Convert to simple dict format
            results = []
            if result.manifest and result.manifest.columns:
                for col in result.manifest.columns:
                    results.append(
                        {
                            "score": col.score if hasattr(col, "score") else None,
                            "content": col.content if hasattr(col, "content") else None,
                            "metadata": col.metadata if hasattr(col, "metadata") else {},
                        }
                    )

            return results
        except Exception as e:
            print(f"❌ Search failed: {e}")
            raise

    def delete_index(self, index_name: str) -> None:
        """
        Delete a vector search index.

        Args:
            index_name: Full name of index to delete
        """
        try:
            self.client.vector_search_indexes.delete_index(index_name=index_name)
            print(f"✅ Deleted index: {index_name}")
        except Exception as e:
            print(f"❌ Failed to delete index: {e}")
            raise

    def list_indexes(self, endpoint_name: str = "default_vector_endpoint") -> List[str]:
        """
        List all vector search indexes on an endpoint.

        Args:
            endpoint_name: Vector search endpoint name

        Returns:
            List of index names
        """
        try:
            indexes = self.client.vector_search_indexes.list_indexes(endpoint_name=endpoint_name)
            return [idx.name for idx in indexes]
        except Exception as e:
            print(f"❌ Failed to list indexes: {e}")
            raise

    def get_index_status(self, index_name: str) -> Dict[str, Any]:
        """
        Get status of a vector search index.

        Args:
            index_name: Full name of index

        Returns:
            Index status information
        """
        try:
            index = self.client.vector_search_indexes.get_index(index_name=index_name)
            return {
                "name": index.name,
                "status": index.status,
                "index_type": index.index_type,
                "endpoint_name": index.endpoint_name,
            }
        except Exception as e:
            print(f"❌ Failed to get index status: {e}")
            raise


# ============================================================================
# For Advanced Usage: Use Databricks SDK Directly
# ============================================================================


def get_native_vector_search_client() -> WorkspaceClient:
    """
    Get the native Databricks SDK client for advanced operations.

    For full API reference, see:
    https://databricks-sdk-py.readthedocs.io/en/latest/workspace/vector_search_indexes.html

    Example:
        ```python
        from databricks_agent_toolkit.integrations import get_native_vector_search_client

        client = get_native_client()

        # Use full SDK capabilities
        indexes = client.vector_search_indexes.list_indexes(endpoint_name="my_endpoint")
        for idx in indexes:
            print(f"Index: {idx.name}, Status: {idx.status}")
        ```
    """
    return WorkspaceClient(host=os.getenv("DATABRICKS_HOST"), token=os.getenv("DATABRICKS_TOKEN"))
