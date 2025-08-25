from flask import Flask, request, jsonify
import asyncio
from testpilot.flow import nl_to_flow_internal, run_flow
from testpilot.actions import navigate, click, fill, wait_for, screenshot, close_browser

app = Flask(__name__)
loop = asyncio.get_event_loop()


@app.route("/nl_to_flow", methods=["POST"])
def api_nl_to_flow():
    body = request.get_json(force=True) or {}
    prompt = body.get("prompt", "")
    headless = bool(body.get("headless", True))
    wait_selector = body.get("wait_for")
    result = loop.run_until_complete(nl_to_flow_internal(prompt, headless, wait_selector))
    return jsonify(result)


@app.route("/run_flow", methods=["POST"])
def api_run_flow():
    steps = request.get_json(force=True)
    results = loop.run_until_complete(run_flow(steps))
    return jsonify(results)


@app.route("/close", methods=["POST"])
def api_close():
    result = loop.run_until_complete(close_browser())
    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
