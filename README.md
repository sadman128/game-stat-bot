# 🎮 Game Stat Discord Bot

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Discord.py](https://img.shields.io/badge/discord.py-Bot-blueviolet)
![Database](https://img.shields.io/badge/Database-MySQL-orange)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-Personal-lightgrey)

---

## 📌 About

A multi-utility Discord bot that tracks **game playtime** of users inside voice channels and displays statistics in real time.

The bot monitors users who are playing games while connected to voice channels, stores playtime in a database, and displays the **Top 5 most played games** along with user activity statistics.

> ⚠️ This project was created mainly out of curiosity and learning. The code is not production optimized so do not judge.

---

## ✨ Features

### Game Tracking
- Tracks games played in voice channels  
- Shows Top 5 most played games  
- Tracks VC activity time  
- Supports stat reset  

### AI Chat (Optional)
- LLM chat support  
- Basic conversation memory  
- Role restricted access  

### Voice Utilities
- Ring users  
- Move users between voice channels  
- VC join/leave logging  
- Anti mass-disconnect  
- Protected user mode  

### Logging & Moderation
- Deleted message logging  
- Role change logging  
- Admin DM command  

### Fun
- Coin flip  
- Rock Paper Scissors  

---

## 📌 Commands

| Command | Description |
|----------|-------------|
| `zping` | Check bot status |
| `zmsg` | Send message using bot (Admin only) |
| `zring @user` | Drag user between VC twice |
| `zmoveall #channel` | Move everyone to another VC |
| `zact` | Show games currently played in server |
| `zresetstat` | Reset game & user stats |
| `znodc` | Toggle anti disconnect system |
| `zflip` | Flip coin |
| `zrps @user` | Rock Paper Scissors |
| `zdm @user message` | Send dm message |
---

## 📊 How It Works

1. Bot scans voice channels every minute
2. Detects users playing games
3. Stores playtime in MySQL database
4. Updates leaderboard automatically
5. Admin can reset stats anytime

---

## 🧰 Tech Stack

- Python 3
- discord.py
- MySQL
- OpenAI / DeepSeek API (Optional)
- Asyncio + Threading
- pytz

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/sajid128/game-stat-bot.git
```
## 📷 Screenshots

<!-- Wide leaderboard images -->
<p align="center">
  <img src="https://github.com/user-attachments/assets/e5a01cbf-6f66-4ade-8a36-82a9ee643cce" width="48%" />
  <img src="https://github.com/user-attachments/assets/7c8112a8-d08c-4d43-8c45-f148b1544780" width="48%" />
</p>

---

<!-- Very wide activity screenshot -->
<p align="center">
  <img src="https://github.com/user-attachments/assets/420d0953-30c6-4f72-b6f9-3ba2901dc688" width="70%" />
</p>

---

<p align="center">
<img src="https://github.com/user-attachments/assets/90cdcf29-04b2-478e-967d-7397d48e3605" width="20%" />
</p>
---

<!-- Tall / narrow images grouped -->
<p align="center">
  <img src="https://github.com/user-attachments/assets/917c1727-ca1c-44c0-8abb-ef58eb848792" width="30%" />
  <img src="https://github.com/user-attachments/assets/7e416632-5850-4acb-b5ae-06e0270cf719" width="45%" />
</p>



