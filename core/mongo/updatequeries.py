'''Update queries using MongoDB'''

def update_primary_channel(mongo, server, channel):

    '''
    Updates the primary channel of a discord server.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - new channel to set
    '''

    mongo.fey.discord_server.update_one(
        {'server_id': server.id},
        {
            '$set': {
                'primary_channel_id': channel.id,
                'last_action': 'Changed Primary Channel'
            },
            '$currentDate': {'date_last_modified': {'$type': 'date'}},
        }
    )

def update_prefix(mongo, server, prefix):

    '''
    Updates the prefix of a discord server.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `prefix` - new prefix to set
    '''

    mongo.fey.discord_server.update_one(
        {'server_id': server.id},
        {
            '$set': {
                'prefix': prefix,
                'last_action': 'Changed Prefix'
            },
            '$currentDate': {'date_last_modified': {'$type': 'date'}},
        }
    )