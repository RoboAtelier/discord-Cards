"""Update queries using MongoDB"""

def update_main_channel(mongo, guild, channel):

    """
    Updates the main channel of a discord server.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `channel` - new channel to set
    """

    mongo.cards.discord_guild.update_one(
        {'guild_id': guild.id},
        {
            '$set': {
                'main_channel_id': channel.id,
                'last_action': 'Changed Main Channel'
            },
            '$currentDate': {'date_last_modified': {'$type': 'date'}},
        }
    )

def update_prefix(mongo, guild, prefix):

    """
    Updates the prefix of a discord server.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `prefix` - new prefix to set
    """

    mongo.cards.discord_guild.update_one(
        {'guild_id': guild.id},
        {
            '$set': {
                'prefix': prefix,
                'last_action': 'Changed Prefix'
            },
            '$currentDate': {'date_last_modified': {'$type': 'date'}},
        }
    )

def update_channel_game(mongo, guild, channel, games):

    """
    Updates the type of game(s) available for a channel.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `channel` - channel to update

    :param: `game` - game type
    """

    mongo.cards.discord_guild.update_one(
        {'guild_id': guild.id},
        {
            '$set': {
                'channel_games': games,
                'last_action': 'Changed Channel Game Hosting'
            },
            '$currentDate': {'date_last_modified': {'$type': 'date'}},
        }
    )

def update_guild_uno_session(mongo, guild, channel, session):

    """
    Updates the progress of a server UNO game session.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `channel` - discord channel

    :param: `session` - running UNO session
    """

    mongo.cards.gd_uno_session.update_one(
        {   
            '$and': [
                {'guild_id': guild.id},
                {'channel_id': channel.id}
            ]
        },
        {'$set': session}
    )