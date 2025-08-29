import re

# URL: stop at whitespace, quotes, comma, or ')'
URL_RE = re.compile(r"https?://[^\s'\",)]+", re.IGNORECASE)

# Verbs that commonly precede credential instructions
VERBS = r"(?:enter|enters|type|types|use|uses|with|as|set|sets|provide|provides|supply|supplies|login with|log in with)"

# NOTE: deliberately exclude plain "user" to avoid matching "user navigates..."
USERNAME_KEYS = ["username", "user name", "email", "e-mail", "login", "login id"]
PASSWORD_KEYS = ["password", "pass", "pwd", "secret", "pin"]

# Token patterns
UNQUOTED_VAL = r"([A-Za-z0-9._%+\-@/]+)"
QUOTED_VAL = r"['\"]([^'^\"]+)['\"]"
VAL = rf"(?:{QUOTED_VAL}|{UNQUOTED_VAL})"  # group(1) if quoted, else group(2)


def _extract_value(text: str, keywords):
    """
    Extract the value that follows any of the keywords.
    Handles both quoted and unquoted values.
    Order-agnostic: just finds the first occurrence.
    """
    t = " ".join(text.split())
    kw = r"(?:%s)" % "|".join([re.escape(k) for k in keywords])

    # 1) VERB ... KEYWORD ... VALUE
    pat1 = re.compile(rf"\b{VERBS}\b[^\"']{{0,80}}?\b{kw}\b[^\"']{{0,40}}?{VAL}", re.IGNORECASE)
    matches = list(pat1.finditer(t))
    if matches:
        m = min(matches, key=lambda x: x.start())  # pick earliest match
        return (m.group(1) or m.group(2)).strip()

    # 2) KEYWORD ... VALUE
    pat2 = re.compile(rf"\b{kw}\b[^\"']{{0,40}}?{VAL}", re.IGNORECASE)
    matches = list(pat2.finditer(t))
    if matches:
        m = min(matches, key=lambda x: x.start())
        return (m.group(1) or m.group(2)).strip()

    return None


def parse_prompt(prompt: str):
    p = prompt.strip()

    # URL
    url_match = URL_RE.search(p)
    url = url_match.group(0) if url_match else None

    # Remove URL (and surrounding quotes) before credential extraction
    text_wo_url = p
    if url:
        text_wo_url = re.sub(r"['\"]?" + re.escape(url) + r"['\"]?", " ", p)

    username = _extract_value(text_wo_url, USERNAME_KEYS)
    password = _extract_value(text_wo_url, PASSWORD_KEYS)

    return {"url": url, "username": username, "password": password}
