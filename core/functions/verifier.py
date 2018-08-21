from .. import admins
from ..mongo import checkqueries

def is_guild_admin(member, channel):

    """
    Checks if the server member possesses the minimum permissions
    to add or change bots in the server (e.g. Manage Servers+).
    Returns true if member has required permissions.

    :param: `member` - user in the discord server

    :param: `channel` - discord channel to check user permissions in

    :param: `appinfo` - information about the bot
    """

    perms = channel.permissions_for(member)
    
    if (member.id == channel.server.owner.id
        or perms.administrator or perms.manage_server):
        return True
    else:
        return False

def is_bot_admin(member, appinfo):

    """
    Checks if the server member is the owner of the bot
    or is a verified administrator for it.
    Returns true if member is a bot administrator.

    :param: `member` - user in the discord server

    :param: `appinfo` - information about the bot
    """

    if (member.id == appinfo.owner.id
        or member.id in admins.ADMIN_LIST):
        return True
    else:
        return False

def verify_channel(db, guild, channel):
    
    """
    Checks if the channel is allowed to listen to commands.
    Returns true if the channel is either a primary or alt channel.

    :param: `db` - mongo database

    :param: `guild` - discord server

    :param: `channel` - discord channel to verify
    """
    
    if (checkqueries.check_primary_channel(db, guild, channel) or
        checkqueries.check_alt_channel(db, guild, channel)):
        return True
    else:
        return False

def check_bot_perms(channel):
    print("TODO")
