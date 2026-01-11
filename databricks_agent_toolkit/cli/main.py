"""
Databricks Agent Toolkit - Main CLI

Main command-line interface for the toolkit.
"""

import argparse
import sys

# Import version from parent module
from databricks_agent_toolkit import __version__

# Try to import check_authentication, but make it optional
try:
    from databricks_agent_toolkit.integrations import check_authentication

    _HAS_DATABRICKS = True
except ImportError:
    _HAS_DATABRICKS = False


def print_banner():
    """Print toolkit banner."""
    print(
        f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       Databricks Agent Toolkit v{__version__}                   ║
    ║                                                           ║
    ║       Pre-wired Databricks integrations for              ║
    ║       building production agents                          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Databricks Agent Toolkit - Build production agents on Databricks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # WORKFLOW: Generate → Deploy → Run → View

  # 1. Generate chatbot with Streamlit UI (default)
  dat generate chatbot my-bot

  # 2. Deploy to Databricks
  cd my-bot && databricks bundle deploy && databricks bundle run

  # L1 Chatbot - All UI frameworks supported
  dat generate chatbot my-bot --model databricks-claude-sonnet-4 --ui streamlit  # Streaming ✅
  dat generate chatbot my-bot --model databricks-claude-sonnet-4 --ui gradio     # Batch only
  dat generate chatbot my-bot --model databricks-claude-sonnet-4 --ui dash       # Batch only

  # Check authentication
  dat auth check

  # Get help on specific commands
  dat generate --help

Uses official Databricks UI templates (Streamlit, Gradio, Dash) - zero custom frontend!
More scaffolds (api, workflow, system) coming in future releases!
For more info: https://github.com/databricks/databricks-agent-toolkit
        """,
    )

    parser.add_argument("--version", action="version", version=f"databricks-agent-toolkit {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Check Databricks authentication")
    auth_parser.add_argument("action", choices=["check"], help="Authentication action")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate agent scaffolds")
    generate_parser.add_argument("level", choices=["chatbot"], help="Agent type to generate")
    generate_parser.add_argument("name", help="Agent name")
    generate_parser.add_argument(
        "--model",
        default="databricks-claude-sonnet-4",
        help="Model endpoint name (default: databricks-claude-sonnet-4)",
    )
    generate_parser.add_argument(
        "--enable-rag", action="store_true", help="Enable RAG capabilities (L2 assistant only)"
    )
    generate_parser.add_argument(
        "--ui",
        choices=["streamlit", "gradio", "dash", "fastapi", "none"],
        default="streamlit",
        help="UI framework (default: streamlit). Streamlit: streaming + memory. Gradio/Dash: batch only, L1 only.",
    )
    generate_parser.add_argument("--output-dir", help="Custom output directory (default: ./<name>)")

    # Test command
    test_parser = subparsers.add_parser("test", help="Validate agent code before deploying")
    test_parser.add_argument("app_dir", help="Path to agent directory (e.g., ./my-bot)")

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
    elif args.command == "test":
        handle_test(args)
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
            print("✅ Authenticated successfully!")
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
    print(f"   Model: {args.model}")
    streaming_status = "✅ streaming" if args.ui == "streamlit" else "⚠️  batch only"
    print(f"   UI: {args.ui} ({streaming_status})")
    if hasattr(args, "enable_rag") and args.enable_rag:
        print("   RAG: enabled")

    try:
        generator = ScaffoldGenerator()
        output_dir = args.output_dir if hasattr(args, "output_dir") and args.output_dir else f"./{args.name}"

        options = {
            "model": args.model,
            "ui": args.ui,
        }

        # Add RAG option if specified (L2 only)
        if hasattr(args, "enable_rag") and args.enable_rag:
            options["enable_rag"] = True

        generator.generate(
            level=args.level,
            name=args.name,
            output_dir=output_dir,
            options=options,
        )
        print("\n✅ Generated successfully!")
        print("\n📋 Next steps:")
        print(f"   1. Test locally:   dat test {output_dir}")
        print(f"   2. Deploy:         cd {output_dir} && databricks bundle deploy")
        print("   3. Run:            databricks bundle run")
        print("   4. View:           Check Databricks Apps UI")
        print(f"\n📖 See {output_dir}/README.md for details")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def handle_test(args):
    """Handle test commands."""
    import os
    import subprocess
    from pathlib import Path

    app_path = Path(args.app_dir).resolve()

    # Check if directory exists
    if not app_path.exists():
        print(f"❌ Directory not found: {app_path}")
        sys.exit(1)

    # Check if it's a valid agent app
    if not (app_path / "start_server.py").exists() and not (app_path / "agent.py").exists():
        print("❌ Not a valid agent directory (missing start_server.py or agent.py)")
        print(f"   Directory: {app_path}")
        sys.exit(1)

    print(f"\n🧪 Testing agent: {app_path.name}")
    print("   Running code validation (no server required)...")
    print()

    # Check if pytest is available
    try:
        subprocess.run(["pytest", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pytest not found. Install it:")
        print("   pip install pytest")
        sys.exit(1)

    # Set environment variable for test
    env = os.environ.copy()
    env["TEST_APP_DIR"] = str(app_path)

    # Run code structure tests (works for all apps - no server needed)
    result = subprocess.run(
        ["pytest", "tests/test_code_structure.py", "-v", "--tb=short"], env=env, cwd=Path(__file__).parent.parent.parent
    )

    print()
    if result.returncode == 0:
        print("✅ Code validation passed!")
        print()
        print("📋 Ready to deploy:")
        print(f"   cd {app_path}")
        print("   databricks bundle deploy")
        print("   databricks bundle run")
    else:
        print("❌ Code validation failed!")
        print()
        print("💡 Fix these issues before deploying:")
        print("   • Using /stream instead of /invocations endpoint")
        print("   • Syntax errors in Python files")
        print("   • Missing required files or configurations")
        sys.exit(1)


if __name__ == "__main__":
    main()
