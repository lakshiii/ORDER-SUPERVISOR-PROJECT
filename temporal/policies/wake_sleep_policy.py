from dataclasses import dataclass

@dataclass
class WakeSleepDecision:
    decision: str  # "wake" or "sleep"
    reason: str
    event_type: str
    priority: str  # "high" or "low"

# Controlled policy rules mapping
POLICY_RULES = {
    "order_created": {
        "decision": "wake",
        "priority": "high",
        "reason": "New order created; requires initial supervisor assessment and tracking setup.",
    },
    "payment_failed": {
        "decision": "wake",
        "priority": "high",
        "reason": "Payment failed; requires immediate intervention or payment recovery workflow.",
    },
    "shipment_delayed": {
        "decision": "wake",
        "priority": "high",
        "reason": "Shipment delay reported; requires proactive carrier tracking and customer notice.",
    },
    "delivered": {
        "decision": "wake",
        "priority": "high",
        "reason": "Order delivered; terminal lifecycle event requires final run completion.",
    },
    "refund_requested": {
        "decision": "wake",
        "priority": "high",
        "reason": "Refund requested by customer; requires supervisor approval or support escalation.",
    },
    "customer_message_received": {
        "decision": "wake",
        "priority": "high",
        "reason": "Inbound customer inquiry received; requires timely supervisor response.",
    },
    "payment_confirmed": {
        "decision": "sleep",
        "priority": "low",
        "reason": "Payment confirmed successfully; normal lifecycle progress recorded.",
    },
    "shipment_created": {
        "decision": "sleep",
        "priority": "low",
        "reason": "Shipment created successfully; normal fulfillment progress recorded.",
    },
    "no_update_for_n_hours": {
        "decision": "sleep",
        "priority": "low",
        "reason": "Periodic quiet period timer expired; no anomaly detected.",
    },
}

def evaluate_wake_sleep_policy(event_type: str) -> WakeSleepDecision:
    """
    Pure, deterministic evaluation function for Wake/Sleep Policy decisions.
    
    Guarantees Temporal workflow determinism:
    - No network I/O
    - No database calls
    - No wall-clock time dependencies outside Temporal APIs
    - No random behavior
    """
    event_type_clean = event_type.strip().lower() if event_type else ""

    rule = POLICY_RULES.get(event_type_clean)
    if rule:
        return WakeSleepDecision(
            decision=rule["decision"],
            reason=rule["reason"],
            event_type=event_type_clean,
            priority=rule["priority"],
        )

    # Safe fallback for unknown event types
    return WakeSleepDecision(
        decision="wake",
        reason=f"Unrecognized event type '{event_type}'; defaulting to wake for supervisor safety.",
        event_type=event_type_clean,
        priority="high",
    )
