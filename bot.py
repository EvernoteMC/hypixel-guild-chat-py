import os
from discord.ext import commands
from constants import PREFIX, TOKEN, OWNER_IDS


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(PREFIX))
        self.token = TOKEN
        self.owner_ids = OWNER_IDS
        for file in os.listdir('cogs'):
            if file.endswith('.py'):
                try:
                    print(f"Loading {file}")
                    self.load_extension(f'cogs.{file[:-3]}')
                except Exception as e:
                    print(f"Failed to load extension {file}\n{type(e).__name__}: {e}")

    def run(self):
        super().run(self.token, reconnect=True)

    async def on_ready(self):
        print(f"{self.user.name} is now online!")


if __name__ == '__main__':
    Bot().run()
