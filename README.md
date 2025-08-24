# 🧪 TestPilot

**TestPilot** is an experimental **natural-language-driven web automation agent**.  
You describe a test in plain English, and TestPilot converts it into **executable automation flows** powered by Playwright.

## ✨ Features
- 🧭 Navigate to any URL with plain English instructions  
- 🔐 Robust login flow detection across multiple websites  
- 🖊️ Auto-detects username, password, and login buttons dynamically (no hardcoded selectors)  
- 🧠 Converts **natural language prompts → JSON flows**  
- ▶️ Execute generated flows step-by-step using Playwright  
- 📸 Capture screenshots and store run reports automatically  

## 🚀 Quick Start

### 1. Clone and Install
```bash
git clone https://github.com/stalinkar/TestPilot.git
cd TestPilot
python -m venv venv
source venv/bin/activate   # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
```

- Install 


```txt
# 📦 requirements.txt
flask
playwright
beautifulsoup4
lxml
```
(after installing, don’t forget to run <i><b>```playwright install```</b></i> once to set up browsers)

### 2. Run the Server
```
python -m testpilot.server
```
- Server starts on http://localhost:5000

### 3. Generate Flow from Prompt
```
curl -s -X POST http://localhost:5000/nl_to_flow \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "navigate to https://www.saucedemo.com and login with username \"standard_user\" and password \"secret_sauce\""
  }' | jq
```
- Example Output:
```
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
Save the flow to a file examples/saucedemo_login.json, then run:
```
curl -s -X POST http://localhost:5000/run_flow \
  -H "Content-Type: application/json" \
  -d @examples/saucedemo_login.json
```

## 📂 Project Layout
```
TestPilot/
├── testpilot/           # Core library
├── examples/            # Example flows
├── reports/             # Run logs
├── screenshots/         # Captured screenshots
```

## 🛠️ Tech Stack
~~~
Playwright
 → Browser automation

Flask
 → API server

BeautifulSoup4
 → HTML parsing (optional extensions)

Python 3.9+
~~~
