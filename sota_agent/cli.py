"""Command-line interface for SOTA Agent Framework."""

import argparse
import sys
from .generator import generate_project


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SOTA Agent Framework - Generate AI agent projects for any domain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sota-generate --domain "customer_support"
  sota-generate --domain "fraud_detection" --output ./fraud-agents
  sota-generate --domain "trip_planner" --agent-type "ENRICHMENT"

For more information, visit: https://github.com/somasekar278/universal-agent-template
        """
    )
    
    parser.add_argument(
        "--domain",
        required=True,
        help="Domain name (e.g., customer_support, fraud_detection)"
    )
    parser.add_argument(
        "--output",
        default="./generated_agent_project",
        help="Output directory (default: ./generated_agent_project)"
    )
    parser.add_argument(
        "--agent-type",
        choices=["CRITICAL_PATH", "ENRICHMENT", "ORCHESTRATION"],
        default="ENRICHMENT",
        help="Agent type (default: ENRICHMENT)"
    )
    parser.add_argument(
        "--priority",
        choices=["CRITICAL", "HIGH", "NORMAL", "LOW"],
        default="NORMAL",
        help="Execution priority (default: NORMAL)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--execution-mode",
        choices=["in_process", "process_pool", "ray_task"],
        default="ray_task",
        help="Execution mode (default: ray_task)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="SOTA Agent Framework 0.1.6"
    )
    
    args = parser.parse_args()
    
    # Generate the project
    try:
        generate_project(
            domain=args.domain,
            output_dir=args.output,
            agent_type=args.agent_type,
            priority=args.priority,
            timeout=args.timeout,
            execution_mode=args.execution_mode,
        )
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

