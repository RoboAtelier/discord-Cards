"""Find/get queries using MongoDB"""

def find_main_channel(mongo, server):

    """
    Finds the main channel of a given discord server.

    Returns a cursor containing the main channel id
    or None if nothing was found.

    :param: `mongo` - mongo client

    :param: `server` - discord server to find
    """

    return mongo.cards.discord_server.find(
        {'server_id': server.id},
        {'main_channel_id': 1}
    ).limit(1)

def find_channel_games(mongo, server, channel):

    """
    Finds the list of games available on a particular channel.

    Returns a cursor containing the a list of game types available
    or None if nothing was found.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - discord channel to check
    """

    check = mongo.cards.discord_server.find(
        {
            '$and': [
                {'server_id': server.id},
                {'main_channel_id': channel.id}
            ],
        },
        {'_id': 1}
    ).limit(1).count(True)
    if check > 0:
        return mongo.cards.discord_server.find(
            {'server_id': server.id},
            {'main_channel_games': 1}
        ).limit(1)
    else:
        return mongo.cards.alt_channel.find(
            {
                '$and': [
                    {'server_id': server.id},
                    {'channel_id': channel.id}
                ],
            },
            {'channel_games': 1}
        ).limit(1)

def find_prefix(mongo, server):

    """
    Finds the command prefix of a given discord server.

    Returns a cursor containing the discord server's prefix
    or None if nothing was found.

    :param: `mongo` - mongo client

    :param: `server` - discord server to find
    """

    return mongo.cards.discord_server.find(
        {'server_id': server.id},
        {'prefix': 1}
    ).limit(1)

def find_server_uno_session(mongo, server, channel):

    """
    Finds a running UNO session on a given channel

    Returns a cursor containing a server UNO session
    or None if nothing was found.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - discord channel to check
    """

    return mongo.cards.sv_uno_session.find(
        {
            '$and': [
                {'server_id': server.id},
                {'channel_id': channel.id}
            ]
        }
    ).limit(1)