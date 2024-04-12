import sqlite3

conn = sqlite3.connect("mindless.db")
c = conn.cursor()


class Database:

    @staticmethod
    def load_roles(serverid):
        c.execute("select * from roles where serverid = ?", (serverid,))
        return c.fetchall()

    @staticmethod
    def save_roles(serverid, roleid, sirorcunt, addorremove):
        c.execute("insert into roles values (?, ?, ?, ?)", (serverid, roleid, sirorcunt, addorremove,))
        conn.commit()

    @staticmethod
    def load_trusted_roles(serverid):
        c.execute("select * from trusted where serverid = ?", (serverid,))
        return c.fetchall()

    @staticmethod
    def save_trusted_roles(serverid, roleid):
        c.execute("insert into trusted values (?, ?)", (serverid, roleid))
        conn.commit()

    @staticmethod
    def load_ice_roles(serverid):
        c.execute("select * from rolesice where serverid = ?", (serverid,))
        return c.fetchall()

    @staticmethod
    def save_ice_roles(serverid, roleid, sirorcunt, addorremove):
        c.execute("insert into rolesice values (?, ?, ?, ?)", (serverid, roleid, sirorcunt, addorremove,))
        conn.commit()

    @staticmethod
    def load_channels(serverid):
        c.execute("select * from channels where serverid = ?", (serverid,))
        return c.fetchall()

    @staticmethod
    def save_channels(serverid, channelid, typee):
        c.execute("insert into channels values (?, ?, ?)", (serverid, channelid, typee))
        conn.commit()

    @staticmethod
    def load_triggers(serverid):
        c.execute("select * from triggers where serverid = ?", (serverid,))
        return c.fetchall()

    @staticmethod
    def save_triggers(serverid, trigger, response, intended):
        c.execute("insert into triggers values (?, ?, ?, ?)", (serverid, trigger, response, intended))
        conn.commit()

    @staticmethod
    def delete_trigger(serverid, triggerword, typee):
        c.execute("DELETE FROM triggers WHERE serverid = ? AND trigger = ? AND intended = ?", (serverid, triggerword, typee))
        conn.commit()

    @staticmethod
    def load_teams(serverid):
        c.execute("select * from teams where serverid = ?", (serverid,))
        return c.fetchall()

    @staticmethod
    def save_teams(serverid, member, team):
        c.execute("insert into teams values (?, ?, ?)", (serverid, member, team))
        conn.commit()

    @staticmethod
    def load_count(serverid):
        c.execute("SELECT * FROM count WHERE serverid = ?", (serverid,))
        return c.fetchone()

    @staticmethod
    def save_count(serverid, count):
        c.execute("INSERT OR REPLACE INTO count (serverid, count) VALUES (?, ?)", (serverid, count))
        conn.commit()

    @staticmethod
    def save_nochat(serverid, channelid):
        c.execute("insert into nochat values (?, ?)", (serverid, channelid))
        conn.commit()

    @staticmethod
    def update_server_message(server_id, role_type, custom_message):
        c.execute("SELECT COUNT(*) FROM custommsg WHERE serverid = ? AND roletype = ?", (server_id, role_type.lower()))
        existing_count = c.fetchone()[0]

        if existing_count > 0:
            c.execute("UPDATE custommsg SET message = ? WHERE serverid = ? AND roletype = ?",
                      (custom_message, server_id, role_type.lower()))
        else:
            c.execute("INSERT INTO custommsg (serverid, roletype, message) VALUES (?, ?, ?)",
                      (server_id, role_type.lower(), custom_message))

        conn.commit()

    @staticmethod
    def disable_trigger(server_id, channel_id, trigger):
        c.execute("INSERT INTO nochat (serverid, channelid, trigger) VALUES (?, ?, ?)",
                  (server_id, channel_id, trigger))
        conn.commit()

    @staticmethod
    def enable_trigger(server_id, channel_id, trigger):
        c.execute("DELETE FROM nochat WHERE serverid = ? AND channelid = ? AND trigger = ?",
                  (server_id, channel_id, trigger))
        conn.commit()

    @staticmethod
    def fetch_nochat(server_id, channel_id):
        c.execute("SELECT * FROM nochat WHERE serverid = ? AND channelid = ?", (server_id, channel_id))
        return c.fetchall()

    @staticmethod
    def fetch_nochat_single(server_id, channel_id, trigger):
        c.execute("SELECT * FROM nochat WHERE serverid = ? AND channelid = ? AND trigger = ?", (server_id, channel_id, trigger))
        return c.fetchone()

    @staticmethod
    def fetch_trigger(server_id, trigger):
        c.execute("SELECT * FROM triggers WHERE serverid = ? AND trigger = ?", (server_id, trigger))
        return c.fetchone()

    @staticmethod
    def load_roles_one(serverid, typee):
        c.execute("select * from roles where serverid = ? AND sirorcunt = ?", (serverid, typee))
        return c.fetchall()

    @staticmethod
    def save_trusted_role(serverid, roleid):
        c.execute("INSERT INTO trusted (serverid, roleid) VALUES (?, ?)", (serverid, roleid))
        conn.commit()

    @staticmethod
    def delete_trusted_role(serverid, roleid):
        c.execute("DELETE FROM trusted WHERE serverid = ? AND roleid = ?", (serverid, roleid))
        conn.commit()

    @staticmethod
    def load_trusted_roles(serverid):
        c.execute("SELECT * FROM trusted WHERE serverid = ?", (serverid,))
        return c.fetchall()

    @staticmethod
    def fetch_trusted_role(serverid, roleid):
        c.execute("SELECT * FROM trusted WHERE serverid = ? AND roleid = ?", (serverid, roleid))
        return c.fetchall()

    @staticmethod
    def channel_update(new_type, server_id, channel_id):
        c.execute("UPDATE channels SET type = ? WHERE serverid = ? AND channelid = ?",
                  (new_type.lower(), server_id, channel_id))
        c.execute("update count set count = 0 where serverid = ?", (server_id,))
        conn.commit()

    @staticmethod
    def fetch_flash_channel(server_id: int) -> tuple:
        c.execute("SELECT * FROM channels WHERE serverid = ? AND type = ?", (str(server_id), "flash"))
        channel_info = c.fetchone()

        return channel_info
