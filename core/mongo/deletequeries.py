'''Delete queries using MongoDB'''

def delete_alt_channel(mongo, server, channel):

    '''
    Deletes an alt channel from the database.

    :param: `mongo` - mongo client

    :param: `server` - discord server

    :param: `channel` - discord channel to remove
    '''

    mongo.fey.alt_channel.delete_one({
        '$and': [
            {'server_id': server.id},
            {'channel_id': channel.id}
        ]
    })
    mongo.fey.discord_server.update_one({'server_id': server.id},
        {
            '$set': {'last_action': 'Deleted Alt Channel'},
            '$currentDate': {'date_last_modified': {'$type': 'date'}}
        }
    )