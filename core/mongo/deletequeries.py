'''Delete queries using MongoDB'''

def delete_alt_channel(mongo, guild, channel):

    '''
    Deletes an alt channel from the database.

    :param: `mongo` - mongo client

    :param: `guild` - discord server

    :param: `channel` - discord channel to remove
    '''

    mongo.cards.alt_channel.delete_one({
        '$and': [
            {'guild_id': guild.id},
            {'channel_id': channel.id}
        ]
    })
    mongo.cards.discord_guild.update_one({'guild_id': guild.id},
        {
            '$set': {'last_action': 'Deleted Alt Channel'},
            '$currentDate': {'date_last_modified': {'$type': 'date'}}
        }
    )