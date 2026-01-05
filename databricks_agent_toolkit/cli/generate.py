"""
Databricks Agent Toolkit - Generate Command

Generate L1-L5 agent scaffolds.
"""

import argparse
import sys

from databricks_agent_toolkit.scaffolds import ScaffoldGenerator


def main():
    """Generate command entry point."""
    parser = argparse.ArgumentParser(
        description="Generate agent scaffolds (L1-L5)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple chatbot
  databricks-agent-toolkit generate chatbot hello-bot

  # Assistant with memory only (no RAG)
  databricks-agent-toolkit generate assistant support-assistant

  # Assistant with memory + RAG (pgvector)
  databricks-agent-toolkit generate assistant doc-assistant \\
    --enable-rag \\
    --rag-source /Volumes/main/default/docs \\
    --index-type ivfflat

  # Assistant with memory + RAG (Vector Search)
  databricks-agent-toolkit generate assistant enterprise-assistant \\
    --enable-rag \\
    --rag-backend vector_search \\
    --rag-source /Volumes/main/default/docs \\
    --vector-search-endpoint my-endpoint \\
    --vector-search-index main.default.docs_index

  # Production API with MCP
  databricks-agent-toolkit generate api customer-support --enable-mcp

  # Complex workflow with optimization
  databricks-agent-toolkit generate workflow research-agent --workflow plan-act-critique --enable-optimization

  # Multi-agent system
  databricks-agent-toolkit generate system healthcare-system --agents diagnostic,treatment,monitoring

For more info: https://databricks-agent-toolkit.readthedocs.io
        """,
    )

    # Level and name (required)
    parser.add_argument(
        "level",
        choices=["chatbot", "assistant", "api", "workflow", "system"],
        help="Agent type (chatbot, assistant, api, workflow, system)",
    )
    parser.add_argument("name", help="Agent name (e.g., 'customer-support', 'research-agent')")

    # Output directory (optional)
    parser.add_argument("-o", "--output", default=None, help="Output directory (default: ./{name})")

    # Model selection
    parser.add_argument(
        "--model", default="databricks-claude-sonnet-4-5", help="Model endpoint (default: databricks-claude-sonnet-4-5)"
    )

    # Feature flags
    parser.add_argument("--enable-mcp", action="store_true", help="Enable MCP tools (api, workflow, system)")
    parser.add_argument(
        "--enable-optimization", action="store_true", help="Enable automatic optimization (workflow, system)"
    )
    parser.add_argument(
        "--enable-memory", action="store_true", default=True, help="Enable memory (assistant+, enabled by default)"
    )
    parser.add_argument("--enable-a2a", action="store_true", help="Enable A2A protocol (system)")

    # RAG configuration (L2+)
    parser.add_argument("--enable-rag", action="store_true", help="Enable RAG for knowledge retrieval (assistant+)")
    parser.add_argument(
        "--rag-backend",
        choices=["pgvector", "vector_search"],
        default="pgvector",
        help="RAG backend (default: pgvector)",
    )
    parser.add_argument("--rag-source", help="UC Volume path for documents (e.g., /Volumes/main/default/docs)")
    parser.add_argument(
        "--index-type",
        choices=["ivfflat", "hnsw"],
        default="ivfflat",
        help="pgvector index type: ivfflat (fast) or hnsw (accurate)",
    )
    parser.add_argument("--vector-search-endpoint", help="Vector Search endpoint name (for vector_search backend)")
    parser.add_argument("--vector-search-index", help="Vector Search index name (e.g., main.default.docs_index)")

    # Workflow-specific
    parser.add_argument(
        "--workflow",
        default="plan-act-critique",
        choices=["plan-act-critique", "react", "chain-of-thought"],
        help="Workflow pattern (default: plan-act-critique)",
    )

    # System-specific
    parser.add_argument(
        "--agents", help="Comma-separated list of agent names for system (e.g., 'agent_a,agent_b,agent_c')"
    )

    # List available levels
    parser.add_argument("--list", action="store_true", help="List available scaffold levels")

    args = parser.parse_args()

    # Handle --list
    if args.list:
        print_levels()
        return

    # Determine output directory
    output_dir = args.output or f"./{args.name}"

    # Parse agents for L5
    agents = None
    if args.agents:
        agents = [a.strip() for a in args.agents.split(",")]

    # Prepare options
    options = {
        "model": args.model,
        "enable_mcp": args.enable_mcp,
        "enable_optimization": args.enable_optimization,
        "enable_memory": args.enable_memory,
        "enable_a2a": args.enable_a2a,
        "workflow": args.workflow,
        "agents": agents or ["agent_a", "agent_b"],
        # RAG options (L2+)
        "enable_rag": args.enable_rag if hasattr(args, "enable_rag") else False,
        "rag_backend": args.rag_backend if hasattr(args, "rag_backend") else "pgvector",
        "rag_source": args.rag_source if hasattr(args, "rag_source") else None,
        "index_type": args.index_type if hasattr(args, "index_type") else "ivfflat",
        "vector_search_endpoint": args.vector_search_endpoint if hasattr(args, "vector_search_endpoint") else None,
        "vector_search_index": args.vector_search_index if hasattr(args, "vector_search_index") else None,
    }

    # Generate scaffold
    try:
        generator = ScaffoldGenerator()
        generator.generate(level=args.level, name=args.name, output_dir=output_dir, options=options)

        print(f"\n✅ Successfully generated {args.level} scaffold!")
        print("\n📁 Next steps:")
        print(f"   cd {output_dir}")
        print("   pip install -r requirements.txt")

        if args.level == "chatbot":
            print("   python chatbot.py")
        elif args.level == "assistant":
            print("   python assistant.py")
        elif args.level == "api":
            print("   python main.py")
        elif args.level in ["workflow", "system"]:
            print("   python workflow.py")

        print(f"\n📖 Read {output_dir}/README.md for detailed instructions")

    except Exception as e:
        print(f"\n❌ Error generating scaffold: {e}", file=sys.stderr)
        sys.exit(1)


def print_levels():
    """Print available scaffold types."""
    generator = ScaffoldGenerator()
    levels = generator.list_levels()

    print("\n🎯 Available Scaffold Types:\n")

    for level_id, info in levels.items():
        print(f"{level_id}: {info['name']}")
        print(f"   Complexity: {info['complexity']}")
        print(f"   Time: {info['time']}")
        print(f"   Description: {info['description']}")
        print(f"   Features: {', '.join(info['features'])}")
        print()


if __name__ == "__main__":
    main()
