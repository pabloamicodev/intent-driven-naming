def authenticate_authorization_header(untrusted_authorization_header, verify_token):
    untrusted_token = untrusted_authorization_header.removeprefix("Bearer ")
    verified_token_claims = verify_token(untrusted_token)
    return {"principal_id": verified_token_claims["sub"]}
