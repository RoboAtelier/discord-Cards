"""Insert queries using MongoDB"""

def insert_discord_user(mongo, user):

    """
    Inserts a new discord user into the database.

    :param: `mongo` - mongo client

    :param: `user` - discord user to add
    """

    new_discorduser = {
        'user_id': user.id,
        'chips': 1000
    }
    mongo.cards.discord_user.insert_one(new_discorduser)

def insert_discord_server(mongo, server, channel):

    """
    Inserts discord server information into the database.

    :param: `mongo` - mongo client

    :param: `server` - discord server to store

    :param: `channel` - discord channel to set as main
    """

    # Store the server id and the channel id of where the channel called on
    new_discordserver = {
        'server_id': server.id,
        'main_channel_id': channel.id,
        'channel_games': [],
        'prefix': 'cc',
        'last_change': 'Server Registered'
    }
    mongo.cards.discord_server.insert_one(new_discordserver)
    mongo.cards.discord_server.update_one(
        {'server_id': server.id},
        {'$currentDate': {'date_last_modified': {'$type': 'date'}}}
    )

def insert_alt_channel(mongo, server, channel):

    """
    Inserts a new alt channel into the database.
    Bot commands can be used on alt channels.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - discord channel to store
    """

    # Selected data from the discord channel to store
    new_altchannel = {
        'channel_id': channel.id,
        'channel_games': [],
        'server_id': server.id
    }
    mongo.cards.alt_channel.insert_one(new_altchannel)
    mongo.cards.discord_server.update_one(
        {'server_id': server.id},
        {
            '$set': {'last_change': 'Added Alt Channel'},
            '$currentDate': {'date_last_modified': {'$type': 'date'}}
        }
    )

def insert_uno_session(mongo, server, channel, username):

    """
    Inserts a new session of UNO.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - discord channel to store

    :param: `username` - discord username
    """
