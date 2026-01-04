"""
Databricks Agent Toolkit - Main CLI

Main command-line interface for the toolkit.
"""

import sys
import argparse

# Try to import check_authentication, but make it optional
try:
    from databricks_agent_toolkit.integrations import check_authentication
    _HAS_DATABRICKS = True
except ImportError:
    _HAS_DATABRICKS = False


def print_banner():
    """Print toolkit banner."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       Databricks Agent Toolkit v0.1.0                    ║
    ║                                                           ║
    ║       Pre-wired Databricks integrations for              ║
    ║       building production agents                          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Databricks Agent Toolkit - Build production agents on Databricks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check authentication
  databricks-agent-toolkit auth check
  
  # Generate chatbot (L1 - Simple)
  databricks-agent-toolkit generate chatbot my-bot
  
  # Generate assistant (L2 - With Memory)
  databricks-agent-toolkit generate assistant my-assistant
  
  # Get help on specific commands
  databricks-agent-toolkit generate --help
  
More scaffolds (api, workflow, system) coming in future releases!
For more info: https://github.com/databricks/databricks-agent-toolkit
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="databricks-agent-toolkit 0.1.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Check Databricks authentication")
    auth_parser.add_argument(
        "action",
        choices=["check"],
        help="Authentication action"
    )
    
    # Generate command (placeholder)
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate agent scaffolds"
    )
    generate_parser.add_argument(
        "level",
        choices=["chatbot", "assistant", "api", "workflow", "system"],
        help="Agent type to generate"
    )
    generate_parser.add_argument(
        "name",
        help="Agent name"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    # Handle commands
    if args.command == "auth":
        handle_auth(args)
    elif args.command == "generate":
        handle_generate(args)
    else:
        parser.print_help()


def handle_auth(args):
    """Handle auth commands."""
    if not _HAS_DATABRICKS:
        print("❌ Databricks integrations not available")
        print("   Install with: pip install databricks-agent-toolkit[databricks]")
        sys.exit(1)
    
    if args.action == "check":
        print("🔐 Checking Databricks authentication...\n")
        status = check_authentication()
        
        if status["authenticated"]:
            print(f"✅ Authenticated successfully!")
            print(f"   Host: {status['host']}")
            print(f"   User: {status['user']}")
        else:
            print(f"❌ Authentication failed: {status['error']}\n")
            print(status.get("help", ""))


def handle_generate(args):
    """Handle generate commands."""
    # Import here to avoid circular dependency
    from databricks_agent_toolkit.scaffolds import ScaffoldGenerator
    
    print(f"\n🚀 Generating {args.level} scaffold: {args.name}")
    
    try:
        generator = ScaffoldGenerator()
        generator.generate(
            level=args.level,
            name=args.name,
            output_dir=f"./{args.name}",
            options={"model": "databricks-claude-sonnet-4-5"}
        )
        print(f"\n✅ Generated successfully! See ./{args.name}/README.md")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

