# 🎮 Game Stat Discord Bot

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Discord.py](https://img.shields.io/badge/discord.py-v2.7+-blueviolet)
![Database](https://img.shields.io/badge/Database-MySQL-orange)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-Personal-lightgrey)

---

## 📌 About

A multi-utility Discord bot designed for community servers like **Basement of Gamers (BOGS)**. It tracks **game playtime** and **voice activity** of users in voice channels in real time, manages live leaderboards, provides an AI chat assistant, and includes moderation and fun utilities.

The bot automatically scans members active in voice channels, updates cumulative stats in a MySQL database, and keeps a live **Top 5 Games** and **Top 5 Lifeless Users** leaderboard pinned and updated in dedicated channels.

---

## ✨ Features

### 📊 Game & Voice Tracking
- **Automated VC Scanning**: Scans voice channels every 60 seconds for active players and streamers.
- **Title Sanitization**: Cleans and normalizes game titles (e.g., PUBG, removing client/tracker tags).
- **Live Leaderboard**: Real-time auto-updating embed displaying Top 5 Games and Top 5 Most Active voice members.
- **Weekly / Periodic Resets**: Easily recap and reset stats with a single command.

### 🤖 AI Chat Assistant
- Powered by OpenRouter API (`~openai/gpt-sol-latest` / configurable).
- Dedicated AI channel with permission checking (`ROLE_USER`).
- Rolling 6-message context memory and user mention translation.

### 🔊 Voice Utilities & Protections
- **Ringing**: Bounce users between their VC and AFK to get their attention.
- **Move All**: Seamlessly transfer everyone in your current VC to a target channel.
- **Join / Leave Logs**: Live color-coded event logging to your designated voice log channel.
- **Anti Mass-Disconnect (`znodc`)**: Monitors audit logs and automatically times out users repeatedly disconnecting others.
- **Beast Mode (`zbeast`)**: Auto-unmutes and auto-undeafens protected server members.

### 🛡️ Moderation & Auditing
- **Deleted Message Logging**: Recovers deleted text and attachments (images/files) into memory and re-uploads them to the audit channel.
- **Role Change Logging**: Tracks role additions and removals with audit log executor identification.
- **Echo & DM**: Send messages or direct messages through the bot with full attachment support.

### 🎲 Fun & Utilities
- Interactive **Rock, Paper, Scissors** with animated countdown and Discord UI dropdowns.
- Animated **Coin Flip** with 3-second delay.
- User permission check and custom help menu.

---

## 📌 Commands

| Command | Permission | Description |
| :--- | :--- | :--- |
| `zping` | Everyone | Check bot responsiveness ("pong") |
| `zcheck` | Everyone | Verify if you have the required server role |
| `zhelp` | Everyone | Display user command menu |
| `zflip` | Everyone | Flip a coin (Heads/Tails) |
| `zrps @user` | Everyone | Interactive Rock, Paper, Scissors with dropdown selection |
| `zact` | `ROLE_USER` | Show playing / streaming activity of everyone in voice channels |
| `zring @user` | `ROLE_USER` | Drag a user to AFK and back twice to alert them |
| `zmoveall #channel` | `ROLE_USER` | Move all members in your current VC to target channel |
| `zmsg <text>` | `ROLE_ADMIN` | Send / echo a message or attachments using the bot |
| `zgamestat` | `ROLE_ADMIN` | Manually restart or trigger the leaderboard embed loop |
| `znodc` | Author | Toggle the anti mass-disconnect protection |
| `zbeast` | Target Author | Toggle auto-unmute / auto-undeafen shield |
| `zdm @user <msg>` | Author | Send a direct message to a user on the bot's behalf (logged) |
| `zresetstat` | Author | Post stat recaps to log channel and reset database statistics |
| `zrestart` | Author | Trigger bot restart via PM2 |

---

## 📁 Project Structure

The project uses a clean, modular **Cog** architecture:

```text
FinalBot/
├── cogs/
│   ├── general.py          # Ping, check, help, coin flip, and RPS
│   ├── voice.py            # Ring, moveall, activity check, beast mode, anti-disconnect
│   ├── stats.py            # VC tracker loop, live leaderboard embeds, stat reset
│   ├── moderation.py       # Message delete recovery, role change logs, DM, echo
│   ├── ai.py               # Dedicated AI chat worker and memory management
│   └── admin.py            # Restart and maintenance commands
├── database/
│   ├── __init__.py
│   └── db.py               # MySQL connection pool, thread-safe queries, and schema helpers
├── .env                    # Secret credentials (ignored in git)
├── .env.example            # Environment configuration template
├── .gitignore              # Git ignore rules for virtualenv, logs, and secrets
├── config.py               # Central configuration loader with fallback support
├── main.py                 # Bot initialization, cog auto-loader, and startup
└── requirements.txt        # Pinned Python package dependencies
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sajid128/game-stat-bot.git
cd game-stat-bot
```

### 2️⃣ Create and Activate a Virtual Environment

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Discord credentials and MySQL database info:

```bash
cp .env.example .env
```

Key variables:
- `BOT_TOKEN`: Your Discord Bot Token.
- `GUILD`: Your target Discord server ID.
- `ROLE_USER` / `ROLE_ADMIN`: Required role IDs.
- `CHANNEL_INFO` / `CHANNEL_LIFELESS`: Channel IDs for leaderboards.
- `DELETE_LOG` / `JOIN_LOG` / `RESET_INFO` / `YAP_CHAT`: Channel IDs for logging.
- `AUTHOR`: Comma-separated list of superuser Discord IDs.
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`, `DB_NAME`: MySQL connection details.
- `AI_TOKEN`, `AI_BASE_URL`, `AI_CHANNEL`: AI integration settings.

### 5️⃣ Run the Bot

```bash
python main.py
```

---

## 📷 Screenshots

<!-- Wide leaderboard images -->
<p align="center">
  <img src="https://github.com/user-attachments/assets/2545cb3b-f81f-4333-ad78-7596ad0a91af"
       width="48%" height="420px" style="object-fit: cover;" />
  <span style="display:inline-block;width:2px;height:320px;background-color:#ccc;margin:0 5px;"></span>
  <img src="https://github.com/user-attachments/assets/7c8112a8-d08c-4d43-8c45-f148b1544780"
       width="48%" height="420px" style="object-fit: cover;" />
</p>

---

<!-- Very wide activity screenshot -->
<p align="center">
  <img src="https://github.com/user-attachments/assets/420d0953-30c6-4f72-b6f9-3ba2901dc688"
       width="48%" height="350px" style="object-fit: cover;" />
  <span style="display:inline-block;width:2px;height:320px;background-color:#ccc;margin:0 5px;"></span>
  <img src="https://github.com/user-attachments/assets/90cdcf29-04b2-478e-967d-7397d48e3605"
       width="48%" height="350px" style="object-fit: cover;" />
</p>

---

<!-- Tall / narrow images grouped -->
<p align="center">
  <img src="https://github.com/user-attachments/assets/917c1727-ca1c-44c0-8abb-ef58eb848792"
       width="48%" height="380px" style="object-fit: cover;" />
  <span style="display:inline-block;width:2px;height:320px;background-color:#ccc;margin:0 5px;"></span>
  <img src="https://github.com/user-attachments/assets/7e416632-5850-4acb-b5ae-06e0270cf719"
       width="48%" height="380px" style="object-fit: cover;" />
</p>
