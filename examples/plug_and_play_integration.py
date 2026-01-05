"""
Example: Plug-and-play integration into existing fraud pipeline.

Shows how customers add agents to their existing Databricks Workflow
with minimal code changes.
"""

import asyncio
from typing import List, Dict, Any

# Customer's existing imports (unchanged)
from pyspark.sql import DataFrame, SparkSession

# Our library (added)
from agents import AgentRouter
from shared.schemas import AgentInput, Transaction


# ==============================================================================
# BEFORE: Customer's existing fraud pipeline (Databricks Workflow job)
# ==============================================================================

def existing_fraud_pipeline_BEFORE(spark: SparkSession):
    """
    Customer's existing pipeline WITHOUT agents.

    Typical flow:
    1. Load transactions
    2. Engineer features
    3. ML scoring
    4. Apply business rules
    5. Write results
    """

    # Step 1: Load transactions
    transactions = spark.table("raw.transactions")

    # Step 2: Feature engineering
    features = engineer_features(transactions)

    # Step 3: ML scoring (their existing model)
    scores = ml_model_predict(features)

    # Step 4: Business rules
    decisions = apply_business_rules(scores)

    # Step 5: Write results
    decisions.write.mode("append").saveAsTable("fraud.decisions")

    print("Pipeline complete!")


# ==============================================================================
# AFTER: Customer's pipeline WITH agents (plug-and-play!)
# ==============================================================================

def fraud_pipeline_with_agents_AFTER(spark: SparkSession):
    """
    Customer's pipeline WITH agents - only 3 lines added!

    New flow:
    1. Load transactions (unchanged)
    2. Engineer features (unchanged)
    3. ML scoring (unchanged)
    4. >>> ADD AGENTS HERE (3 lines!) <<<
    5. Apply business rules (unchanged)
    6. Write results (unchanged)
    """

    # Step 1-3: Existing code (UNCHANGED)
    transactions = spark.table("raw.transactions")
    features = engineer_features(transactions)
    scores = ml_model_predict(features)

    # ========================================
    # NEW: Add agents (3 lines!)
    # ========================================
    router = AgentRouter.from_yaml("config/agents.yaml")  # 1. Load config
    enriched = asyncio.run(                                # 2. Enrich
        enrich_with_agents(scores, router)
    )
    # ========================================

    # Step 4-5: Existing code (UNCHANGED)
    decisions = apply_business_rules(enriched)
    decisions.write.mode("append").saveAsTable("fraud.decisions")

    print("Pipeline complete with agents!")


async def enrich_with_agents(
    scores: DataFrame,
    router: AgentRouter
) -> DataFrame:
    """
    Enrich scores with agent outputs.

    This helper function:
    - Converts DataFrame rows to AgentInput (Pydantic)
    - Routes to appropriate agents based on config
    - Handles inline vs async execution
    - Returns enriched DataFrame
    """

    enriched_rows = []

    for row in scores.collect():
        # Convert to AgentInput (Pydantic validates!)
        agent_input = AgentInput(
            request_id=row.transaction_id,
            transaction=Transaction(
                id=row.transaction_id,
                timestamp=row.timestamp,
                amount=row.amount,
                currency=row.currency,
                # ... map other fields
            ),
            # ... other contexts
        )

        # Get risk score from ML model
        risk_score = row.risk_score

        # Determine which agents to run based on config
        # (Config specifies thresholds for each agent)

        # Example: Run narrative agent for high-risk only
        if risk_score > 0.7:
            try:
                # Router handles execution mode (inline vs async) automatically!
                result = await router.route("narrative", agent_input)

                # Add agent output to row
                enriched_row = {
                    **row.asDict(),
                    "narrative": result.risk_narrative,
                    "agent_confidence": result.confidence_score,
                }
            except Exception as e:
                print(f"Agent failed for {row.transaction_id}: {e}")
                enriched_row = {
                    **row.asDict(),
                    "narrative": None,
                    "agent_confidence": None,
                }
        else:
            # Low risk - no enrichment needed
            enriched_row = row.asDict()

        enriched_rows.append(enriched_row)

    # Convert back to DataFrame
    spark = SparkSession.getActiveSession()
    return spark.createDataFrame(enriched_rows)


# ==============================================================================
# Configuration-driven behavior (no code changes!)
# ==============================================================================

def same_code_different_behavior():
    """
    Shows how customers control agent behavior via config ONLY.

    NO CODE CHANGES - just switch config file!
    """

    # Scenario 1: Tight SLA (50ms) - only inline agents
    # config/tight_sla.yaml:
    #   agents:
    #     fast_scorer:
    #       execution_mode: "inline"

    router_tight = AgentRouter.from_yaml("config/tight_sla.yaml")
    # All agents run inline (fast!)

    # Scenario 2: Relaxed SLA - can use async agents
    # config/relaxed_sla.yaml:
    #   agents:
    #     narrative:
    #       execution_mode: "async"

    router_relaxed = AgentRouter.from_yaml("config/relaxed_sla.yaml")
    # Slow agents run async (doesn't block pipeline)

    # Scenario 3: A/B testing - enable/disable agents
    # config/ab_test.yaml:
    #   agents:
    #     narrative:
    #       enabled: false  # Disabled for test

    router_ab = AgentRouter.from_yaml("config/ab_test.yaml")
    # Agent won't run (A/B test)

    # SAME CODE - different behavior based on config!
    # No deployment needed, just change YAML!


# ==============================================================================
# Helper functions (customer's existing code - unchanged)
# ==============================================================================

def engineer_features(df: DataFrame) -> DataFrame:
    """Customer's existing feature engineering."""
    # ... their code ...
    return df

def ml_model_predict(df: DataFrame) -> DataFrame:
    """Customer's existing ML model."""
    # ... their code ...
    return df

def apply_business_rules(df: DataFrame) -> DataFrame:
    """Customer's existing business rules."""
    # ... their code ...
    return df


# ==============================================================================
# Summary: What changed?
# ==============================================================================

"""
BEFORE (existing pipeline):
- transactions = load()
- features = engineer(transactions)
- scores = ml_model(features)
- decisions = rules(scores)
- write(decisions)

AFTER (with agents):
- transactions = load()
- features = engineer(transactions)
- scores = ml_model(features)
+ router = AgentRouter.from_yaml("config.yaml")  # ADD 1 line
+ enriched = enrich_with_agents(scores, router)   # ADD 1 line
- decisions = rules(enriched)                     # CHANGE 1 line
- write(decisions)

Total changes: 3 lines!

Benefits:
✅ Plug-and-play - minimal code changes
✅ Config-driven - no code changes to enable/disable agents
✅ SLA-aware - customer controls inline vs async
✅ Type-safe - Pydantic validates all data
✅ Flexible - works with any existing pipeline
"""


if __name__ == "__main__":
    # Example: Load router from config
    router = AgentRouter.from_yaml("config/agents/example_basic.yaml")

    print("✅ Agents loaded from config!")
    print(f"Registered agents: {list(router.registry.list_agents().keys())}")
