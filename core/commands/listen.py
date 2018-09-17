"""
`listen` command:

Allows the bot to listen for commands on the channel.
Required for all servers to use first to allow bot usage.
"""

from . import config
from ..functions import logwriter, messenger, verifier
from ..mongo import checkqueries, deletequeries, insertqueries, updatequeries

async def listen_command(message, bot, mongo, content, logstore):

    """
    (async)

    `listen` command:

    Allows the bot to listen for commands on the channel.
    Required for all servers to use first to allow bot usage.
    Can be used in ANY channel, even after using it for the first time.
    
    Returns True if the process was executed successfully and changes were made.

    :param: `message` - discord message

    :param: `bot` - discord bot

    :param: `mongo` - mongo client

    :param: `content` - contents of the message

    :param: `logstore` - class containing log paths
    """

    # Check necessary permissions and guild registration
    appinfo = await bot.application_info()
    if (verifier.is_guild_admin(message.author, message.channel)
        or verifier.is_bot_admin(message.author, appinfo)):

        option = ''
        #params = ''
        if len(content) > 0:
            contsplit = content.split(' ', 1)
            option = contsplit[0]
            #if len(contsplit) > 1:
                #params = contsplit[1]

        if checkqueries.is_main_channel(mongo, message.server, message.channel):

            if option in ('-m', 'main'):
                log = 'Nothing happened.'
                logwriter.write_log(log, logstore.userlog)
                await messenger.send_timed_message(
                    bot, 5,
                    config.ERR_WARNINGS['error'] + 'This is already the main channel.',
                    message.channel)
                return False
            else:
                log = 'Nothing happened.'
                logwriter.write_log(log, logstore.userlog)
                await messenger.send_timed_message(
                    bot, 5,
                    config.ERR_WARNINGS['error'] + 'I\'m already listening on this channel.',
                    message.channel)
                return False

        elif checkqueries.is_alt_channel(mongo, message.server, message.channel):

            # Set alt channel as the new main channel
            if option in ('-m', 'main'):
                updatequeries.update_main_channel(mongo, message.server, message.channel)
                deletequeries.delete_alt_channel(mongo, message.server, message.channel)
                log = '#{} (ID: {}) is now set as the main channel of the server.'.format(
                    message.channel.name, message.channel.id)
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                await bot.send_message(
                    message.channel,
                    ':tada: | {} is now the main channel! Bot announcements will be posted here.'.format(
                        message.mention))
                return True
            else:
                log = 'Nothing happened.'
                logwriter.write_log(log, logstore.userlog)
                await messenger.send_timed_message(
                    bot, 5,
                    config.ERR_WARNINGS['error'] + 'I\'m already listening on this channel.',
                    message.channel)
                return False

        elif checkqueries.check_discord_guild(mongo, message.server):

            # Insert new alt channel into the database
            insertqueries.insert_alt_channel(mongo, message.server, message.channel)
            log = '#{} (ID: {}) has been added as a new alt channel for the server.'.format(
                message.channel.name, message.channel.id)
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            await bot.send_message(
                message.channel,
                ':tada: | I will now listen for commands on this channel.')
            return True

        else:

            # Insert new discord guild into the database
            insertqueries.insert_discord_guild(mongo, message.server, message.channel)
            log = 'Server is now registered into the database.'
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            await bot.send_message(
                message.channel,
                ':tada: | Main channel set! I will listen for commands and post my announcements on this channel.')
            return True

    else:
        log = 'User had insufficient permissions.'
        logwriter.write_log(log, logstore.userlog)
        await messenger.send_timed_message(
            bot, 5,
            config.ERR_WARNINGS['no_perm'],
            message.channel)
        return False