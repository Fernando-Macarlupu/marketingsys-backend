from django.contrib.auth.hashers import check_password, is_password_usable, make_password


def hash_password(raw_password: str) -> str:
    return make_password(raw_password)


def verify_password(raw_password: str, stored_password: str) -> bool:
    if not stored_password:
        return False
    if is_password_usable(stored_password):
        return check_password(raw_password, stored_password)
    return raw_password == stored_password


def ensure_hashed(raw_password: str) -> str:
    if is_password_usable(raw_password):
        return raw_password
    return make_password(raw_password)
