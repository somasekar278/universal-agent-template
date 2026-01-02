"""
Main CLI entry point for Agent Framework.

Provides overview of all available commands and pathways.
"""

import argparse
import sys


def main():
    """Main entry point showing all available commands."""
    
    parser = argparse.ArgumentParser(
        prog="agent",
        description="Agent Framework - Universal template for AI agent workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Commands:
  
  🎓 LEARNING & GETTING STARTED
  ────────────────────────────────────────────────────────────────
  agent-learn              Interactive learning mode (5 progressive levels)
                           • Level 1: Simple Chatbot (2-4 hrs)
                           • Level 2: Context-Aware Assistant (4-8 hrs)
                           • Level 3: Production API (8-16 hrs)
                           • Level 4: Complex Workflow (16-32 hrs)
                           • Level 5: Multi-Agent System (32-64 hrs)
                           
                           Examples:
                             agent-learn info 1        # Learn about Level 1
                             agent-learn start 2       # Start Level 2 project
                             agent-learn overview      # See all levels
  
  🎯 PROJECT SETUP & GENERATION
  ────────────────────────────────────────────────────────────────
  agent-setup              Interactive setup wizard
                           Guides you through feature selection based on use case
                           
                           Example:
                             agent-setup
  
  agent-generate           Generate new agent project
                           Quick scaffold for any domain
                           
                           Examples:
                             agent-generate --domain fraud_detection
                             agent-generate --domain customer_support --output ./my-agent
  
  🤖 ARCHITECTURE & PLANNING
  ────────────────────────────────────────────────────────────────
  agent-architect          AI-powered architecture recommendations
                           Analyzes your brief and recommends optimal architecture
                           
                           Examples:
                             agent-architect "Build a chatbot with memory"
                             agent-architect -f brief.pdf           # From document
                             agent-architect -f brief.docx --select # Interactive selection
  
  agent-advisor            Analyze existing project
                           Get recommendations for improvements
                           
                           Example:
                             agent-advisor ./my-project
  
  📊 TESTING & BENCHMARKING
  ────────────────────────────────────────────────────────────────
  agent-benchmark          Run benchmarks and evaluations
                           Test agent performance with comprehensive metrics
                           
                           Examples:
                             agent-benchmark run --suite fraud_detection
                             agent-benchmark create --suite my_suite
                             agent-benchmark run --agents all --report html
  
  🚀 DEPLOYMENT
  ────────────────────────────────────────────────────────────────
  agent-deploy             Deployment management
                           Generate configs for Docker, K8s, Databricks, Serverless
                           
                           Examples:
                             agent-deploy init --platform kubernetes
                             agent-deploy build --tag v1.0.0
                             agent-deploy status

Quick Start Pathways:
  
  🌱 New to Agents? Start here:
     1. agent-learn overview          # Understand the 5 levels
     2. agent-learn start 1           # Build your first chatbot
     3. agent-learn start 2           # Add memory and context
  
  🔧 Have a use case? Go interactive:
     1. agent-architect "Your use case description"
     2. agent-setup                   # Configure features
     3. agent-generate your_project   # Generate scaffold
  
  📄 Have a document/brief?
     1. agent-architect -f your_brief.pdf --select
     2. Follow recommendations to generate project

For detailed help on any command:
  agent-<command> --help

Documentation: https://github.com/somasekar278/universal-agent-template
PyPI: https://pypi.org/project/sota-agent-framework/
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Agent Framework 0.4.3"
    )
    
    # If no arguments, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # Should never reach here as we handle --version and no args above
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

