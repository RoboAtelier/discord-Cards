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

def insert_discord_guild(mongo, guild, channel):

    """
    Inserts discord guild information into the database.

    :param: `mongo` - mongo client

    :param: `guild` - discord server to store

    :param: `channel` - discord channel to set as main
    """

    # Store the guild id and the channel id of where the channel called on
    new_discordguild = {
        'guild_id': guild.id,
        'main_channel_id': channel.id,
        'channel_games': [],
        'prefix': 'cc',
        'last_change': 'Server Registered'
    }
    mongo.cards.discord_guild.insert_one(new_discordguild)
    mongo.cards.discord_guild.update_one(
        {'guild_id': guild.id},
        {'$currentDate': {'date_last_modified': {'$type': 'date'}}}
    )

def insert_alt_channel(mongo, guild, channel):

    """
    Inserts a new alt channel into the database.
    Bot commands can be used on alt channels.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `channel` - discord channel to store
    """

    # Selected data from the discord channel to store
    new_altchannel = {
        'channel_id': channel.id,
        'channel_games': [],
        'guild_id': guild.id
    }
    mongo.cards.alt_channel.insert_one(new_altchannel)
    mongo.cards.discord_guild.update_one(
        {'guild_id': guild.id},
        {
            '$set': {'last_change': 'Added Alt Channel'},
            '$currentDate': {'date_last_modified': {'$type': 'date'}}
        }
    )

def insert_guild_uno_session(mongo, session):

    """
    Inserts a new guild session of UNO on an open channel.

    :param: `mongo` - mongo client

    :param: `session` - uno session dict
    """

    mongo.cards.gd_uno_session.insert_one(session)