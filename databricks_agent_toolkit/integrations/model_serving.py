"""
Databricks Model Serving Integration

Easy LLM client for Databricks Model Serving with automatic:
- Authentication via Databricks SDK or environment variables
- MLflow tracing
- Token usage tracking
- Error handling
"""

from typing import List, Dict, Any, Optional, AsyncIterator
import mlflow
import logging
import os
import requests

try:
    from databricks.sdk import WorkspaceClient
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    WorkspaceClient = None

logger = logging.getLogger(__name__)


class DatabricksLLM:
    """
    Easy LLM client for Databricks Model Serving.
    
    Features:
    - Automatic authentication via Databricks SDK
    - Automatic MLflow tracing (optional)
    - Tool calling support (OpenAI format)
    - Streaming support
    - Token usage tracking
    
    Example:
        from databricks_agent_toolkit.integrations import DatabricksLLM
        
        llm = DatabricksLLM(endpoint="databricks-claude-sonnet-4-5")
        
        # Simple chat
        response = await llm.chat([
            {"role": "user", "content": "What is machine learning?"}
        ])
        print(response["content"])
        
        # With tool calling
        response = await llm.chat(
            messages=[...],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "search_docs",
                        "description": "Search documentation",
                        "parameters": {"query": {"type": "string"}}
                    }
                }
            ]
        )
        
        # Streaming
        async for chunk in llm.stream(messages):
            print(chunk, end="")
    """
    
    def __init__(
        self,
        endpoint: str,
        workspace_client: Optional['WorkspaceClient'] = None,
        auto_trace: bool = True,
        **kwargs
    ):
        """
        Initialize Databricks LLM client.
        
        Args:
            endpoint: Model serving endpoint name (e.g., "databricks-claude-sonnet-4-5")
            workspace_client: Optional WorkspaceClient (auto-created if None)
            auto_trace: Automatically trace with MLflow (default: True)
            **kwargs: Additional configuration
        """
        self.endpoint = endpoint
        self.auto_trace = auto_trace
        
        # Get Databricks credentials - support multiple auth methods
        self.oauth_client_id = os.getenv('DATABRICKS_CLIENT_ID')
        self.oauth_client_secret = os.getenv('DATABRICKS_CLIENT_SECRET')
        self._cached_token = None
        self._token_expiry = 0
        
        # Priority order for authentication:
        # 1. Explicit OAuth M2M (DATABRICKS_CLIENT_ID + SECRET)
        # 2. Static token (DATABRICKS_TOKEN)
        # 3. Databricks SDK config (local dev)
        
        if self.oauth_client_id and self.oauth_client_secret:
            # OAuth M2M (highest priority - for Databricks Apps)
            self.workspace_client = None
            self.databricks_host = os.getenv('DATABRICKS_HOST', '')
            self.auth_method = "OAuth M2M"
        elif os.getenv('DATABRICKS_TOKEN'):
            # Static token (second priority - for notebooks)
            self.workspace_client = None
            self.databricks_host = os.getenv('DATABRICKS_HOST', '')
            self.auth_method = "Token"
        elif workspace_client and SDK_AVAILABLE:
            # Explicit SDK client provided
            self.workspace_client = workspace_client
            self.databricks_host = workspace_client.config.host.rstrip('/')
            self.auth_method = "SDK"
        elif SDK_AVAILABLE:
            # Try SDK config (lowest priority - for local dev)
            try:
                self.workspace_client = WorkspaceClient()
                self.databricks_host = self.workspace_client.config.host.rstrip('/')
                self.auth_method = "SDK"
            except Exception:
                raise ValueError(
                    "No authentication method available. Provide one of:\n"
                    "- DATABRICKS_CLIENT_ID + DATABRICKS_CLIENT_SECRET (Databricks Apps)\n"
                    "- DATABRICKS_TOKEN (notebooks/clusters)\n"
                    "- databricks-sdk config (local dev)"
                )
        else:
            raise ValueError(
                "No authentication method available. Provide one of:\n"
                "- DATABRICKS_CLIENT_ID + DATABRICKS_CLIENT_SECRET (Databricks Apps)\n"
                "- DATABRICKS_TOKEN (notebooks/clusters)\n"
                "- Install databricks-sdk for local dev"
            )
        
        # Ensure https:// scheme
        if self.databricks_host and not self.databricks_host.startswith('http'):
            self.databricks_host = f'https://{self.databricks_host}'
        self.databricks_host = self.databricks_host.rstrip('/')
        
        if not self.databricks_host:
            raise ValueError("DATABRICKS_HOST not found")
        
        logger.info(f"✅ Initialized Databricks LLM client: {endpoint} (auth: {self.auth_method})")
    
    def _get_auth_token(self) -> str:
        """
        Get authentication token using the appropriate method.
        
        Returns:
            Valid authentication token
        """
        import time
        
        # For OAuth M2M, cache token and refresh when expired
        if self.auth_method == "OAuth M2M":
            current_time = time.time()
            
            # Return cached token if still valid (with 60s buffer)
            if self._cached_token and current_time < (self._token_expiry - 60):
                return self._cached_token
            
            # Get new OAuth token
            from requests.auth import HTTPBasicAuth
            
            token_url = f"{self.databricks_host}/oidc/v1/token"
            response = requests.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "scope": "all-apis"
                },
                auth=HTTPBasicAuth(self.oauth_client_id, self.oauth_client_secret),
                timeout=30
            )
            response.raise_for_status()
            token_data = response.json()
            
            self._cached_token = token_data['access_token']
            # OAuth tokens typically expire in 3600s (1 hour)
            self._token_expiry = current_time + token_data.get('expires_in', 3600)
            
            return self._cached_token
        
        elif self.auth_method == "Token":
            return os.getenv('DATABRICKS_TOKEN')
        
        elif self.auth_method == "SDK":
            return self.workspace_client.config.token
        
        else:
            raise ValueError(f"Unknown auth method: {self.auth_method}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat completion with automatic tracing.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool schemas (OpenAI format)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the model
        
        Returns:
            Dict with:
            - content: Response text
            - tool_calls: List of tool calls (if any)
            - usage: Token usage stats
            - model: Model used
        
        Example:
            response = await llm.chat(
                messages=[{"role": "user", "content": "Hello!"}],
                temperature=0.7
            )
            print(response["content"])
        """
        # Execute chat completion (tracing handled by parent span if active)
        try:
            return await self._do_chat(messages, tools, temperature, max_tokens, **kwargs)
        except Exception as e:
            logger.error(f"❌ Chat completion failed: {e}")
            raise
    
    async def _do_chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Internal method to execute chat completion via REST API."""
        
        # Build request URL
        url = f"{self.databricks_host}/serving-endpoints/{self.endpoint}/invocations"
        
        # Get authentication token
        token = self._get_auth_token()
        
        # Build request headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Build request payload
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # Add tools if provided
        if tools:
            payload["tools"] = tools
        
        # Call Databricks Model Serving REST API
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        response_data = response.json()
        
        # Extract response (OpenAI-compatible format)
        choice = response_data['choices'][0]
        message = choice['message']
        
        return {
            "content": message.get('content', ''),
            "tool_calls": message.get('tool_calls'),
            "usage": response_data.get('usage', {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }),
            "model": response_data.get('model', self.endpoint),
            "finish_reason": choice.get('finish_reason')
        }
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream chat completion.
        
        Args:
            messages: List of message dicts
            tools: Optional list of tool schemas
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
        
        Yields:
            String chunks of the response
        
        Example:
            async for chunk in llm.stream(messages):
                print(chunk, end="", flush=True)
        """
        try:
            # Build request URL
            url = f"{self.databricks_host}/serving-endpoints/{self.endpoint}/invocations"
            
            # Get authentication token
            token = self._get_auth_token()
            
            # Build request headers
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Build request payload
            payload = {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs
            }
            
            if tools:
                payload["tools"] = tools
            
            # Stream from Databricks Model Serving REST API
            response = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            # Parse SSE stream
            import json
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                delta = chunk_data['choices'][0].get('delta', {})
                                content = delta.get('content')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            pass  # Skip malformed chunks
        
        except Exception as e:
            logger.error(f"❌ Streaming failed: {e}")
            raise
    
    def get_endpoint_info(self) -> Dict[str, Any]:
        """
        Get information about the model serving endpoint.
        
        Returns:
            Dict with endpoint details
        """
        try:
            if self.workspace_client:
                # Use SDK if available
                endpoint = self.workspace_client.serving_endpoints.get(name=self.endpoint)
                return {
                    "name": endpoint.name,
                    "state": endpoint.state,
                    "creator": endpoint.creator,
                    "creation_timestamp": endpoint.creation_timestamp,
                    "config": endpoint.config
                }
            else:
                # Use REST API fallback
                token = self._get_auth_token()
                url = f"{self.databricks_host}/api/2.0/serving-endpoints/{self.endpoint}"
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to get endpoint info: {e}")
            return {"error": str(e)}

