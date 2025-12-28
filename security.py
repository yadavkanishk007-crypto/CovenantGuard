from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

MAX_PASSWORD_LENGTH = 72


def _normalize_password(password: str) -> str:
    # bcrypt hard limit protection
    if len(password.encode("utf-8")) > MAX_PASSWORD_LENGTH:
        password = password.encode("utf-8")[:MAX_PASSWORD_LENGTH].decode("utf-8", errors="ignore")
    return password


def hash_password(password: str) -> str:
    password = _normalize_password(password)
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    password = _normalize_password(password)
    return pwd_context.verify(password, hashed)
