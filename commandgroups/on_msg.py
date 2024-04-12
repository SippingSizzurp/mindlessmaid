from database import *
import re


class Triggers:

    @staticmethod
    async def check(server_id, ch_id, message):
        triggers = Database.load_triggers(server_id)
        nochat_entries = Database.fetch_nochat(server_id, ch_id)
        user = message.author
        user_roles = user.roles
        roles = Database.load_roles(server_id)

        for row in triggers:
            trigger = row[1]
            response = row[2]
            intended = row[3]
            pattern = fr"\b{re.escape(trigger)}\b"

            # Check if the current trigger is disabled for the current channel
            if any(entry[2] == trigger for entry in nochat_entries):
                continue

            # Check if the trigger is present in the message content
            if re.search(pattern, message.content):
                # Check if the message owner has a role that matches the intended role for the trigger
                conflicting_roles = [role for role in roles if role[0] == str(server_id) and role[2] == intended and role[3] == "add" and str(role[1]) in [str(role.id) for role in user_roles]]
                print(conflicting_roles)
                if conflicting_roles:
                    await message.reply(response)
                break
