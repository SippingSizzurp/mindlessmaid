from discord.ext import commands
from modals import *
import discord
from main import bot


@bot.slash_command(name="verify", description="[ADMIN] Verify a member or an ice breaker")
async def verify(ctx: discord.ApplicationContext, member: discord.Member):
    return
