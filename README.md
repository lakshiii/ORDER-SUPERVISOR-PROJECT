# ORDER-SUPERVISOR-PROJECT
Order Supervisor is an AI-driven supervisor system for order lifecycle management. For every order, the system launches a long-running Temporal workflow (`order-supervisor-{order_id}`). Incoming events enter as signals, prompting the AI supervisor to evaluate history, take simulated business actions, schedule wake-ups, or sleep until needed.
