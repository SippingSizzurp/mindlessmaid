from commandgroups import manage, triggers, view, flash
import asyncio
from modals import *
from commandgroups.on_msg import *
from discord.ext import commands


bot = discord.Bot(intents=discord.Intents.all(), help_command=None)


async def change_status():
    activities = [
        discord.Activity(type=discord.ActivityType.watching, name="V3.0"),
        discord.Activity(type=discord.ActivityType.playing, name="Made by @sippingsizzurp")
    ]

    while True:
        for activity in activities:
            await bot.change_presence(activity=activity)
            await asyncio.sleep(10)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready")
    asyncio.create_task(change_status())


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    server_id = str(message.guild.id)

    await Triggers.check(message.guild.id, message.channel.id, message)
    c.execute("select * from channels where serverid = ? and type = 'flash'", (server_id,))
    chtype = c.fetchone()
    c.execute("select * from channels where serverid = ? and type = 'void'", (server_id,))
    chtype2 = c.fetchone()

    if chtype and message.channel.id == chtype[1]:
        await asyncio.sleep(120)
        await message.delete()

    if chtype2 and message.channel.id == chtype2[1]:
        await asyncio.sleep(1)
        await message.delete()

    try:
        counter = int(message.content)
        c.execute("select * from channels where serverid = ? and type = 'counting'", (server_id,))
        ch = c.fetchone()
        c.execute("select * from count where serverid = ?", (server_id,))
        count = c.fetchone()
        if message.channel.id == ch[1]:
            c.execute("select * from count where serverid = ?", (server_id,))
            countee = c.fetchone()
            if countee[2] != message.author.id or countee[2] is None:
                if counter == count[1] + 1:
                    await message.add_reaction('✅')
                    c.execute("UPDATE count SET count = ? WHERE serverid = ?", (count[1] + 1, server_id))
                    c.execute("update count set last = ? where serverid = ?", (message.author.id, server_id))
                    conn.commit()
                else:
                    await message.channel.send(
                        f"{message.author.mention} has lost count! The next number was {count[1] + 1} Punish the guilty!")
                    c.execute("UPDATE count SET count = 0 WHERE serverid = ?", (server_id,))
                    c.execute("UPDATE count SET last = NULL WHERE serverid = ?", (server_id,))
                    conn.commit()
                    return
            else:
                await message.channel.send(f"{message.author.mention} has double counted! Punish the guilty!")
                c.execute("UPDATE count SET count = 0 WHERE serverid = ?", (server_id,))
                c.execute("UPDATE count SET last = NULL WHERE serverid = ?", (server_id,))
                conn.commit()
                return
    except ValueError:
        return


@bot.message_command(name="Report message")
async def report(ctx: discord.ApplicationContext, message: discord.Message):
    ch = ctx.guild.get_channel(1028583352405602304)
    await ctx.send_modal(ReportModal(ctx, message, ch, title="REPORT"))


@bot.slash_command(name="verify", description="[ADMIN] Verify a member or an ice breaker")
async def verify(ctx: discord.ApplicationContext, member: discord.Member):
    perms = ctx.respond(ctx.author.guild_permissions.manage_roles)
    await ctx.respond(view=Verify(ctx.author, member, ctx.guild, perms), ephemeral=True)


bot.add_application_command(manage.manage)
bot.add_application_command(triggers.triggers)
bot.add_application_command(view.view)
bot.add_application_command(flash.flash)

bot.run("")
