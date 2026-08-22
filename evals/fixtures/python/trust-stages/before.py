def process(data, verify_token):
    raw = data.removeprefix("Bearer ")
    value = verify_token(raw)
    return {"principal_id": value["sub"]}
