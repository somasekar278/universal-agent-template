"""
Example usage of data schemas.

This module demonstrates how to create and use the core data structures
for the fraud detection system.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from shared.schemas import (
    Transaction,
    PaymentMethod,
    FraudLabel,
    FraudSignals,
    VelocitySignal,
    AmountAnomalySignal,
    LocationSignal,
    DeviceSignal,
    MerchantContext,
    CustomerContext,
    MerchantRiskTier,
    AgentInput,
    AgentOutput,
    AgentAction,
    ReasoningStep,
    ToolCall,
    ToolResult,
)


def create_example_transaction() -> Transaction:
    """Create an example high-risk transaction."""
    return Transaction(
        transaction_id="txn_example_001",
        merchant_id="mch_electronics_uk",
        customer_id="cust_new_user_123",
        timestamp=datetime.utcnow(),
        amount=Decimal("1299.99"),
        currency="GBP",
        payment_method=PaymentMethod.CARD,
        fraud_label=FraudLabel.UNKNOWN,
        ml_risk_score=0.78,
        device_fingerprint="fp_new_device_xyz",
        ip_address="185.220.101.42",
        country_code="RO",
        city="Bucharest",
        latitude=44.4268,
        longitude=26.1025,
    )


def create_example_fraud_signals() -> FraudSignals:
    """Create example fraud signals showing high-risk patterns."""
    return FraudSignals(
        transaction_id="txn_example_001",
        velocity=VelocitySignal(
            transactions_last_hour=5,
            transactions_last_day=12,
            transactions_last_week=15,
            total_amount_last_hour=Decimal("4200.00"),
            total_amount_last_day=Decimal("8950.00"),
            unique_merchants_last_day=7,
            unique_countries_last_day=3,
            is_velocity_anomaly=True,
            velocity_score=0.89,
        ),
        amount_anomaly=AmountAnomalySignal(
            customer_avg_transaction=Decimal("85.50"),
            customer_max_transaction=Decimal("249.99"),
            merchant_avg_transaction=Decimal("425.00"),
            is_amount_anomaly=True,
            amount_z_score=4.2,
            amount_percentile=98.5,
        ),
        location=LocationSignal(
            customer_home_country="GB",
            customer_recent_countries=["GB", "FR"],
            distance_from_last_transaction_km=2100.0,
            time_since_last_transaction_seconds=1800.0,
            is_location_mismatch=True,
            is_impossible_travel=True,
            location_risk_score=0.92,
        ),
        device=DeviceSignal(
            device_id="fp_new_device_xyz",
            is_new_device=True,
            device_age_days=0,
            device_transaction_count=1,
            device_customer_count=1,
            is_device_anomaly=True,
            is_device_shared=False,
            device_risk_score=0.75,
        ),
        rules_triggered=[
            "HIGH_VELOCITY",
            "AMOUNT_ANOMALY",
            "LOCATION_MISMATCH",
            "IMPOSSIBLE_TRAVEL",
            "NEW_DEVICE",
        ],
        overall_signal_strength=0.87,
    )


def create_example_merchant_context() -> MerchantContext:
    """Create example merchant context."""
    return MerchantContext(
        merchant_id="mch_electronics_uk",
        business_name="TechGear Electronics Ltd",
        merchant_category="electronics_retail",
        risk_tier=MerchantRiskTier.MEDIUM,
        account_created_at=datetime.utcnow() - timedelta(days=450),
        account_age_days=450,
        is_verified=True,
        total_transactions=12450,
        total_volume=Decimal("4250000.00"),
        avg_transaction_amount=Decimal("341.37"),
        chargeback_count=48,
        chargeback_rate=0.0039,
        fraud_incident_count=12,
        primary_countries=["GB", "IE", "FR"],
        transactions_last_30_days=850,
        volume_last_30_days=Decimal("285000.00"),
    )


def create_example_customer_context() -> CustomerContext:
    """Create example customer context showing new, unverified account."""
    return CustomerContext(
        customer_id="cust_new_user_123",
        account_created_at=datetime.utcnow() - timedelta(days=2),
        account_age_days=2,
        email_verified=False,
        phone_verified=False,
        total_transactions=12,
        successful_transactions=10,
        declined_transactions=2,
        total_spend=Decimal("8950.00"),
        avg_transaction_amount=Decimal("745.83"),
        max_transaction_amount=Decimal("1499.99"),
        preferred_payment_methods=["card"],
        transaction_countries=["GB", "FR", "RO"],
        home_country="GB",
        known_devices=2,
        known_ip_addresses=4,
        fraud_incidents=0,
        disputes_filed=0,
        chargebacks=0,
        last_transaction_at=datetime.utcnow() - timedelta(minutes=30),
        transactions_last_30_days=12,
        spend_last_30_days=Decimal("8950.00"),
    )


def create_example_agent_input() -> AgentInput:
    """Create complete agent input with all context."""
    return AgentInput(
        request_id="req_example_001",
        transaction=create_example_transaction(),
        fraud_signals=create_example_fraud_signals(),
        merchant_context=create_example_merchant_context(),
        customer_context=create_example_customer_context(),
    )


def create_example_agent_output() -> AgentOutput:
    """Create example agent output with reasoning trace."""
    start_time = datetime.utcnow() - timedelta(milliseconds=245)
    
    # Example tool calls
    tool_call_1 = ToolCall(
        tool_id="call_001",
        tool_name="merchant_context",
        tool_server="uc-query-server",
        arguments={"merchant_id": "mch_electronics_uk"},
        called_at=start_time + timedelta(milliseconds=10),
    )
    
    tool_result_1 = ToolResult(
        tool_call_id="call_001",
        success=True,
        result={"chargeback_rate": 0.0039, "risk_tier": "medium"},
        latency_ms=42.5,
        completed_at=start_time + timedelta(milliseconds=52.5),
    )
    
    tool_call_2 = ToolCall(
        tool_id="call_002",
        tool_name="velocity_check",
        tool_server="risk-calculation-server",
        arguments={"customer_id": "cust_new_user_123", "time_window": "1h"},
        called_at=start_time + timedelta(milliseconds=60),
    )
    
    tool_result_2 = ToolResult(
        tool_call_id="call_002",
        success=True,
        result={"transactions": 5, "total_amount": 4200.0, "is_anomaly": True},
        latency_ms=38.2,
        completed_at=start_time + timedelta(milliseconds=98.2),
    )
    
    # Reasoning steps
    reasoning_steps = [
        ReasoningStep(
            step_number=1,
            thought="I need to fetch merchant context to understand their typical transaction patterns and risk profile.",
            tool_call=tool_call_1,
            tool_result=tool_result_1,
            timestamp=start_time + timedelta(milliseconds=10),
        ),
        ReasoningStep(
            step_number=2,
            thought="Merchant has medium risk tier with acceptable chargeback rate. Now checking customer velocity patterns.",
            tool_call=tool_call_2,
            tool_result=tool_result_2,
            timestamp=start_time + timedelta(milliseconds=60),
        ),
        ReasoningStep(
            step_number=3,
            thought="Customer shows highly suspicious velocity: 5 transactions in 1 hour totaling £4200. Account is only 2 days old and unverified.",
            timestamp=start_time + timedelta(milliseconds=120),
        ),
        ReasoningStep(
            step_number=4,
            thought="Transaction amount (£1299.99) is 15x customer's average. Location jumped from GB to Romania in 30 minutes - impossible travel detected.",
            timestamp=start_time + timedelta(milliseconds=180),
        ),
        ReasoningStep(
            step_number=5,
            thought="Multiple high-risk signals: velocity anomaly, impossible travel, new unverified device, amount anomaly. Strong fraud indicators. Recommending manual review.",
            timestamp=start_time + timedelta(milliseconds=220),
        ),
    ]
    
    return AgentOutput(
        request_id="req_example_001",
        agent_id="agent_narrative_ephemeral_42",
        risk_narrative=(
            "HIGH RISK - Manual Review Required. "
            "This transaction exhibits multiple critical fraud indicators: "
            "(1) Severe velocity anomaly - 5 transactions in 1 hour from 2-day-old account; "
            "(2) Impossible travel - location changed from GB to Romania within 30 minutes; "
            "(3) Significant amount anomaly - £1299.99 is 15x above customer's typical £85 spend; "
            "(4) New unverified device from foreign country. "
            "Customer account shows unverified email/phone with rapid high-value spending pattern. "
            "Strong likelihood of account takeover or card testing. "
            "Recommend immediate manual review and customer verification before approval."
        ),
        recommended_action=AgentAction.REVIEW,
        confidence_score=0.92,
        risk_score=0.87,
        reasoning_steps=reasoning_steps,
        tools_called=["merchant_context", "velocity_check"],
        started_at=start_time,
        completed_at=datetime.utcnow(),
        latency_ms=245.3,
        model_name="meta-llama-3.1-70b-instruct",
        prompt_tokens=1850,
        completion_tokens=185,
    )


def demo_full_flow():
    """Demonstrate complete agent flow from input to output."""
    print("=" * 80)
    print("FRAUD DETECTION AGENT - EXAMPLE FLOW")
    print("=" * 80)
    
    # Create agent input
    agent_input = create_example_agent_input()
    print("\n📥 AGENT INPUT")
    print(f"Transaction ID: {agent_input.transaction.transaction_id}")
    print(f"Amount: {agent_input.transaction.amount} {agent_input.transaction.currency}")
    print(f"ML Risk Score: {agent_input.transaction.ml_risk_score:.2f}")
    print(f"Fraud Signals: {len(agent_input.fraud_signals.rules_triggered)} rules triggered")
    print(f"Rules: {', '.join(agent_input.fraud_signals.rules_triggered)}")
    
    # Create agent output
    agent_output = create_example_agent_output()
    print("\n📤 AGENT OUTPUT")
    print(f"Agent ID: {agent_output.agent_id}")
    print(f"Action: {agent_output.recommended_action.value}")
    print(f"Risk Score: {agent_output.risk_score:.2f}")
    print(f"Confidence: {agent_output.confidence_score:.2f}")
    print(f"Latency: {agent_output.latency_ms:.1f}ms")
    print(f"Tools Used: {', '.join(agent_output.tools_called)}")
    print(f"\n📝 RISK NARRATIVE:")
    print(agent_output.risk_narrative)
    
    print("\n🔍 REASONING TRACE:")
    for step in agent_output.reasoning_steps:
        print(f"\nStep {step.step_number}:")
        print(f"  Thought: {step.thought}")
        if step.tool_call:
            print(f"  Tool: {step.tool_call.tool_name} (server: {step.tool_call.tool_server})")
        if step.tool_result:
            print(f"  Result: Success={step.tool_result.success}, Latency={step.tool_result.latency_ms:.1f}ms")
    
    print("\n" + "=" * 80)
    print("✅ FLOW COMPLETE - Ready for MLflow logging and Zerobus telemetry")
    print("=" * 80)


if __name__ == "__main__":
    demo_full_flow()

