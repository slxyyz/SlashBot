import discord, logging
from discord.ext import commands
from discord import app_commands

import os, datetime
from datetime import timezone


class CoreCog(commands.Cog):
    """
    A simple Cog that provides basic slash commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @app_commands.command(
        name="cogs", description="List all available cogs in the bot."
    )
    async def list_cogs(self, interaction: discord.Interaction):
        """
        List all cogs found in the 'cogs' folder.
        Displays the results in an embed.
        """
        # Get list of cogs from the "cogs" folder
        cogs = [
            filename[:-3]
            for filename in os.listdir("./cogs")
            if filename.endswith(".py") and not filename.startswith("__")
        ]

        # Create an embed with cog info
        embed = discord.Embed(
            title="Available Cogs",
            description="Here are the cogs currently loaded:",
            color=discord.Color.blue(),
        )

        # Add a field for each cog
        for cog in cogs:
            embed.add_field(
                name=cog.capitalize(),
                value=f"`/{cog.lower()} help` for more info (example)",
                inline=False,
            )

        # Send as an ephemeral message
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.logger.info(f"Listed cogs to user {interaction.user}.")

    # Ping command
    @app_commands.command(name="ping", description="Checks the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        """Responds with the bot's latency."""
        latency = round(self.bot.latency * 1000)  # Convert to milliseconds
        await interaction.response.send_message(f"Pong! Latency: {latency}ms")
        self.logger.info(
            f"Ping command used by {interaction.user}. Latency: {latency}ms"
        )

    # Botinfo command
    @app_commands.command(name="info", description="Displays information about the bot")
    async def info(self, interaction: discord.Interaction):
        """Displays bot information."""
        current_time = datetime.datetime.now(timezone.utc)  # Set current time
        uptime = current_time - self.bot.start_time  # Calculate uptime
        uptime_str = str(uptime).split(".")[0]  # Convert to string

        # Create embed
        embed = discord.Embed(title="Bot Information", color=discord.Color.blue())
        embed.add_field(name="Uptime", value=uptime_str, inline=True)
        embed.add_field(name="Version", value="0.1", inline=True)
        embed.add_field(name="Owner", value="slxyyz", inline=True)
        embed.set_footer(text="Bot developed by slxyyz")

        # Send embed
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.logger.info(f"Info command used by {interaction.user}.")

    # Serverinfo command
    @app_commands.command(
        name="serverinfo", description="Displays information about the server"
    )
    async def serverinfo(self, interaction: discord.Interaction):
        """Displays server information."""

        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )

        guild = interaction.guild
        embed = discord.Embed(title=f"{guild.name}", color=discord.Color.purple())
        embed.add_field(name="Server ID", value=str(guild.id), inline=False)
        embed.add_field(
            name="Owner", value=f"{guild.owner} (ID: {guild.owner_id})", inline=False
        )
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        embed.set_footer(text="Server Info")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.logger.info(
            f"Server info requested by {interaction.user} in guild {guild.name}."
        )

    # Channelinfo command
    @app_commands.command(
        name="channelinfo", description="Displays information about a specific channel."
    )
    async def channelinfo(
        self, interaction: discord.Interaction, channel: discord.TextChannel = None
    ):
        """
        Retrieves information about the specified channel.
        If no channel is provided, shows info about the current one.
        """
        # Default to the channel in which the command was used
        if channel is None:
            channel = interaction.channel

        embed = discord.Embed(title=f"{channel.name}", color=discord.Color.gold())
        embed.add_field(name="Channel ID", value=str(channel.id), inline=True)
        embed.add_field(name="Channel Type", value=str(channel.type), inline=False)
        embed.add_field(
            name="Created At",
            value=channel.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            inline=True,
        )
        embed.add_field(
            name="Category",
            value=channel.category.name if channel.category else "No Category",
            inline=True,
        )
        # For text channels, 'topic' can exist:
        topic = getattr(channel, "topic", None)
        if topic:
            embed.add_field(name="Topic", value=topic, inline=True)

        embed.set_footer(text="Channel Info")

        # Send as an ephemeral
        await interaction.response.send_message(embed=embed, ephemeral=True)

        self.logger.info(
            f"Channel info requested by {interaction.user} for channel {channel.name}."
        )

    # Set activity command
    @app_commands.command(
        name="setactivity",
        description="Sets the bot's activity (displayed as 'Playing ...').",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setactivity(self, interaction: discord.Interaction, activity: str):
        """
        Updates the bot's displayed activity.
        Only users with Administrator permission can do this.
        """
        # Create the new activity object
        new_activity = discord.Game(name=activity)

        # Only changes bots activity, not status
        await self.bot.change_presence(activity=new_activity)

        # Confirm to the user
        await interaction.response.send_message(
            f"Activity updated to: '{activity}'", ephemeral=True
        )

        self.logger.info(f"Activity updated to '{activity}' by {interaction.user}.")

    # # Invite Link command
    # @app_commands.command(name="invite", description="Get the bot's invite link")
    # async def invite(self, interaction: discord.Interaction):
    #     """Provides the bot's invite link."""
    #         invite_url = discord.utils.oauth_url(
    #             self.bot.user.id,
    #             permissions=discord.Permissions(permissions=8),
    #             scopes=["bot", "applications.commands"],
    #         )
    #         await interaction.response.send_message(
    #             f"Invite me to your server using this link: {invite_url}",
    #             ephemeral=True,
    #         )
    #         self.logger.info(f"Invite link requested by {interaction.user}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(CoreCog(bot))
