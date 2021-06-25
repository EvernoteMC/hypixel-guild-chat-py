import os
from dotenv import load_dotenv

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


# Don't touch this unless you know what you're doing
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_CHAT_CHANNEL = int(os.getenv("GUILD_CHAT_CHANNEL"))
MINECRAFT_EMAIL = os.getenv("MINECRAFT_EMAIL")
MINECRAFT_PASSWORD = os.getenv("MINECRAFT_PASSWORD")
