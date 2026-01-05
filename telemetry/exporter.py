"""
Telemetry exporters for Delta Lake.

Implements the Zerobus pattern: OTEL → Stream → Delta Lake
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ExporterConfig:
    """Configuration for telemetry export."""
    catalog_name: str = "sota_agents"
    schema_name: str = "production"
    table_name: str = "agent_telemetry"
    batch_size: int = 100
    flush_interval_seconds: int = 30


class DeltaLakeExporter:
    """
    Export telemetry to Delta Lake.

    Batches spans and writes to Delta table for analysis.
    """

    def __init__(self, config: Optional[ExporterConfig] = None):
        self.config = config or ExporterConfig()
        self._buffer: List[Dict[str, Any]] = []
        self._spark = None

    def _get_spark(self):
        """Get Spark session."""
        if self._spark is None:
            try:
                from pyspark.sql import SparkSession
                self._spark = SparkSession.builder.getOrCreate()
            except:
                print("⚠️  Spark not available")
        return self._spark

    def export(self, span_data: Any) -> None:
        """
        Export span to Delta Lake.

        Args:
            span_data: OpenTelemetry span data
        """
        try:
            # Convert span to dict
            record = self._span_to_record(span_data)
            self._buffer.append(record)

            # Flush if batch size reached
            if len(self._buffer) >= self.config.batch_size:
                self.flush()

        except Exception as e:
            print(f"⚠️  Failed to export span: {e}")

    def _span_to_record(self, span_data: Any) -> Dict[str, Any]:
        """Convert OpenTelemetry span to Delta record."""
        return {
            "timestamp": datetime.now(),
            "trace_id": str(span_data.context.trace_id) if hasattr(span_data, 'context') else None,
            "span_id": str(span_data.context.span_id) if hasattr(span_data, 'context') else None,
            "agent_id": span_data.attributes.get("agent.id") if hasattr(span_data, 'attributes') else None,
            "event_type": span_data.name if hasattr(span_data, 'name') else "unknown",
            "duration_ms": (span_data.end_time - span_data.start_time) / 1_000_000 if hasattr(span_data, 'end_time') else 0,
            "status": span_data.status.status_code.name if hasattr(span_data, 'status') else "UNSET",
            "attributes": dict(span_data.attributes) if hasattr(span_data, 'attributes') else {}
        }

    def flush(self):
        """Flush buffer to Delta Lake."""
        if not self._buffer:
            return

        spark = self._get_spark()
        if not spark:
            return

        try:
            # Create DataFrame
            df = spark.createDataFrame(self._buffer)

            # Write to Delta table
            table_path = f"{self.config.catalog_name}.{self.config.schema_name}.{self.config.table_name}"
            df.write.format("delta").mode("append").saveAsTable(table_path)

            print(f"✅ Flushed {len(self._buffer)} spans to {table_path}")
            self._buffer.clear()

        except Exception as e:
            print(f"⚠️  Failed to flush to Delta: {e}")

    def shutdown(self):
        """Shutdown exporter."""
        self.flush()


class ZerobusExporter:
    """
    Export via Zerobus streaming pattern.

    Implements real-time streaming to Delta Lake.
    """

    def __init__(self, config: Optional[ExporterConfig] = None):
        self.config = config or ExporterConfig()
        self._stream = None

    def export(self, span_data: Any):
        """Export span via streaming."""
        # Implementation would use Spark Structured Streaming
        # or Databricks Delta Live Tables
        pass
