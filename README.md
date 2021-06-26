# Guild Chat Bot
[![Discord Server](https://img.shields.io/discord/763987695374434306?color=5865F2&logo=discord&logoColor=white)](https://discord.gg/YyCyZtchg3) \
A bot that connects your guild chat to a discord channel. Uses [discord.py](https://github.com/Rapptz/discord.py) and [pyCraft](https://github.com/ammaraskar/pyCraft)

## Deploy on Railway
[Railway](https://railway.app) is a cloud development platform that lets you host projects 24/7 for free!

### 1. Click button to deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2Fevernotemc%2Fhypixel-guild-chat-py&envs=TOKEN%2CGUILD_CHAT_CHANNEL%2CMINECRAFT_EMAIL%2CMINECRAFT_PASSWORD&TOKENDesc=Bot+Token+from+Discord+Developer+Portal&GUILD_CHAT_CHANNELDesc=The+channel+id+of+where+the+bot+should+send+messages&MINECRAFT_EMAILDesc=The+email+of+the+Minecraft+account+%28Mojang+only%29+the+bot+should+log+in+to&MINECRAFT_PASSWORDDesc=The+password+of+the+Minecraft+account+the+bot+should+log+in+to)

### 2. Configure and launch your environment
You'll need to specify four environment variables in order to get your bot up and running:
- `TOKEN` - Bot Token from [Discord Developer Portal](https://discord.com/developers/applications)
- `GUILD_CHAT_CHANNEL` - The ID of the channel where the bot should send and receive guild chat messages (e.g `792771296445726740`)
- `MINECRAFT_EMAIL` - The email of the Minecraft account you want the bot to use
- `MINECRAFT_PASSWORD` - The password of the Minecraft account you want the bot to use

**NOTE**: You can't use a Microsoft account for the bot.

### 3. Set prefix and emojis
You can edit the `constants.py` file to change the bot's prefix, and the emojis it uses.
```python
# The prefix the bot responds to for commands
PREFIX = '!'
# Emojis the bot should use for certain events
EMOJIS = {
    'DISCORD': '🗨️',  # When a message is sent from Discord
    'HYPIXEL': '🎮',  # When a message is sent from Hypixel
    'JOIN': '📥',  # When a member joins Hypixel
    'LEAVE': '📤'  # When a member leaves Hypixel
}
# List of Owner IDs (to use commands like sumo)
OWNER_IDS = [177750582818242561]
```
You can use a unicode, like 🎮, or custom emojis like `<:hypixel:855419679597920257>`

## Help
Confused with something? Join the [Observer Support](https://discord.gg/YyCyZtchg3) server for help!
