import re
from .utils import URL_RE


def parse_prompt(prompt: str):
    p = prompt.strip()
    url_match = URL_RE.search(p)
    url = url_match.group(0) if url_match else None

    def extract_after(words):
        pattern = r"(?:{})(?:\s*[:=]?\s*)(?:'|\")([^'\"]+)(?:'|\")".format("|".join([re.escape(w) for w in words]))
        m = re.search(pattern, p, re.IGNORECASE)
        return m.group(1) if m else None

    username = extract_after(["username", "user", "email", "login id", "login"])
    password = extract_after(["password", "pass", "pwd", "secret", "pin"])
    return {"url": url, "username": username, "password": password}
