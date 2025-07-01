# TelEX – Telegram-Controlled Multi-Exchange Crypto Trading Bot

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**TelEX** is a modular, Telegram-based crypto trading bot framework that allows you to manage multiple exchange accounts ("instances") via a simple chat interface. Built on [CCXT](https://github.com/ccxt/ccxt), it provides flexible, alias-based control over spot and futures markets on major crypto exchanges.

---

## 🚀 Features

- 🔧 Add exchange instances dynamically from Telegram
- 💬 Control spot or futures accounts via simple text commands
- 🧠 Custom logic possible (e.g., trailing stop, break-even SL)
- 💾 Stores instance settings in a persistent config file
- 🛡️ Chat ID–restricted access for safety

---

## 🛠️ Technologies Used

- Python 3.9+
- CCXT (multi-exchange trading)
- python-telegram-bot
- JSON (for local config storage)

---

## 📁 Project Structure

```
TelEX/
├── main.py                   # Telegram bot entry point
├── config/
│   └── exchange_instances.json  # Saved exchange instances with API credentials
├── core/
│   ├── exchanges.py          # Exchange instance logic
│   ├── trading.py            # Trading actions (buy/sell/SL)
│   └── storage.py            # JSON config file handler
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

1. **Clone the repository**

```bash
git clone https://github.com/gberenyi/TelEX.git
cd TelEX
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set environment variables**

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_allowed_chat_id"
```

4. **Run the bot**

```bash
python main.py
```

---

## 📲 Adding Exchange Instances via Telegram

Add new exchange configurations from Telegram using the `/addinstance` command:

```
/addinstance <alias> <exchange_id> <api_key> <api_secret>
```

**Example:**

```
/addinstance binfut binanceusdm YOUR_API_KEY YOUR_SECRET
```

The alias (`binfut`) can then be used to execute future trade commands.

---

## 🔐 Security

- All API keys are stored **locally** in a JSON file
- Only the pre-defined `chat_id` has access to the bot
- No external cloud services involved — fully self-hosted

---

## 🧩 Planned Features

- `/buy`, `/sell`, `/close`, `/status` commands
- Dynamic SL management (break-even, trailing SL)
- Position tracking and reporting
- Multiple user sessions
- Plugin-style strategy logic

---

## 📜 License

This project is licensed under the MIT License.  
See [LICENSE](LICENSE) for full details.

---

## 👤 Author

Developed by [Gábor Berényi](https://github.com/gberenyi)  
Project repository: [github.com/gberenyi/TelEX](https://github.com/gberenyi/TelEX)

---

> TelEX – built for control freaks who trade smart.
