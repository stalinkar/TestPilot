import os, uuid, base64
from playwright.async_api import async_playwright

playwright_instance = None
browser = None
page = None

REPORTS_DIR = "../target/reports"
SCREENSHOTS_DIR = "../target/screenshots"
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


async def init_browser(headless: bool = True):
    global playwright_instance, browser, page
    if not playwright_instance:
        playwright_instance = await async_playwright().start()
        browser = await playwright_instance.chromium.launch(headless=headless)
        page = await browser.new_page()
    return page


async def close_browser():
    global playwright_instance, browser, page
    if browser:
        await browser.close()
        await playwright_instance.stop()
    playwright_instance, browser, page = None, None, None
    return {"status": "browser_closed"}


# ----- Actions -----
async def navigate(url: str):
    pg = await init_browser()
    await pg.goto(url, wait_until="domcontentloaded")
    return {"status": "navigated", "url": url}


async def click(selector: str):
    if not page: return {"error": "No active page"}
    screenshots = await screenshot(None, True)
    await page.click(selector)
    return {"status": "clicked", "selector": selector, "screenshot": screenshots}


async def fill(selector: str, text: str):
    if not page: return {"error": "No active page"}
    await page.fill(selector, text)
    return {"status": "filled", "selector": selector, "value": text}


async def wait_for(selector: str, timeout: int = 5000):
    if not page: return {"error": "No active page"}
    await page.wait_for_selector(selector, timeout=timeout)
    return {"status": "waited", "selector": selector, "timeout": timeout}


async def screenshot(selector: str = None, save: bool = False):
    if not page: return {"error": "No active page"}
    if selector:
        el = await page.query_selector(selector)
        if not el: return {"error": f"Element {selector} not found"}
        img = await el.screenshot()
    else:
        img = await page.screenshot(full_page=True)

    if save:
        path = os.path.join(SCREENSHOTS_DIR, f"screenshot_{uuid.uuid4().hex}.png")
        with open(path, "wb") as f: f.write(img)
        return {"status": "screenshot_saved", "path": path}
    return {"status": "screenshot_inline", "data": base64.b64encode(img).decode("utf-8")}
