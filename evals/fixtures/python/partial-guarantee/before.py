def authorize_user(raw_user, should_validate, validate, authorize):
    validated_user = validate(raw_user) if should_validate else raw_user
    return authorize(validated_user)
