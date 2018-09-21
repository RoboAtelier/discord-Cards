"""Update queries using MongoDB"""

def change_alt_main(mongo, guild, channel):
    """Changes an alt channel to be the main listening channel
    and vice versa.

    Args:
        mongo (pymongo.MongoClient): MongoDB client connection
        guild (discord.Guild): Discord guild object
        channel (discord.Channel): Discord channel object related to guild
    """
    newmain = {
        'main_channel_id': channel.id,
        'last_action': 'Changed Main Channel'
    }
    newalt = {'guild_id': guild.id}
    oldmain = mongo.cards.discord_guild.find(
        {'guild_id': guild.id},
        {
            'main_channel_id': 1,
            'channel_games': 1
        }
    ).limit(1)[0]
    newalt['channel_id'] = oldmain['main_channel_id']
    newalt['channel_games'] = oldmain['channel_games']
    oldalt = mongo.cards.alt_channel.find(
        {
            '$and': [
                {'guild_id': guild.id},
                {'channel_id': channel.id}
            ]
        },
        {
            'channel_id': 1,
            'channel_games': 1
        }
    ).limit(1)
    if oldalt.count(True) > 0:
        newmain['channel_games'] = oldalt[0]['channel_games']
        mongo.cards.alt_channel.delete_one(
            {
                '$and': [
                    {'guild_id': guild.id},
                    {'channel_id': channel.id}
                ]
            }
        )
    mongo.cards.discord_guild.update_one(
        {'guild_id': guild.id},
        {
            '$set': newmain,
            '$currentDate': {'date_last_modified': {'$type': 'date'}}
        }
    )
    mongo.cards.alt_channel.insert_one(newalt)

def update_main_channel(mongo, guild, channel):
    """Updates a channel to be the main listening channel in the guild

    Args:
        mongo (pymongo.MongoClient): MongoDB client connection
        guild (discord.Guild): Discord guild object
        channel (discord.Channel): Discord channel object related to guild
    """

    mongo.cards.discord_guild.update_one(
        {'guild_id': guild.id},
        {
            '$set': {
                'main_channel_id': channel.id,
                'last_action': 'Changed Main Channel'
            },
            '$currentDate': {'date_last_modified': {'$type': 'date'}}
        }
    )

def update_prefix(mongo, guild, prefix):
    """Updates a channel to be the main listening channel in the guild

    Args:
        mongo (pymongo.MongoClient): MongoDB client connection
        guild (discord.Guild): Discord guild object
        prefix (str): Prefix string to set
    """

    mongo.cards.discord_guild.update_one(
        {'guild_id': guild.id},
        {
            '$set': {
                'prefix': prefix,
                'last_action': 'Changed Prefix'
            },
            '$currentDate': {'date_last_modified': {'$type': 'date'}}
        }
    )

def update_main_channel_games(mongo, guild, channel, *games):
    """Updates the games available for the main channel.

    Args:
        mongo (pymongo.MongoClient): MongoDB client connection
        guild (discord.Guild): Discord guild object
        channel (discord.Channel): Discord channel object related to guild
        *games (list): List of game name strings
    """

    mongo.cards.discord_guild.update_one(
        {'guild_id': guild.id},
        {
            '$set': {
                'channel_games': games,
                'last_action': 'Changed Main Channel Games'
            },
            '$currentDate': {'date_last_modified': {'$type': 'date'}}
        }
    )

def update_alt_channel_games(mongo, guild, channel, *games):
    """Updates the games available for an alt channel.

    Args:
        mongo (pymongo.MongoClient): MongoDB client connection
        guild (discord.Guild): Discord guild object
        channel (discord.Channel): Discord channel object related to guild
        *games (list): List of game name strings
    """

    mongo.cards.alt_channel.update_one(
        {'guild_id': guild.id},
        {'$set': {'channel_games': games}}
    )
    mongo.cards.discord_guild.update_one(
        {'guild_id': guild.id},
        {
            '$set': {'last_action': 'Changed Alt Channel Games'},
            '$currentDate': {'date_last_modified': {'$type': 'date'}}
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