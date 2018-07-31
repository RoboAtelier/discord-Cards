"""
`ignore` command:

Tells the bot to ignore commands on the channel.
The channel being ignored must be an alt channel.
Alias for cclisten -i/ignore
"""

from . import config
from ..functions import logwriter, messenger, verifier
from ..mongo import checkqueries, deletequeries

async def ignore_command(message, bot, mongo, content, logstore):

    """
    (async)

    `ignore` command:

    Tells the bot to ignore commands on the channel.
    The channel being ignored must be an alt channel.
    Alias for cclisten -i/ignore
    
    Returns True if the process was executed successfully and changes were made.

    :param: `message` - discord message

    :param: `bot` - discord bot

    :param: `mongo` - mongo client

    :param: `content` - contents of the message

    :param: `logstore` - class containing log paths
    """

    # Check necessary permissions and server registration
    appinfo = await bot.application_info()
    if (verifier.is_server_admin(message.author, message.channel)
        or verifier.is_bot_admin(message.author, appinfo)):

        if checkqueries.is_alt_channel(mongo, message.server, message.channel):

            deletequeries.delete_alt_channel(mongo, message.server, message.channel)
            log = '#{} (ID: {}) is no longer an alt channel for this server.'.format(
                message.channel.name, message.channel.id)
            logwriter.write_log(log, logstore.userlog, logstore.serverlog)
            await bot.send_message(message.channel,
                ':no_bell: | I will no longer listen to commands here.')
            return True

        elif checkqueries.is_main_channel(mongo, message.server, message.channel):

            log = 'Nothing happened.'
            logwriter.write_log(log, logstore.userlog)
            await messenger.send_timed_message(bot, 3,
                config.ERR_WARNINGS['error'] + 'I can\'t ignore the main channel!', message.channel)
            return False

        else:
            
            log = 'Nothing happened.'
            logwriter.write_log(log, logstore.userlog)
            return False