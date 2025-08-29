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


async def label_text_for(page, el):
    # Check <label for="id"> and aria-label & nearby text
    el_id = await el.get_attribute("id")
    if el_id:
        lab = await page.query_selector(f"label[for='{el_id}']")
        if lab:
            t = await lab.text_content() or ""
            if t.strip():
                return t.strip()

    aria = await el.get_attribute("aria-label")
    if aria: return aria

    # Try parent container text
    parent_text = await el.evaluate("""
      (e) => {
        if (!e.parentElement) return '';
        const t = e.parentElement.innerText || '';
        return t.length > 200 ? t.slice(0,200) : t;
      }
    """)
    return parent_text or ""
