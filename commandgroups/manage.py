from discord.ext import commands
from modals import *
import discord


manage = discord.SlashCommandGroup("manage", "Commands to manage the various systems")


@commands.has_permissions(manage_roles=True)
@manage.command(name="roles", description="[ADMIN] Add, remove, or delete a role for /verify")
async def roles(ctx: discord.ApplicationContext):
    await ctx.respond(view=ManageRolesView(ctx.guild.id), ephemeral=True)


@commands.has_permissions(manage_roles=True)
@manage.command(name="icebreaker-roles", description="[ADMIN] Add, remove, or delete a role for /verify ice breakers")
async def rolesice(ctx: discord.ApplicationContext):
    await ctx.respond(view=ManageIceRolesView(ctx.guild.id), ephemeral=True)


@commands.has_permissions(manage_roles=True)
@manage.command(name="verify-message", description="[ADMIN] Update the custom verification message for a role type")
async def verify_message(ctx: discord.ApplicationContext):
    await ctx.respond(view=VerifyMessageView(ctx.guild.id), ephemeral=True)

@commands.has_permissions(manage_messages=True)
@manage.command(name="triggers", description="[ADMIN] Update the list of trigger words")
async def triggers(ctx: discord.ApplicationContext):
    await ctx.respond(view=ManageTriggers(ctx.guild.id), ephemeral=True)


@commands.has_permissions(manage_roles=True)
@manage.command(name="trusted", description="[ADMIN] Adds a trusted role")
async def trusted(ctx:discord.ApplicationContext):
    await ctx.respond(view=Trusted(ctx.guild.id), ephemeral=True)


@commands.has_permissions(manage_channels=True)
@manage.command(name="channels", description="[ADMIN] Update or set a channel to a specific type")
async def channels(ctx:discord.ApplicationContext):
    await ctx.respond(view=ChannelType(ctx.guild.id), ephemeral=True)
