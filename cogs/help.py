import discord, logging
from discord.ext import commands
from discord import app_commands


class HelpCog(commands.Cog):
    """
    A Cog that provides a slash-based help command.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @app_commands.command(
        name="help",
        description="Displays a list of all available slash commands or usage for a specific command.",
    )
    @app_commands.describe(
        command="(Optional) The name of a command to see detailed info about."
    )
    async def help_command(self, interaction: discord.Interaction, command: str = None):
        """
        Sends an embed listing all registered slash commands on the bot.
        If a command name is specified, shows details about that command only.
        """
        # If no specific command is requested, show a general list of all commands.
        if not command:
            all_commands = self.bot.tree.get_commands()

            embed = discord.Embed(
                title="Bot Commands",
                description="Here are the slash commands you can use:",
                color=discord.Color.blue(),
            )

            # List every top-level slash command (ignore groups/subcommands for simplicity)
            for cmd in all_commands:
                if isinstance(cmd, app_commands.Command):
                    embed.add_field(
                        name=f"/{cmd.name}",
                        value=(cmd.description or "No description provided."),
                        inline=False,
                    )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            self.logger.info(f"Displayed a general help list to {interaction.user}.")
            return

        # If a command name is provided, attempt to find and display details for it.
        # Note: This checks top-level commands only, not subcommands.
        cmd = self.bot.tree.get_command(command, type=discord.AppCommandType.chat_input)

        if cmd is None:
            # No command found with this name
            await interaction.response.send_message(
                f"No slash command named `/{command}` found.", ephemeral=True
            )
            self.logger.info(
                f"User {interaction.user} requested help for unknown command '{command}'."
            )
            return

        # Build a detailed embed for the specified command
        embed = discord.Embed(
            title=f"Help: /{cmd.name}",
            description=cmd.description or "No description provided.",
            color=discord.Color.green(),
        )

        # If you wanted to show parameters, usage, or subcommands, you could expand here.
        # For instance, if you have slash command options, you could list them out.

        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.logger.info(
            f"Displayed detailed help for /{cmd.name} to {interaction.user}."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
