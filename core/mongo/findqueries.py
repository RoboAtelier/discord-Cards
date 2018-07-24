'''Find/get queries using MongoDB'''

def find_primary_channel(mongo, server):

    '''
    Finds the primary channel of a given discord server.

    Returns a cursor containing the primary channel id
    or None if nothing was found.

    :param: `mongo` - mongo client

    :param: `server` - discord server to find
    '''

    return mongo.fey.discord_server.find(
        {'server_id': server.id},
        {'primary_channel_id': 1}
    ).limit(1)

def find_prefix(mongo, server):

    '''
    Finds the command prefix of a given discord server.

    Returns a cursor containing the discord server's prefix
    or None if nothing was found.

    :param: `mongo` - mongo client

    :param: `server` - discord server to find
    '''

    return mongo.fey.discord_server.find(
        {'server_id': server.id},
        {'prefix': 1}
    ).limit(1)