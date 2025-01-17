import discord, logging
from discord.ext import commands
from dotenv import load_dotenv

import os, sys, asyncio, datetime
from datetime import timezone

# Load environment variables
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID", "0") # Defaults to Zero (global sync)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Check if DISCORD_TOKEN is set
if not TOKEN:
    sys.exit("Error: DISCORD_TOKEN is not set in the .env file.")

# Check if LOG_LEVEL is valid
valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
if LOG_LEVEL.upper() not in valid_log_levels:
    print(f"Invalid LOG_LEVEL '{LOG_LEVEL}' specified. Defaulting to 'INFO'.")
    LOG_LEVEL = "INFO"

# Initialize logging
logging.basicConfig(
    level=LOG_LEVEL.upper(),
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("discord.log", encoding="utf-8", mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Check if GUILD_ID is valid, defaults to 0 and global sync if set incorrect
try:
    GUILD_ID = int(GUILD_ID)
except ValueError:
    logger.warning("GUILD_ID is not a valid integer. Defaulting to 0 (global sync).")
    GUILD_ID = 0
logger.debug(f"GUILD_ID set to: {GUILD_ID}")

# Enable Intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=None,
            intents=intents,
            help_command=None,
        )
        # Creates a variable to track uptime
        self.start_time = datetime.datetime.now(timezone.utc)

    # Load all cogs
    async def setup_hook(self):
        # 1. Load all cogs from the "./cogs" directory
        for filename in os.listdir("cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                cog_name = filename[:-3]
                try:
                    await self.load_extension(f"cogs.{cog_name}")
                    logger.info(f"Loaded cog: {cog_name}")
                except Exception as e:
                    logger.error(f"Failed to load cog {cog_name}: {e}")

        # 2. Sync commands to set Guild, if no Guild is set defaults to global command registration
        try:
            if GUILD_ID != 0:
                # Copy all commands recognized so far into the Guild
                self.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
                # Sync the commands to the Guild
                synced = await self.tree.sync(guild=discord.Object(id=GUILD_ID))
                logger.info(f"Synced {len(synced)} command(s) to guild: {GUILD_ID}.")
            else:
                # Global sync
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} command(s) globally.")
        except Exception as e:
            logger.error(f"Command sync failed: {e}")

    # Log when the bot is ready
    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("Bot is online and ready to receive commands!")

async def main():
    bot = MyBot()
    async with bot:
        try:
            await bot.start(TOKEN)
        except discord.LoginFailure:
            logger.critical("Invalid token. Check your DISCORD_TOKEN in .env.")
            sys.exit(1)
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            sys.exit(1)


# If this file is run directly, start the bot
if __name__ == "__main__":
    asyncio.run(main())
