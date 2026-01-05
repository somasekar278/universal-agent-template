"""
Zerobus Telemetry Example

Demonstrates turnkey telemetry integration with Unity Catalog.

Based on: https://github.com/vivian-xie-db/e2e-chatbot-zerobus

What this shows:
- Automatic telemetry setup
- Real-time event streaming to Unity Catalog
- Custom event logging
- Batch processing
- Error resilience

Setup:
  1. Run: agent-telemetry setup --interactive
  2. Run this example: python examples/zerobus_telemetry_example.py
  3. Query: SELECT * FROM catalog.schema.telemetry
"""

import os
import time
from datetime import datetime
from typing import Dict, Any

# ============================================================================
# Example 1: Automatic Agent Telemetry
# ============================================================================

def example_1_automatic_telemetry():
    """
    Agents automatically log telemetry when Zerobus is enabled.

    No code changes needed - just enable in config!
    """
    print("=" * 80)
    print("Example 1: Automatic Agent Telemetry")
    print("=" * 80)
    print()

    from agents.base import Agent
    from shared.schemas import AgentInput, AgentOutput

    class ChatbotAgent(Agent):
        def __init__(self):
            super().__init__(name="chatbot", description="Simple chatbot")

        def process(self, input_data: AgentInput) -> AgentOutput:
            """
            Process request.

            Telemetry automatically logged:
            - Request timestamp
            - Input text
            - Processing time
            - Output text
            - Response timestamp
            """
            # Simulate processing
            time.sleep(0.1)

            response = f"Echo: {input_data.data.get('message', '')}"

            return AgentOutput(
                success=True,
                data={"response": response},
                metadata={"model": "echo-v1"}
            )

    # Create agent
    agent = ChatbotAgent()

    # Process request - telemetry logged automatically!
    input_data = AgentInput(
        request_id="req_001",
        data={"message": "Hello, agent!"}
    )

    result = agent.process(input_data)

    print(f"✅ Request processed: {result.data['response']}")
    print(f"   Telemetry automatically logged to Unity Catalog!")
    print()


# ============================================================================
# Example 2: Custom Event Logging
# ============================================================================

def example_2_custom_events():
    """
    Log custom telemetry events.

    Useful for tracking custom metrics, business events, etc.
    """
    print("=" * 80)
    print("Example 2: Custom Event Logging")
    print("=" * 80)
    print()

    try:
        from telemetry.zerobus_integration import create_zerobus_client, log_agent_event

        # Load config
        import yaml
        from pathlib import Path

        config_file = Path("config/agent_config.yaml")
        if not config_file.exists():
            print("⚠️  Config file not found - using environment variables")
            config = {
                "uc_endpoint": os.getenv("DATABRICKS_HOST"),
                "table": os.getenv("ZEROBUS_TABLE", "catalog.schema.telemetry"),
                "client_id": os.getenv("DATABRICKS_CLIENT_ID"),
                "client_secret": os.getenv("DATABRICKS_CLIENT_SECRET")
            }
        else:
            with open(config_file, 'r') as f:
                full_config = yaml.safe_load(f)
                config = full_config.get("telemetry", {}).get("zerobus", {})

        # Create client
        client = create_zerobus_client(config)

        # Log custom events
        events = [
            {
                "type": "custom_metric",
                "name": "Cache Hit Rate",
                "value": 0.85,
                "unit": "percentage"
            },
            {
                "type": "custom_metric",
                "name": "API Latency",
                "value": 120,
                "unit": "ms"
            },
            {
                "type": "business_event",
                "name": "User Conversion",
                "user_id": "user_123",
                "action": "signed_up"
            }
        ]

        for event in events:
            log_agent_event(
                client=client,
                event_type="custom",
                agent_id="custom_logger",
                data=event
            )
            print(f"✅ Logged: {event.get('name', event.get('type'))}")

        # Flush to ensure delivery
        client.flush()
        print()
        print("✅ All events flushed to Unity Catalog")
        print()

    except ImportError as e:
        print(f"⚠️  Zerobus not configured: {e}")
        print("   Run: agent-telemetry setup --interactive")
        print()


# ============================================================================
# Example 3: Batch Processing with Telemetry
# ============================================================================

def example_3_batch_processing():
    """
    Process many events efficiently with batching.

    Events are automatically batched:
    - Flush every 1000 events (configurable)
    - Or every 10 seconds (configurable)
    """
    print("=" * 80)
    print("Example 3: Batch Processing")
    print("=" * 80)
    print()

    try:
        from telemetry.zerobus_integration import create_zerobus_client
        import yaml
        from pathlib import Path

        # Load config
        config_file = Path("config/agent_config.yaml")
        if not config_file.exists():
            print("⚠️  Config file not found")
            return

        with open(config_file, 'r') as f:
            full_config = yaml.safe_load(f)
            config = full_config.get("telemetry", {}).get("zerobus", {})

        # Create client
        client = create_zerobus_client(config)

        # Process many events
        print("Processing 100 events...")
        start_time = time.time()

        for i in range(100):
            client.log_event({
                "event_type": "batch_process",
                "agent_id": "batch_agent",
                "record_id": f"record_{i:04d}",
                "value": i * 2
            })

        # Force flush
        client.flush()

        elapsed = time.time() - start_time

        print(f"✅ Processed 100 events in {elapsed:.2f}s")
        print(f"   Average: {elapsed/100*1000:.2f}ms per event")
        print()

        print("ℹ️  Events are automatically batched for performance:")
        print(f"   - Batch size: {config.get('batch_size', 1000)} events")
        print(f"   - Flush interval: {config.get('batch_interval_seconds', 10)}s")
        print()

    except Exception as e:
        print(f"⚠️  Error: {e}")
        print()


# ============================================================================
# Example 4: Telemetry with Error Handling
# ============================================================================

def example_4_error_resilience():
    """
    Telemetry is resilient - failures don't crash your agent.

    Features:
    - Automatic retry (3 attempts by default)
    - Exponential backoff (1s, 2s, 4s)
    - Graceful degradation
    """
    print("=" * 80)
    print("Example 4: Error Resilience")
    print("=" * 80)
    print()

    try:
        from telemetry.zerobus_integration import ZerobusClient

        # Create client with intentionally bad config
        bad_config = {
            "uc_endpoint": "https://invalid.databricks.com",
            "table": "invalid.table",
            "client_id": "invalid",
            "client_secret": "invalid",
            "max_retries": 3
        }

        client = ZerobusClient(bad_config)

        print("Attempting to log event with invalid config...")

        # Try to log - will fail gracefully
        success = client.log_event({
            "event_type": "test",
            "agent_id": "test_agent",
            "message": "This will fail"
        })

        if not success:
            print("❌ Event logging failed (as expected)")
            print("✅ But the agent didn't crash!")
            print()
            print("ℹ️  Telemetry failures are non-fatal:")
            print("   - Your agent continues running")
            print("   - Automatic retry with backoff")
            print("   - Events buffered in memory")
            print()

    except Exception as e:
        print(f"⚠️  Error: {e}")
        print()


# ============================================================================
# Example 5: Query Telemetry from Python
# ============================================================================

def example_5_query_telemetry():
    """
    Query telemetry data from Unity Catalog.

    Use Databricks SQL connector to analyze telemetry.
    """
    print("=" * 80)
    print("Example 5: Query Telemetry")
    print("=" * 80)
    print()

    try:
        from databricks import sql
        import os

        # Connect to Databricks
        connection = sql.connect(
            server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
            http_path=os.getenv("DATABRICKS_HTTP_PATH"),
            access_token=os.getenv("DATABRICKS_TOKEN")
        )

        cursor = connection.cursor()

        # Query recent events
        table = os.getenv("ZEROBUS_TABLE", "catalog.schema.telemetry")

        query = f"""
        SELECT
            timestamp,
            event_type,
            agent_id,
            COUNT(*) as count
        FROM {table}
        WHERE timestamp > current_timestamp() - INTERVAL 1 HOUR
        GROUP BY timestamp, event_type, agent_id
        ORDER BY timestamp DESC
        LIMIT 10
        """

        print(f"Querying: {table}")
        print()

        cursor.execute(query)

        print(f"{'Timestamp':<20} {'Event Type':<15} {'Agent ID':<20} {'Count':<10}")
        print("-" * 70)

        for row in cursor.fetchall():
            print(f"{str(row[0]):<20} {row[1]:<15} {row[2]:<20} {row[3]:<10}")

        print()
        print("✅ Query complete")
        print()

        cursor.close()
        connection.close()

    except ImportError:
        print("⚠️  databricks-sql-connector not installed")
        print("   Install with: pip install databricks-sql-connector")
        print()
    except Exception as e:
        print(f"⚠️  Query failed: {e}")
        print()
        print("   Query telemetry in Databricks SQL instead:")
        print(f"   SELECT * FROM {os.getenv('ZEROBUS_TABLE', 'catalog.schema.telemetry')} LIMIT 10;")
        print()


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print()
    print("🎯 Zerobus Telemetry Examples")
    print("=" * 80)
    print()
    print("These examples demonstrate turnkey telemetry with Unity Catalog.")
    print()
    print("Prerequisites:")
    print("  1. Run: agent-telemetry setup --interactive")
    print("  2. Ensure config/agent_config.yaml has zerobus.enabled: true")
    print()
    print("=" * 80)
    print()

    # Run examples
    try:
        example_1_automatic_telemetry()
        example_2_custom_events()
        example_3_batch_processing()
        example_4_error_resilience()
        example_5_query_telemetry()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 80)
    print("✅ Examples Complete")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Query telemetry in Databricks SQL")
    print("  2. Build dashboards")
    print("  3. Set up alerts")
    print()
    print("📚 Documentation: docs/TELEMETRY.md")
    print()
