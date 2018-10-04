"""`ignore` command:

Ignore command module.
Tells the bot to no longer listen for commands on a channel.
Alias for cclisten -i/ignore
"""

from asyncio import ensure_future
from . import config
from ..functions import logwriter, messenger, verifier
from ..mongo import checkqueries, deletequeries

async def ignore_command(message, bot, mongo, content, logstore):

    """(async)

    Listen command module.
    Allows the bot to listen for commands on a chosen channel.
    Required for all servers to use first before other commands are unlocked.
    Can be used in ANY channel, even after using it for the first time.
    
    Args:
        message (discord.Message): Discord message object
        bot (discord.Client): Discord bot client
        mongo (pymongo.MongoClient): MongoDB client connection
        content (str): String contents of the discord message without the command name
        logstore (LogStore): Object containing log file paths

    Returns:
        A bool indicating a successful process execution and changes were made
    """

    # Check necessary permissions and guild registration
    if verifier.is_guild_admin(message.author, message.channel):

        log = 'No action taken.'
        dmsg = ''
        #option = ''
        #params = ''

        if checkqueries.is_alt_channel(mongo, message.server, message.channel):

            deletequeries.delete_alt_channel(mongo, message.server, message.channel)
            log = 'Deleted an alt channel from {} (ID: {}) guild.'.format(
                message.server.name, message.server.id
            )
            logwriter.write_log(log, logstore.userlog)
            log = '#{} (ID: {}) is no longer an alt channel for this guild.'.format(
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.guildlog)
            dmsg = ':no_bell: | I will no longer listen to commands here.'
            await bot.send_message(message.channel, dmsg)
            return True

        elif checkqueries.is_main_channel(mongo, message.server, message.channel):

            dmsg = ':no_entry_sign: I can\'t ignore the main channel!'

        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(bot, 5, dmsg, message.channel)
        )
        return False