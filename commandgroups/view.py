from discord.ext import commands
from modals import *
import discord


view = discord.SlashCommandGroup("view", "Commands to view various systems")


@commands.has_permissions(manage_roles=True)
@view.command(name="roles", description="View roles being added/removed for /verify")
async def view_roles(ctx: discord.ApplicationContext):
    await ctx.respond(view=ViewRoles(ctx.guild.id), ephemeral=True)


@commands.has_permissions(manage_messages=True)
@view.command(name="triggers", description="View a list of the current triggers")
async def viewtriggers(ctx: discord.ApplicationContext):
    triggers = Database.load_triggers(ctx.guild.id)

    if not triggers:
        await ctx.respond("There are no triggers set for this guild.")
        return

    trigger_list = "\n".join(f"{row[1]}: {row[2]}" for row in triggers)

    embed = discord.Embed(title="Current Triggers", description=trigger_list, color=discord.Color.green())

    await ctx.respond(embed=embed)