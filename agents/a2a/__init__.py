"""
Official Agent2Agent (A2A) Protocol Integration

Implements the Linux Foundation Agent2Agent Protocol for industry-standard
agent interoperability and communication.

Official Specification: https://github.com/a2aproject/A2A
Protocol Site: https://a2a-protocol.org/

The A2A protocol enables:
- Agent discovery via Agent Cards
- Task-based collaboration
- Secure cross-agent communication
- Standardized JSON-RPC 2.0 over HTTP(S)
- Streaming (SSE) and push notifications
- Multi-framework interoperability

Key Concepts:
- **Agent Card**: JSON document describing agent capabilities
- **Task**: Unit of work agents collaborate on
- **Skills**: Capabilities an agent advertises
- **JSON-RPC 2.0**: Communication protocol over HTTP(S)

Usage:
    # Install A2A SDK
    pip install a2a-sdk
    
    # Create A2A-enabled agent
    from agents.a2a import A2AAgent, A2AServer
    
    agent = A2AAgent(
        name="fraud_detector",
        skills=["fraud_detection", "risk_analysis"]
    )
    
    # Start A2A server
    server = A2AServer(agent, port=8080)
    await server.start()

When to Use A2A:
- ✅ Need cross-framework agent communication
- ✅ Building agent marketplaces
- ✅ Enterprise agent ecosystems
- ✅ Industry-standard interoperability
- ❌ Single-framework systems (use Router)
- ❌ Simple internal communication (use Router)

A2A vs Router:
- Router: Internal framework agents (fast, in-process)
- A2A: External agents across systems (HTTP, standardized)
"""

# Check if A2A SDK is available
try:
    import a2a
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False
    a2a = None

# Only expose classes if SDK is installed
if A2A_AVAILABLE:
    from .server import A2AServer
    from .client import A2AClient  
    from .agent import A2AAgent
    from .card import create_agent_card
    
    __all__ = [
        "A2AServer",
        "A2AClient",
        "A2AAgent",
        "create_agent_card",
        "A2A_AVAILABLE"
    ]
else:
    __all__ = ["A2A_AVAILABLE"]


def check_a2a_available():
    """Check if A2A SDK is installed."""
    if not A2A_AVAILABLE:
        raise ImportError(
            "A2A SDK not installed. Install with: pip install a2a-sdk\n"
            "See https://github.com/a2aproject/A2A for documentation"
        )


# Version aligned with A2A protocol
__version__ = "0.3.0"  # Aligned with A2A Protocol v0.3.0
