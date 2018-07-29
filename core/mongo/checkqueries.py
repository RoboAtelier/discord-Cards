"""Checks data with MongoDB"""

def check_discord_server(mongo, server):

    """
    Checks if a discord server is in the database.

    Returns True if the server is found.

    :param: `mongo` - mongo client

    :param: `server` - discord server to check
    """
    check = mongo.cards.discord_server.find(
        {'server_id': server.id},
        {'_id': 1}
    ).limit(1).count(True)
    if check > 0:
        return True
    else:
        return False

def is_main_channel(mongo, server, channel):

    """
    Checks if a given channel is the main channel of the server.

    Returns True if the channel is the main channel.

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
        return True
    else:
        return False

def is_alt_channel(mongo, server, channel):

    """
    Checks if a given channel is an alt channel of the server.

    Returns True if the channel is an alt channel.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - discord channel to check
    """

    check = mongo.cards.alt_channel.find(
        {
            '$and': [
                {'server_id': server.id},
                {'channel_id': channel.id}
            ]
        },
        {'_id': 1}
    ).limit(1).count(True)
    if check > 0:
        return True
    else:
        return False

def is_listening_channel(mongo, server, channel):

    """
    Checks if a given channel can listen for commands.

    Returns True if the channel can listen for command.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - discord channel to check
    """

    mcheck = is_main_channel(mongo, server, channel)
    acheck = is_alt_channel(mongo, server, channel)
    if mcheck or acheck:
        return True
    else:
        return False