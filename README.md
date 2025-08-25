# 🧪 TestPilot

**TestPilot** is an experimental **natural-language-driven web automation agent**.
You describe a test in plain English, and TestPilot converts it into **executable automation flows** powered by Playwright.

## ✨ Features

- 🧭 Navigate to any URL with plain English instructions
- 🔐 Robust login flow detection across multiple websites
- 🖊️ Auto-detects username, password, and login buttons dynamically (no hardcoded selectors)
- 🧠 Converts **natural language prompts → JSON flows**
- ▶️ Execute generated flows step-by-step using Playwright
- 📸 Capture screenshots and store run reports automatically (HTML + JSON)

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/stalinkar/TestPilot.git
cd TestPilot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install
```

#### requirements.txt

```txt
# 📦 requirements.txt
flask
playwright
beautifulsoup4
lxml
```

(after installing, don’t forget to run <i><b>```playwright install```</b></i> once to set up browsers)

### 2. Run the Server

```bash
python -m testpilot.server
# Server runs on http://localhost:5000
```

### 3. Generate Flow from Prompt

```bash
curl -s -X POST http://localhost:5000/nl_to_flow \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "navigate to https://www.saucedemo.com and login with username \"standard_user\" and password \"secret_sauce\""
  }' | jq
```

**Example response (truncated):**

```json
{
  "flow": [
    {"action":"navigate","url":"https://www.saucedemo.com"},
    {"action":"fill","selector":"#user-name","text":"standard_user"},
    {"action":"fill","selector":"#password","text":"secret_sauce"},
    {"action":"click","selector":"#login-button"},
    {"action":"wait_for","selector":"body","timeout":5000},
    {"action":"screenshot","save":false}
  ]
}
```

### 4. Execute Flow

Save the `flow` into `examples/saucedemo_login.json`, then:

```bash
curl -s -X POST http://localhost:5000/run_flow \  
-H "Content-Type: application/json" \  
-d @examples/saucedemo_login.json | jq
```

This also writes an HTML report to `reports/` with collapsible step I/O and inline screenshots.

## 📂 Project Layout

```
TestPilot/
├── testpilot/           # Core library
│   ├── server.py        # Flask API routes
│   ├── flow.py          # NL→flow + executor + reports
│   ├── actions.py       # Playwright actions
│   ├── dom_scanner.py   # Dynamic login discovery
│   ├── nlp_parser.py    # Prompt parser
│   └── utils.py         # Helpers & constants
├── examples/            # Example flows
├── reports/             # Run logs (HTML/JSON)
└── screenshots/         # Captured screenshots
```

## 🛠️ Tech Stack

- Playwright (Python) — browser automation
- Flask — API server
- Python 3.9+

## 🧭 API Endpoints

- `POST /nl_to_flow` → `{prompt, headless?, wait_for?}` → returns `{flow, discovered_selectors, parsed_entities}`
- `POST /run_flow` → `[ {action, ...}, ... ]` → executes the steps and returns per-step results; also writes an
  HTML/JSON report
- `POST /close` → closes the shared browser session

## 🔐 Notes on Login Robustness

- DOM scanner scores inputs via type, placeholder, aria-label, hints (`user`, `email`, `pass`)
- Buttons ranked by visible text (`login`, `sign in`, `submit`) and type=submit
- Selectors prefer `id`, `data-test`, `name`, then `placeholder`, then nth-of-type fallback

## 🧪 Examples

See `examples/` and try prompts for:

- https://www.saucedemo.com/
- https://rahulshettyacademy.com/client/#/auth/login
- https://courses.ultimateqa.com/users/sign_in

## 🧰 Troubleshooting

- Always run `python -m playwright install` once after dependency install
- If `nl_to_flow` returns “Could not detect username/password”, pass a `wait_for` selector so the page can finish
  rendering the form
- For locked-down pages (SSO/CAPTCHA), consider manual overrides or site-specific hints

## 🗺️ Roadmap

- Improve NLU (synonyms, entity extraction: “email” vs “username”)
- Multifactorial auth detection and handoff
- Domain memory: cache selectors per site
- Extend beyond login (menus, forms, carts)
- CLI + YAML flow runner
- Dockerfile and CI

## 🤝 Contributing

PRs welcome. Please open issues for bugs and feature ideas.

Python 3.9+
~~~
