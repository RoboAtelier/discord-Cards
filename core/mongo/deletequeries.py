"""Delete queries using MongoDB"""

def delete_alt_channel(mongo, guild, channel):
    """Deletes an alt channel from the database

    Args:
        mongo (pymongo.MongoClient): MongoDB client connection
        guild (discord.Guild): Discord guild object
        channel (discord.Channel): Discord channel object related to guild
    """

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