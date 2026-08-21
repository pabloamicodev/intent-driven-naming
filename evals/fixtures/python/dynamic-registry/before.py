def do(data):
    return data["payment_id"]


handlers = {"payment.succeeded": do}
