import discord
from discord.ext import commands
from discord import app_commands
import logging


class HelpCog(commands.Cog):
    """
    A Cog that provides a slash-based help command.
    It displays an embed of all available slash commands on the bot.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @app_commands.command(
        name="help", description="Displays a list of all available slash commands."
    )
    async def help_command(self, interaction: discord.Interaction):
        """
        Sends an embed listing all registered slash commands on the bot.
        """
        try:
            # Retrieve all slash commands from the bot's tree
            all_commands = self.bot.tree.get_commands()

            # Create an embed to display commands nicely
            embed = discord.Embed(
                title="Bot Commands",
                description="Here are the slash commands you can use:",
                color=discord.Color.blue(),
            )

            # Populate the embed
            for cmd in all_commands:
                # Skip command groups, or handle them differently if you want
                if isinstance(cmd, app_commands.Command):
                    embed.add_field(
                        name=f"/{cmd.name}",
                        value=(cmd.description or "No description provided."),
                        inline=False,
                    )

            # Send it as an ephemeral message
            await interaction.response.send_message(embed=embed, ephemeral=True)
            self.logger.info(f"Displayed help to {interaction.user}.")

        except Exception as e:
            # Log the error
            self.logger.error(f"Error in /help command: {e}")

            # If the interaction hasn't been responded to yet, respond. Otherwise, use followup.
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "Something went wrong while displaying help. Please try again later.",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    "Something went wrong while displaying help. Please try again later.",
                    ephemeral=True,
                )

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
