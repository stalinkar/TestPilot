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


# --- Multi-step parsing: additive, non-breaking ---

# Split on commas/semicolons and simple coordinators
SPLIT_RE = re.compile(r"\s*(?:,|;|\band then\b|\bthen\b|\band\b)\s*", re.IGNORECASE)


def split_into_steps(prompt: str):
    parts = [p.strip() for p in SPLIT_RE.split(prompt or "") if p and p.strip()]
    return parts


def parse_step(step: str):
    """
    Lightweight intent detector. Uses lowercase only for detection,
    extracts values from the ORIGINAL 'step' to preserve case.
    """
    s = step.lower()

    # login
    if "login" in s or "log in" in s:
        # try to extract user if present
        m = re.search(r"user\s+([A-Za-z0-9._%+\-@]+)", step, re.IGNORECASE)
        username = m.group(1) if m else None
        return {"action": "login", "params": {"username": username}}

    # navigate → profile
    if "profile" in s and ("go to" in s or "navigate" in s or "open" in s):
        return {"action": "navigate", "params": {"page": "profile"}}

    # update bio
    if "update" in s and "bio" in s:
        m = re.search(r"bio\s*(?:to|as|=)\s*(.+)", step, re.IGNORECASE)
        value = m.group(1).strip() if m else None
        return {"action": "update", "params": {"field": "bio", "value": value}}

    # logout
    if "logout" in s or "log out" in s or "sign out" in s:
        return {"action": "logout", "params": {}}

    # search
    if s.startswith("search") or "search for" in s:
        m = re.search(r"search\s+(?:for\s+)?['\"]?([^'\"\n]+)['\"]?", step, re.IGNORECASE)
        query = m.group(1).strip() if m else None
        return {"action": "search", "params": {"query": query}}

    # click <target>
    if "click" in s:
        m = re.search(r"click\s+([A-Za-z0-9_\-#. \[\]=:]+)", step, re.IGNORECASE)
        target = m.group(1).strip() if m else None
        return {"action": "click", "params": {"target": target}}

    return {"action": "unknown", "params": {"raw": step}}


def parse_workflow(prompt: str):
    """
    Returns a list of structured steps. Non-breaking: existing code still uses parse_prompt().
    """
    steps = split_into_steps(prompt or "")
    return [parse_step(s) for s in steps]
