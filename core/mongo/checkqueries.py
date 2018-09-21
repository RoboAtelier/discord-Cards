"""Checks data with MongoDB"""

def check_discord_guild(mongo, guild):
    """Checks if a discord guild is in the database

    Args:
        mongo (pymongo.MongoClient): MongoDB client connection
        guild (discord.Guild): Discord guild object

    Returns:
        A bool indicating if the guild is in the database.
    """

    check = mongo.cards.discord_guild.find(
        {'guild_id': guild.id},
        {'_id': 1}
    ).limit(1).count(True)
    if check > 0:
        return True
    return False

def check_guild_uno_session(mongo, guild, channel):

    """
    Checks if there is a running UNO session on a given channel.

    Returns True if there is a running UNO session on the given channel.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `channel` - discord channel to check
    """

    check = mongo.cards.gd_uno_session.find(
        {
            '$and': [
                {'guild_id': guild.id},
                {'channel_id': channel.id}
            ]
        },
        {'_id': 1}
    ).limit(1).count(True)
    if check > 0:
        return True
    else:
        return False

def is_main_channel(mongo, guild, channel):
    """Checks if a channel is the main listening channel of the guild

    Args:
        mongo (pymongo.MongoClient): MongoDB client connection
        guild (discord.Guild): Discord guild object
        channel (discord.Channel): Discord channel object

    Returns:
        A bool indicating if the given channel is
        the main listening channel of the guild.
    """

    check = mongo.cards.discord_guild.find(
        {
            '$and': [
                {'guild_id': guild.id},
                {'main_channel_id': channel.id}
            ],
        },
        {'_id': 1}
    ).limit(1).count(True)
    if check > 0:
        return True
    return False

def is_alt_channel(mongo, guild, channel):

    """
    Checks if a given channel is an alt channel of the guild.

    Returns True if the channel is an alt channel.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `channel` - discord channel to check
    """

    check = mongo.cards.alt_channel.find(
        {
            '$and': [
                {'guild_id': guild.id},
                {'channel_id': channel.id}
            ]
        },
        {'_id': 1}
    ).limit(1).count(True)
    if check > 0:
        return True
    else:
        return False

def is_listening_channel(mongo, guild, channel):

    """
    Checks if a given channel can listen for commands.

    Returns True if the channel can listen for command.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `channel` - discord channel to check
    """

    mcheck = is_main_channel(mongo, guild, channel)
    acheck = is_alt_channel(mongo, guild, channel)
    if mcheck or acheck:
        return True
    else:
        return False