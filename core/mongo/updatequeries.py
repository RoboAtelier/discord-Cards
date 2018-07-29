"""Update queries using MongoDB"""

def update_main_channel(mongo, server, channel):

    """
    Updates the main channel of a discord server.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - new channel to set
    """

    mongo.cards.discord_server.update_one(
        {'server_id': server.id},
        {
            '$set': {
                'main_channel_id': channel.id,
                'last_action': 'Changed Main Channel'
            },
            '$currentDate': {'date_last_modified': {'$type': 'date'}},
        }
    )

def update_channel_game(mongo, server, channel, games):

    """
    Updates the type of game(s) available for a channel.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - channel to update

    :param: `game` - game type
    """

    mongo.cards.discord_server.update_one(
        {'server_id': server.id},
        {
            '$set': {
                'prefix': prefix,
                'last_action': 'Changed Channel Game Hosting'
            },
            '$currentDate': {'date_last_modified': {'$type': 'date'}},
        }
    )