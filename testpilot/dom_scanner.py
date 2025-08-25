from .utils import contains_any, safe, USERNAME_HINTS, PASSWORD_HINTS, LOGIN_TEXT_HINTS


async def build_best_selector(el):
    tag = await el.evaluate("e => e.tagName.toLowerCase()")
    el_id = await el.get_attribute("id")
    if el_id: return f"#{el_id}"
    dt = await el.get_attribute("data-test")
    if dt: return f"{tag}[data-test='{dt}']"
    name = await el.get_attribute("name")
    if name: return f"{tag}[name='{name}']"
    ph = await el.get_attribute("placeholder")
    if ph: return f"{tag}[placeholder*='{ph[:20]}']"
    nth = await el.evaluate("""
        (e) => { let i=1,n=e; while((n=n.previousElementSibling)!=null){ if(n.tagName===e.tagName) i++; } return i; }
    """)
    return f"{tag}:nth-of-type({nth})"


async def is_visible(el):
    return await el.evaluate("""
        e => { const s=window.getComputedStyle(e),r=e.getBoundingClientRect();
               return s.display!=='none' && s.visibility!=='hidden' && r.width>0 && r.height>0 }
    """)


async def score_username_input(page, el):
    if not await is_visible(el): return -1
    t = (await el.get_attribute("type") or "").lower()
    ph = await el.get_attribute("placeholder") or ""
    lab = await el.get_attribute("aria-label") or ""
    score = 0
    if t in ("text", "email"): score += 3
    if t == "email": score += 4
    for v in [ph, lab]:
        if contains_any(v, USERNAME_HINTS): score += 3
    if len(safe(ph)) >= 3: score += 1
    return score


async def score_password_input(page, el):
    if not await is_visible(el): return -1
    t = (await el.get_attribute("type") or "").lower()
    ph = await el.get_attribute("placeholder") or ""
    score = 0
    if t == "password": score += 6
    if contains_any(ph, PASSWORD_HINTS): score += 3
    return score


async def score_login_button(el):
    if not await is_visible(el): return -1
    text = await el.inner_text() or ""
    score = 0
    if contains_any(text, LOGIN_TEXT_HINTS): score += 5
    return score


async def find_login_elements_dynamic(page):
    inputs = await page.query_selector_all("input, textarea")
    cand_user, su = None, -1
    cand_pass, sp = None, -1
    for el in inputs:
        su_el = await score_username_input(page, el)
        sp_el = await score_password_input(page, el)
        if su_el >= su: su, cand_user = su_el, el
        if sp_el >= sp: sp, cand_pass = sp_el, el

    btns = await page.query_selector_all("button, input[type='submit'], [role='button'], *:has-text('Sign in'), "
                                         "*:has-text('Log in')")
    cand_btn, sb = None, -1
    for el in btns:
        sbtn = await score_login_button(el)
        if sbtn >= sb: sb, cand_btn = sbtn, el

    return {
        "username": {"selector": await build_best_selector(cand_user) if cand_user else None, "score": su},
        "password": {"selector": await build_best_selector(cand_pass) if cand_pass else None, "score": sp},
        "button": {"selector": await build_best_selector(cand_btn) if cand_btn else None, "score": sb}
    }
