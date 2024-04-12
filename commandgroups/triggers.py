from discord.ext import commands
from modals import *
import discord

triggers = discord.SlashCommandGroup("triggers", "Commands to manage triggers")


@commands.has_permissions(manage_channels=True)
@triggers.command(name="channel-settings", description="[ADMIN] Disables/Enables specific triggers in specified channels")
async def disable_triggers(ctx: discord.ApplicationContext, trigger: str):
    await ctx.respond(view=DisableTriggers(ctx.guild.id, trigger, ctx.guild), ephemeral=True)
