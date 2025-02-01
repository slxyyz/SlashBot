import os
import sys
import logging
import asyncio
import datetime
from datetime import timezone

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID", "0")  # Defaults to 0 (global sync)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if not TOKEN:
    sys.exit("Error: DISCORD_TOKEN is not set in the .env file.")

# Validate log level
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
    logger.warning(
        "GUILD_ID is not a valid integer. Defaulting to 0 (global command sync)."
    )
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
        # Track bot start time
        self.start_time = datetime.datetime.now(timezone.utc)

    async def setup_hook(self):
        # Load all cogs from the "./cogs" directory
        for filename in os.listdir("cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                cog_name = filename[:-3]
                try:
                    await self.load_extension(f"cogs.{cog_name}")
                    logger.info(f"Loaded cog: {cog_name}")
                except Exception as e:
                    logger.error(f"Failed to load cog {cog_name}: {e}")

        # Sync commands to set Guild, if no Guild is set defaults to global command registration
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

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("Bot is online and ready to receive commands!")

    # Global error handler for interactions
    async def on_interaction(self, interaction: discord.Interaction):
        try:
            # Process the interaction normally
            await super().on_interaction(interaction)
        except app_commands.CommandOnCooldown as cooldown_error:
            await interaction.response.send_message(
                f"This command is on cooldown. Try again in {cooldown_error.retry_after:.2f}s",
                ephemeral=True,
            )
        except app_commands.MissingPermissions:
            await interaction.response.send_message(
                "You don't have the required permissions to use this command.",
                ephemeral=True,
            )
        except app_commands.BotMissingPermissions:
            await interaction.response.send_message(
                "I don't have the required permissions to execute this command.",
                ephemeral=True,
            )
        except app_commands.CommandNotFound:
            # Unlikely with slash commands
            await interaction.response.send_message(
                "Command not found.", ephemeral=True
            )
        except Exception as error:
            # Log unexpected errors with traceback
            command_name = interaction.command if interaction.command else "Unknown"
            logger.error(f"Error in command {command_name}: {error}", exc_info=True)

            # Send an error message to the user
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "An unexpected error occurred. Please try again later.",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    "An unexpected error occurred. Please try again later.",
                    ephemeral=True,
                )


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


if __name__ == "__main__":
    asyncio.run(main())
