"""Find/get queries using MongoDB"""

def find_main_channel(mongo, guild):
    """Finds the main channel of a given discord server.

    Args:
        mongo (pymongo.MongoClient): MongoDB client connection
        guild (discord.Guild): Discord guild object

    Returns:
        A dictionary containing the main channel id and its games
        or None if nothing was found
    """

    find = mongo.cards.discord_guild.find(
        {'guild_id': guild.id},
        {
            'main_channel_id': 1,
            'channel_games': 1
        }
    ).limit(1)
    if find.count(True) > 0:
        return find[0]
    return None

def find_channel_games(mongo, guild, channel):
    """Finds the list of games available on a particular channel.

    Args:
        mongo (pymongo.MongoClient): MongoDB client connection
        guild (discord.Guild): Discord guild object

    Returns:
        A dictionary containing the games available
        on the channel or None if nothing was found
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
        return mongo.cards.discord_guild.find(
            {'guild_id': guild.id},
            {'channel_games': 1}
        ).limit(1)
    else:
        return mongo.cards.alt_channel.find(
            {
                '$and': [
                    {'guild_id': guild.id},
                    {'channel_id': channel.id}
                ],
            },
            {'channel_games': 1}
        ).limit(1)

def find_prefix(mongo, guild):

    """
    Finds the command prefix of a given discord server.

    Returns a cursor containing the discord server's prefix
    or None if nothing was found.

    :param: `mongo` - mongo client

    :param: `guild` - discord server to find
    """

    return mongo.cards.discord_guild.find(
        {'guild_id': guild.id},
        {'prefix': 1}
    ).limit(1)

def find_guild_uno_session(mongo, guild, channel):

    """
    Finds a running UNO session on a given channel

    Returns a cursor containing a server UNO session
    or None if nothing was found.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `channel` - discord channel to check
    """

    return mongo.cards.gd_uno_session.find(
        {
            '$and': [
                {'guild_id': guild.id},
                {'channel_id': channel.id}
            ]
        },
        {'_id': 0}
    ).limit(1)

def findall_guild_uno_session(mongo, guild):

    """
    Finds all running UNO session on a given server

    Returns a cursor containing all UNO sessions on a server
    or None if nothing was found.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `channel` - discord channel to check
    """

    return mongo.cards.gd_uno_session.find(
        {'guild_id': guild.id},
        {'_id': 0}
    )