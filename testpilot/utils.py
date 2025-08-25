import re
from urllib.parse import urlparse

USERNAME_HINTS = ["user", "username", "email", "e-mail", "mail", "login", "id", "account", "mobile", "phone"]
PASSWORD_HINTS = ["pass", "passwd", "password", "pwd", "secret", "pin"]
LOGIN_TEXT_HINTS = ["login", "log in", "sign in", "signin", "submit", "continue", "next"]


def contains_any(text, hints):
    t = (text or "").lower()
    return any(h in t for h in hints)


def safe(s):
    return (s or "").strip()


def normalize_url(u: str):
    if not u: return None
    parts = urlparse(u)
    return u if parts.scheme else "https://" + u


URL_RE = re.compile(r'https?://[^\s"\'<>]+', re.IGNORECASE)
