import discord
from database import *

#####################
# MANAGE ROLE CHAIN #
#####################


class ManageRolesView(discord.ui.View):
    def __init__(self, server_id):
        super().__init__()
        self.server_id = server_id

    @discord.ui.select(
        placeholder="Role type",
        min_values= 1,
        max_values= 1,
        options= [
            discord.SelectOption(label="Sir", description="Manage the roles for sirs"),
            discord.SelectOption(label="Cunt", description="Manage roles for Cunts")
        ]
    )
    async def callback(self, select, interaction):
        typee = select.values[0].lower()
        await interaction.response.send_message(view=ManageRolesView2(typee, self.server_id), ephemeral=True)


class ManageRolesView2(discord.ui.View):
    def __init__(self, typee, server_id):
        super().__init__()
        self.typee = typee
        self.server_id = server_id

    @discord.ui.select(
        placeholder="Method",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Add", description="Adds a role to be **ADDED** when verified"),
            discord.SelectOption(label="Remove", description="Adds a role to be **REMOVED** when verified"),
            discord.SelectOption(label="Delete", description="Deletes a role from being added **OR** removed when verified")
        ]
    )
    async def callback(self, select, interaction):
        method = select.values[0].lower()
        await interaction.response.send_message(view=ManageRolesView3(self.typee, self.server_id, method), ephemeral=True)


class ManageRolesView3(discord.ui.View):
    def __init__(self, typee, server_id, method):
        super().__init__()
        self.typee = typee
        self.server_id = server_id
        self.method = method

    @discord.ui.role_select(max_values=9)
    async def callback(self, select, interaction):
        embed = discord.Embed(title="SUCCESS")
        for role in select.values:
            Database.save_roles(self.server_id, role.id, self.typee, self.method)
            embed.add_field(name=f"{self.method}'d", value=role.mention, inline=False)

        await interaction.response.send_message(embed=embed)


########################
# VERIFY MESSAGE CHAIN #
########################


class VerifyMessageView(discord.ui.View):
    def __init__(self, server_id):
        super().__init__()
        self.server_id = server_id

    @discord.ui.select(
        placeholder="Role type",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Sir", description="Manage the welcome message for sirs"),
            discord.SelectOption(label="Cunt", description="Manage the welcome message for Cunts")
        ]
    )
    async def callback(self, select, interaction):
        await interaction.response.send_modal(VerifyMessageView2(self.server_id, select.values[0].lower(), title=f"Change Welcome Message for {select.values[0]}"))


class VerifyMessageView2(discord.ui.Modal):
    def __init__(self, server_id, role_type, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Message: ", style=discord.InputTextStyle.long))
        self.server_id = server_id
        self.role_type = role_type

    async def callback(self, interaction: discord.Interaction):
        Database.update_server_message(self.server_id, self.role_type, self.children[0].value)
        embed = discord.Embed(title=f"SUCCESSFULLY CHANGED WELCOME MESSAGE FOR {self.role_type.upper()}'S")
        embed.add_field(name="New Welcome Message", value=self.children[0].value)
        await interaction.response.send_message(embeds=[embed])

##########################
# DISABLE TRIGGERS CHAIN #
##########################


class DisableTriggers(discord.ui.View):
    def __init__(self, server_id, trigger, server):
        super().__init__()
        self.server_id = server_id
        self.trigger = trigger
        self.server = server

    @discord.ui.select(
        placeholder="METHOD",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Enable", description="Enable the trigger in the specified channel"),
            discord.SelectOption(label="Disable", description="Disable the trigger in the specified channel")
        ]
    )
    async def callback(self, select, interaction):
        await interaction.response.send_message(view=DisableTriggers2(self.server_id, self.trigger, select.values[0], self.server), ephemeral=True)


class DisableTriggers2(discord.ui.View):
    def __init__(self, server_id,trigger, method, server):
        super().__init__()
        self.server_id = server_id
        self.trigger = trigger
        self.method = method
        self.server= server

    @discord.ui.channel_select(
        placeholder="CHANNELS",
        channel_types=[discord.ChannelType.text],
        min_values=1,
        max_values=9,
    )
    async def callback(self, select, interaction):
        embed = discord.Embed(title=f"TRIGGER {self.method.upper()}D")
        embed.add_field(name="TRIGGER:", value=self.trigger)
        if self.method.lower() == "disable":
            if Database.fetch_trigger(self.server_id, self.trigger):
                for channel in self.get_channels(self.server, select.values):
                    if Database.fetch_nochat_single(self.server_id, channel.id, self.trigger):
                        pass
                    else:
                        Database.disable_trigger(str(self.server_id), channel.id, self.trigger)
                        embed.add_field(name="EFFECTED", value=channel.mention, inline=False)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("That trigger does not exist in this server")

        if self.method.lower() == "enable":
            if Database.fetch_trigger(self.server_id, self.trigger):
                for channel in self.get_channels(self.server, select.values):
                    if Database.fetch_nochat_single(self.server_id, channel.id, self.trigger):
                        Database.enable_trigger(self.server_id, channel.id, self.trigger)
                        embed.add_field(name="EFFECTED", value=channel.mention, inline=False)
                    else:
                        pass
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("That trigger does not exist in this server")

    @classmethod
    def get_channels(cls, server: discord.Guild, channels):
        channel_objects = []
        for channel in channels:
            channel_objects.append(server.get_channel(channel.id))

        return channel_objects


################
# REPORT CHAIN #
################

class ReportModal(discord.ui.Modal):
    def __init__(self, ctx, message, ch, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Explanation: ", style=discord.InputTextStyle.long))
        self.ctx = ctx
        self.message = message
        self.ch = ch

    async def callback(self, interaction: discord.Interaction):
        await interaction.respond("Message has been reported", ephemeral=True)

        embed = discord.Embed(title="NEW REPORT")
        embed.add_field(name="USER", value=self.message.author.mention, inline=False)
        embed.add_field(name="Message", value=self.message.content)
        embed.add_field(name="Message Link", value=f"[HERE]({self.message.jump_url})")
        embed.set_footer(text=f"Reported by: {self.ctx.author.display_name}")
        embed.add_field(name="Explanation", value=self.children[0].value, inline=False)
        await self.ch.send(embed=embed)

####################
# VIEW ROLES CHAIN #
####################


class ViewRoles(discord.ui.View):
    def __init__(self, serverid):
        super().__init__()
        self.serverid = serverid

    @discord.ui.select(
        placeholder="Role type",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Sir", description="View the roles for sirs"),
            discord.SelectOption(label="Cunt", description="View the roles for Cunts")
        ]
    )
    async def callback(self, select, interaction):
        typee = select.values[0]
        roles_to_display = [(row[1], row[3]) for row in Database.load_roles_one(self.serverid, typee.lower()) if
                            row[2] == typee.lower() and row[3] in ["add", "remove"]]
        if not roles_to_display:
            await interaction.response.send_message(f"No roles to display for {typee} verification.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Roles being added/removed for {typee} verification")
        for role_id, add_or_remove in roles_to_display:
            role = discord.utils.get(interaction.guild.roles, id=role_id)
            if role:
                embed.add_field(name=f"{add_or_remove.title()} role", value=role.mention, inline=False)

        await interaction.response.send_message(embed=embed)


#########################
# MANAGE TRIGGERS CHAIN #
#########################

class ManageTriggers(discord.ui.View):
    def __init__(self, server_id):
        super().__init__()
        self.server_id = server_id


    @discord.ui.select(
        placeholder="Role type",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Sir", description="Add/Remove a trigger word for sirs"),
            discord.SelectOption(label="Cunt", description="Add/Remove a trigger word for cunts"),
        ]
    )
    async def callback(self, select, interaction):
        typee = select.values
        await interaction.response.send_message(view=ManageTriggers2(typee, self.server_id), ephemeral=True)


class ManageTriggers2(discord.ui.View):
    def __init__(self, typee, server_id):
        super().__init__()
        self.typee = typee
        self.server_id = server_id

    @discord.ui.select(
        placeholder="Action",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Add", description="Add a trigger word"),
            discord.SelectOption(label="Remove", description="Remove a trigger word"),
        ]
    )
    async def callback(self, select, interaction):
        if select.values[0] == "Add":
            await interaction.response.send_modal(ManageTriggers3(self.typee, self.server_id, title="ADD A TRIGGER"))
        else:
            await interaction.response.send_modal(ManageTriggers4(self.typee, self.server_id, title="REMOVE A TRIGGER"))

class ManageTriggers3(discord.ui.Modal):
    def __init__(self, typee, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="trigger: ", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="response: ", style=discord.InputTextStyle.long))
        self.typee = typee
        self.server_id = server_id

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="SUCCESS")
        embed.add_field(name="TRIGGER", value= self.children[0].value, inline=False)
        embed.add_field(name="RESPONSE", value= self.children[1].value, inline=False)
        for typ in self.typee:
            Database.save_triggers(self.server_id, self.children[0].value, self.children[1].value, typ.lower())
            embed.add_field(name="EFFECTED", value= typ, inline=True)

        await interaction.response.send_message(embed=embed)


class ManageTriggers4(discord.ui.Modal):
    def __init__(self, typee, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="trigger: ", style=discord.InputTextStyle.short))
        self.typee = typee
        self.server_id = server_id

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="SUCCESS")
        embed.add_field(name="TRIGGER", value=self.children[0].value, inline=False)

        for typ in self.typee:
            Database.delete_trigger(self.server_id, self.children[0].value, typ.lower())
            embed.add_field(name="EFFECTED", value=typ, inline=True)

        await interaction.response.send_message(embed=embed)

################
# VERIFY CHAIN #
################


class Verify(discord.ui.View):
    def __init__(self, author: discord.Member, member: discord.Member, server: discord.Guild, perms):
        super().__init__()
        self.member = member
        self.author = author
        self.server = server
        self.perms = perms

    @discord.ui.select(
        placeholder="VERIFY",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Verify Member", description="[ADMIN] Verify a user"),
            discord.SelectOption(label="Verify Ice Breaker", description="Verify an Ice Breaker"),
        ]
    )
    async def callback(self, select, interaction):
        if select.values[0] == "Verify Ice Breaker":
            trusted_roles = Database.load_trusted_roles(self.server.id)
            author_roles = self.author.roles
            trusted = []
            for role in trusted_roles:
                roleobj = self.server.get_role(int(role[1]))
                trusted.append(roleobj)
            if any(role in author_roles for role in trusted):
                await interaction.response.send_message(view=Verify3(self.member, self.server), ephemeral=True)
            else:
                await interaction.response.send_message("You do not have a trusted role", ephemeral=True)
        else:
            if self.perms:
                await interaction.response.send_message(view=Verify2(self.member, self.server), ephemeral=True)
            else:
                await interaction.response.send_message("You do not have an admin role", ephemeral=True)


class Verify2(discord.ui.View):
    def __init__(self, member, server: discord.Guild):
        super().__init__()
        self.member = member
        self.server = server

    @discord.ui.select(
        placeholder="Role Type",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Sir", description="Verify a sir"),
            discord.SelectOption(label="Cunt", description="Verify a cunt"),
        ]
    )
    async def callback(self, select, interaction):
        roles = Database.load_roles(self.server.id)
        role_type_lower = select.values[0].lower()
        roles_to_modify = [row for row in roles if row[2] == role_type_lower and row[3] in ["add", "remove"]]

        roles_to_add = []
        roles_to_remove = []

        for row in roles_to_modify:
            role_id = row[1]
            add_or_remove = row[3]

            role = self.server.get_role(role_id)
            if role:
                if add_or_remove == "add":
                    roles_to_add.append(role)
                elif add_or_remove == "remove":
                    roles_to_remove.append(role)

        for role in roles_to_add:
            await self.member.add_roles(role)

        for role in roles_to_remove:
            await self.member.remove_roles(role)

        c.execute("SELECT message FROM custommsg WHERE serverid = ? AND roletype = ?", (self.server.id, role_type_lower))
        custom_message = c.fetchone()
        if custom_message:
            custom_message = custom_message[0]
            await interaction.response.send_message(custom_message)
        else:
            await interaction.response.send_message(f"{self.member.display_name} has been verified as a {select.values[0]}!")


class Verify3(discord.ui.View):
    def __init__(self, member, server: discord.Guild):
        super().__init__()
        self.member = member
        self.server = server

    @discord.ui.select(
        placeholder="Role Type",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Sir", description="Verify a sir"),
            discord.SelectOption(label="Cunt", description="Verify a cunt"),
        ]
    )
    async def callback(self, select, interaction):
        roles = Database.load_ice_roles(self.server.id)
        role_type_lower = select.values[0].lower()
        roles_to_modify = [row for row in roles if row[2] == role_type_lower and row[3] in ["add", "remove"]]

        print(roles_to_modify)
        roles_to_add = []
        roles_to_remove = []

        for row in roles_to_modify:
            role_id = row[1]
            add_or_remove = row[3]

            role = self.server.get_role(role_id)
            if role:
                if add_or_remove == "add":
                    roles_to_add.append(role)
                elif add_or_remove == "remove":
                    roles_to_remove.append(role)

        for role in roles_to_add:
            await self.member.add_roles(role)

        for role in roles_to_remove:
            await self.member.remove_roles(role)

        await interaction.response.send_message(f"{self.member.display_name} has been verified as a {select.values[0]}!")

#################
# TRUSTED CHAIN #
#################


class Trusted(discord.ui.View):
    def __init__(self, serverid):
        super().__init__()
        self.serverid = serverid

    @discord.ui.select(
        placeholder="Action",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Add", description="Add a trusted role"),
            discord.SelectOption(label="Remove", description="Remove a trusted role"),
        ]
    )
    async def callback(self, select, interaction):
            if select.values[0] == "Add":
                await interaction.response.send_message(view=Trusted2(self.serverid), ephemeral=True)
            else:
                await interaction.response.send_message(view=Trusted3(self.serverid), ephemeral=True)


class Trusted2(discord.ui.View):
    def __init__(self, serverid):
        super().__init__()
        self.serverid = serverid

    @discord.ui.role_select(max_values=9)
    async def callback(self, select, interaction):
        embed = discord.Embed(title="SUCCESS")
        for role in select.values:
            Database.save_trusted_role(self.serverid, role.id)
            embed.add_field(name="ROLE ADDED", value=role.mention, inline=False)
        await interaction.response.send_message(embed=embed)


class Trusted3(discord.ui.View):
    def __init__(self, serverid):
        super().__init__()
        self.serverid = serverid

    @discord.ui.role_select(max_values=9)
    async def callback(self, select, interaction):
        embed = discord.Embed(title="SUCCESS")
        for role in select.values:
            Database.delete_trusted_role(self.serverid, role.id)
            embed.add_field(name="ROLES REMOVED", value=role.mention, inline=False)
        await interaction.response.send_message(embed=embed)


#################
# CHANNEL TYPE  #
#################

class ChannelType(discord.ui.View):
    def __init__(self, serverid):
        super().__init__()
        self.serverid = serverid

    @discord.ui.select(
        placeholder="TYPE",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Counting", description="Mark a channel as counting"),
            discord.SelectOption(label="Flash", description="Mark a channel as flash"),
            discord.SelectOption(label="Void", description="Mark a channel as void"),
        ]
    )
    async def callback(self, select, interaction):
        await interaction.response.send_message(view=ChannelType2(self.serverid, select.values[0]), ephemeral=True)


class ChannelType2(discord.ui.View):
    def __init__(self, serverid, typee):
        super().__init__()
        self.serverid = serverid
        self.typee = typee

    @discord.ui.channel_select()
    async def callback(self, select, interaction):
        existing_channels = Database.load_channels(self.serverid)
        channel_entry = next((row for row in existing_channels if row[1] == select.values[0].id), None)

        if channel_entry:
            Database.channel_update(self.typee, self.serverid, select.values[0].id)
            await interaction.response.send_message(f"The type of channel {select.values[0].mention} has been updated to '{self.typee}'.")
        else:
            Database.save_channels(self.serverid, select.values[0].id, self.typee.lower())
            Database.save_count(self.serverid, 0)
            await interaction.response.send_message(f"The type of channel {select.values[0].mention} has been set to '{self.typee}'.")


#############################
# MANAGE TRUSTED ROLE CHAIN #
#############################


class ManageTrustedRolesView(discord.ui.View):
    def __init__(self, server_id):
        super().__init__()
        self.server_id = server_id

    @discord.ui.select(
        placeholder="Role type",
        min_values= 1,
        max_values= 1,
        options= [
            discord.SelectOption(label="Sir", description="Manage the roles for sirs"),
            discord.SelectOption(label="Cunt", description="Manage roles for Cunts")
        ]
    )
    async def callback(self, select, interaction):
        typee = select.values[0]
        await interaction.response.send_message(view=ManageTrustedRolesView2(typee, self.server_id), ephemeral=True)


class ManageTrustedRolesView2(discord.ui.View):
    def __init__(self, typee, server_id):
        super().__init__()
        self.typee = typee
        self.server_id = server_id

    @discord.ui.select(
        placeholder="Method",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Add", description="Adds a role to be **ADDED** when verified"),
            discord.SelectOption(label="Remove", description="Adds a role to be **REMOVED** when verified"),
            discord.SelectOption(label="Delete", description="Deletes a role from being added **OR** removed when verified")
        ]
    )
    async def callback(self, select, interaction):
        method = select.values[0]
        await interaction.response.send_message(view=ManageTrustedRolesView3(self.typee, self.server_id, method), ephemeral=True)


class ManageTrustedRolesView3(discord.ui.View):
    def __init__(self, typee, server_id, method):
        super().__init__()
        self.typee = typee
        self.server_id = server_id
        self.method = method

    @discord.ui.role_select(max_values=9)
    async def callback(self, select, interaction):
        embed = discord.Embed(title="SUCCESS")
        for role in select.values:
            Database.save_trusted_roles(self.server_id, role.id)
            embed.add_field(name=f"{self.method}'d", value=role.mention, inline=False)

        await interaction.response.send_message(embed=embed)


#############################
# MANAGE ICE ROLE CHAIN #
#############################


class ManageIceRolesView(discord.ui.View):
    def __init__(self, server_id):
        super().__init__()
        self.server_id = server_id

    @discord.ui.select(
        placeholder="Role type",
        min_values= 1,
        max_values= 1,
        options= [
            discord.SelectOption(label="Sir", description="Manage the roles for sirs"),
            discord.SelectOption(label="Cunt", description="Manage roles for Cunts")
        ]
    )
    async def callback(self, select, interaction):
        typee = select.values[0].lower()
        print(typee)
        await interaction.response.send_message(view=ManageIceRolesView2(typee, self.server_id), ephemeral=True)


class ManageIceRolesView2(discord.ui.View):
    def __init__(self, typee, server_id):
        super().__init__()
        self.typee = typee
        self.server_id = server_id

    @discord.ui.select(
        placeholder="Method",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Add", description="Adds a role to be **ADDED** when verified"),
            discord.SelectOption(label="Remove", description="Adds a role to be **REMOVED** when verified"),
            discord.SelectOption(label="Delete", description="Deletes a role from being added **OR** removed when verified")
        ]
    )
    async def callback(self, select, interaction):
        method = select.values[0].lower()
        await interaction.response.send_message(view=ManageIceRolesView3(self.typee, self.server_id, method), ephemeral=True)


class ManageIceRolesView3(discord.ui.View):
    def __init__(self, typee, server_id, method):
        super().__init__()
        self.typee = typee
        self.server_id = server_id
        self.method = method

    @discord.ui.role_select(max_values=9)
    async def callback(self, select, interaction):
        embed = discord.Embed(title="SUCCESS")
        for role in select.values:
            print(self.server_id, role.id, self.typee, self.method)
            Database.save_ice_roles(self.server_id, role.id, self.typee, self.method)
            embed.add_field(name=f"{self.method}'d", value=role.mention, inline=False)

        await interaction.response.send_message(embed=embed)