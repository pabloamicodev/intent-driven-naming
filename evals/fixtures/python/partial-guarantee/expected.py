def authorize_user(raw_user, should_validate, validate, authorize):
    user_for_authorization = validate(raw_user) if should_validate else raw_user
    return authorize(user_for_authorization)
