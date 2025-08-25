import os, uuid, json
from datetime import datetime
from .nlp_parser import parse_prompt
from .utils import normalize_url
from .dom_scanner import find_login_elements_dynamic
from .actions import init_browser, close_browser, navigate, fill, click, wait_for, screenshot, REPORTS_DIR


# ----------- NL -> Flow -----------
async def nl_to_flow_internal(prompt: str, headless=True, wait_selector=None):
    parsed = parse_prompt(prompt)
    url = normalize_url(parsed["url"])
    if not url:
        return {"error": "No URL in prompt."}

    await init_browser(headless=headless)
    await navigate(url)
    if wait_selector:
        try:
            await wait_for(wait_selector, 8000)
        except Exception:
            pass

    discovered = await find_login_elements_dynamic(await init_browser())
    steps = [{"action": "navigate", "url": url}]
    steps.append(
        {"action": "fill", "selector": discovered["username"]["selector"], "text": parsed["username"] or "<USERNAME>"})
    steps.append(
        {"action": "fill", "selector": discovered["password"]["selector"], "text": parsed["password"] or "<PASSWORD>"})
    if discovered["button"]["selector"]:
        steps.append({"action": "click", "selector": discovered["button"]["selector"]})
    steps.append({"action": "wait_for", "selector": "body", "timeout": 5000})
    steps.append({"action": "screenshot", "save": True})

    await close_browser()
    return {"prompt": prompt, "parsed_entities": parsed, "discovered_selectors": discovered, "flow": steps}


async def run_flow(steps: list):
    results = []
    start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # report_id = f"flow_{start_time}_{uuid.uuid4().hex[:6]}"
    report_id = f"flow_{start_time}"
    json_report_file = os.path.join(REPORTS_DIR, f"{report_id}.json")
    html_report_file = os.path.join(REPORTS_DIR, f"{report_id}.html")

    passed_count, failed_count = 0, 0

    for idx, step in enumerate(steps, start=1):
        action = step.get("action")
        status = "passed"
        try:
            if action == "navigate":
                result = await navigate(step["url"])
            elif action == "click":
                result = await click(step["selector"])
            elif action == "close":
                result = await close_browser()
            elif action == "fill":
                result = await fill(step["selector"], step["text"])
            elif action == "wait_for":
                result = await wait_for(step["selector"], step.get("timeout", 5000))
            elif action == "screenshot":
                result = await screenshot(step.get("selector"), step.get("save", False))
            else:
                result = {"error": f"Unknown action {action}"}
                status = "failed"
        except Exception as e:
            result = {"error": str(e), "step": step}
            status = "failed"

        if "error" in result:
            status = "failed"
            failed_count += 1
        else:
            passed_count += 1

        results.append({"step_number": idx, "action": action, "status": status, "input": step, "output": result,
                        "timestamp": datetime.now().isoformat()})

    overall_status = "PASSED" if failed_count == 0 else "FAILED"

    # Save JSON report
    with open(json_report_file, "w", encoding="utf-8") as f:
        json.dump({"report_id": report_id, "overall_status": overall_status, "results": results}, f, indent=2)

    # Build HTML report
    html = [f"<html><head><title>Flow Report {report_id}</title>", "<style>", "body{font-family:Arial;margin:20px;}",
            "table{border-collapse:collapse;width:100%;margin-bottom:20px;}",
            "th,td{border:1px solid #ddd;padding:8px;vertical-align:top;}", "th{background:#f4f4f4;}",
            ".passed{color:green;font-weight:bold;}", ".failed{color:red;font-weight:bold;}",
            "pre{white-space:pre-wrap;word-wrap:break-word;max-height:200px;overflow:auto;background:#f9f9f9;padding"
            ":6px;border-radius:4px;}",
            "details{margin:4px 0;}", "</style>", "</head><body>", f"<h1>Flow Report: {report_id}</h1>",
            f"<p>Generated at: {datetime.now().isoformat()}</p>", f"<h2>Summary</h2>",
            f"<p>Overall Status: <span class='{overall_status.lower()}'>{overall_status}</span></p>",
            f"<p>Total Steps: {len(results)} | Passed: <span class='passed'>{passed_count}</span> | Failed: <span class='failed'>{failed_count}</span></p>",
            "<h2>Step Details</h2>", "<table>",
            "<tr><th>Step</th><th>Action</th><th>Status</th><th>Input</th><th>Output</th><th>Screenshot</th></tr>"]

    for r in results:
        output = r["output"]
        screenshot_html = ""
        if isinstance(output, dict) and "screenshot" in output:
            output = output["screenshot"]
        if isinstance(output, dict) and "data" in output:  # inline screenshot
            screenshot_html = f'<img src="data:image/png;base64,{output["data"]}" width="300"/>'
        if isinstance(output, dict) and "path" in output:  # inline linked screenshot
            screenshot_html = (f'<a href="../{output["path"]}" target="_blank"><img src="../{output["path"]}" width'
                               f'="200"/></a>')

        input_html = f"<details><summary>Show Input</summary><pre>{json.dumps(r['input'], indent=2)}</pre></details>"
        output_html = f"<details><summary>Show Output</summary><pre>{json.dumps(r['output'], indent=2)}</pre></details>"

        html.append(f"<tr>"
                    f"<td>{r['step_number']}</td>"
                    f"<td>{r['action']}</td>"
                    f"<td class='{r['status']}'>{r['status'].upper()}</td>"
                    f"<td>{input_html}</td>"
                    f"<td>{output_html}</td>"
                    f"<td>{screenshot_html}</td>"
                    f"</tr>")

    html.append("</table></body></html>")

    with open(html_report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

    return {"report_id": report_id, "overall_status": overall_status, "json_report": json_report_file,
            "html_report": html_report_file, "results": results}
