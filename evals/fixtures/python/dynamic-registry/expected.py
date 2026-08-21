def handle_payment_succeeded(event_payload):
    return event_payload["payment_id"]


handlers = {"payment.succeeded": handle_payment_succeeded}
