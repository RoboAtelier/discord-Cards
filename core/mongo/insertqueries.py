'''Insert queries using MongoDB'''

def insert_discord_server(mongo, server, channel):

    '''
    Inserts discord server information into the database.

    :param: `mongo` - mongo client

    :param: `server` - discord server to store

    :param: `channel` - discord channel to set as primary
    '''

    # Selected data from the discord server to store
    newdiscordserver = {
        'server_id': server.id,
        'primary_channel_id': channel.id,
        'prefix': ',',
        'last_action': 'Server Registered'
    }
    mongo.fey.discord_server.insert_one(newdiscordserver)
    mongo.fey.discord_server.update_one(
        {'server_id': server.id},
        {'$currentDate': {'date_last_modified': {'$type': 'date'}}}
    )

def insert_alt_channel(mongo, server, channel):

    '''
    Inserts a new alt channel into the database.
    Bot commands can be used on alt channels.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - discord channel to store
    '''

    # Selected data from the discord channel to store
    newaltchannel = {
        'channel_id': channel.id,
        'server_id': server.id
    }
    mongo.fey.alt_channel.insert_one(newaltchannel)
    mongo.fey.discord_server.update_one(
        {'server_id': server.id},
        {
            '$set': {'last_action': 'Added Alt Channel'},
            '$currentDate': {'date_last_modified': {'$type': 'date'}}
        }
    )