# York Bot — Satellite 06 (Greed)

> *"It's mine now. Don't touch it."*

A Discord bot based on **York**, Vegapunk's Satellite 06 — the embodiment of Greed, self-serving behaviour, and basic needs.

## Commands

| Command | Description |
|---|---|
| `york eat <food>` | York eats something (logged in SQLite) |
| `york sleep` | York takes a nap (random duration) |
| `york claim <item>` | York claims an item for herself |
| `york inventory` | Show everything York has claimed in this server |
| `york take @user <amount>` | York takes coins from another user |
| `york wallet` | Show York's total coins taken in this server |
| `york siblings` | List all six Vegapunk satellites |
| `york?` | Show the help menu with a select dropdown |

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/york-bot.git
cd york-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your token
```bash
cp .env.example .env
```
Edit `.env` and paste your Discord bot token:
```
DISCORD_TOKEN=your_token_here
```

### 4. Run the bot
```bash
python bot.py
```

## Database

York uses a local SQLite database (`york.db`) to store meals, claimed items, and taken coins. Created automatically on first run.

## Discord Developer Portal Setup

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Create a new application named **York**
3. Go to **Bot** → Create a bot
4. Under **Privileged Gateway Intents**, enable:
   - **Message Content Intent**
   - **Server Members Intent**
5. Copy the token into your `.env`
6. Under **OAuth2 → URL Generator**, select `bot` scope and the following permissions:
   - Send Messages, Embed Links, Read Message History, View Channels

## Cross-bot Awareness

York reacts when sibling satellite names are mentioned in chat (Shaka, Lilith, Edison, Pythagoras, Atlas). For full cross-bot awareness, run all 6 satellite bots in the same server.
