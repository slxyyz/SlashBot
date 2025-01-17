import discord, logging
from discord.ext import commands
from discord import app_commands

import docker
import docker.errors


class DockerCog(commands.Cog):
    """_summary_
    Provides commands for interacting with an underlying Docker socket.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

        # Connect to Docker socket
        try:
            self.client = docker.from_env()
            
            running_containers = self.client.containers.list() # Get all running container
            all_containers = self.client.containers.list(all=True) # Get all container
            stopped_containers = [
                c for c in all_containers if c not in running_containers # Check for stopped container
            ]
        except docker.errors.DockerException as e:
            self.logger.error(f"Connection to Docker socket failed: {e}")

        # Helper function to format container info 
        def format_container_info(self, container, running=True):
            """Formats container information for display."""
            # Get container details
            name = container.name
            image = (
                container.image.tags[0]
                if container.image.tags
                else container.image.short_id
            )
            status = container.status.capitalize()
            uptime = self.get_uptime(container)
            emoji = "🟢" if running else "🔴"
            info = (
                f"{emoji} **Name:** `{name}`\n"
                f"**Image:** `{image}`\n"
                f"**Uptime:** `{uptime}`\n"
                f"**Status:** `{status}`\n"
                "----------------------------------\n"
            )
            return info

        @app_commands.command(
            name="do_ps", description="List all available containers."
        )
        async def do_ps(self, interaction: discord.Interaction, container=None):
            """_summary_

            Args:
                interaction (discord.Interaction): _description_
                container (_type_, optional): _description_. Defaults to None.
            """
            try:
                if self.client is None:
                    await interaction.respond.send_message(
                        "❌ Docker client is not available. Please check Docker connection."
                    )

            except docker.errors.DockerException as e:
                self.logger.error(f"Couldnt fetch container list: {e}")
