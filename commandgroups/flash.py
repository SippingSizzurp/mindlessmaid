import typing
import discord
import asyncio

flash = discord.SlashCommandGroup("nude", "Commands to manage the flash system")


@flash.command(name="send", description="Send an image or video to the current channel")
async def send_image(ctx: discord.ApplicationContext,
                     message: typing.Optional[str] = None,
                     anonymous: typing.Optional[bool] = False):
    # Ask the user to reply with an image or video
    await ctx.respond("Post in this channel with an image or video.", ephemeral=True)

    # Wait for the user's reply
    reply = await ctx.bot.wait_for(
        "message",
        check=lambda message: message.author == ctx.author and message.channel == ctx.channel,
        timeout=480  # 8 minutes
    )

    # Check if the reply has attachments
    if not reply.attachments:
        await ctx.respond("Please reply to this command with an image or video.", ephemeral=True)
        return

    # Delete the replied message
    await reply.delete()

    sent_messages = []  # List to store sent messages

    for attachment in reply.attachments:
        # Create a new embed for each attachment
        embed = discord.Embed(title="New Media", color=discord.Color.blue())
        attachment_url = attachment.url

        # Extract the file extension by splitting the URL and removing query parameters
        file_extension = attachment_url.split(".")[-1].split("?")[0].lower()

        # CHECKS IF THE FILE IS AN IMAGE
        if file_extension in ["png", "jpg", "jpeg", "gif", "webp"]:
            embed.set_image(url=attachment_url)
        # CHECKS IF THE FILE IS A VIDEO
        elif file_extension in ["mp4", "webm", "mov"]:
            video = await ctx.send(file=await attachment.to_file())
        else:
            await ctx.respond("Unsupported file format. Please reply to this command with an image or video.",
                              ephemeral=True)
            return

        # Add optional message to the embed description
        if message:
            embed.description = message

        # Send the embed to the flash channel
        if anonymous:
            sent_message = await ctx.send(embed=embed)
        else:
            embed.description = f"{embed.description}\nSent by {ctx.author.mention}"
            sent_message = await ctx.send(embed=embed)

        sent_messages.append(sent_message)  # Append sent message to list

        # Add reaction to allow message deletion by the original author
        await sent_message.add_reaction('🗑️')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '🗑️' and reaction.message.id in [msg.id for msg in
                                                                                               sent_messages]

    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', check=check)

        # Find and delete the specific message that was reacted to
        for msg in sent_messages:
            if msg.id == reaction.message.id:
                await msg.delete()
                if 'video' in locals():
                    await video.delete()
                break
    except asyncio.TimeoutError:
        pass
