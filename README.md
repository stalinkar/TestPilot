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
