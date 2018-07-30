"""
`prefix` command:

Changes the server's prefix.
Useful for an easier or memorable prefix or if it interferes with another bot.
"""

from . import config
from ..functions import logwriter, messenger, verifier
from ..mongo import updatequeries

async def prefix_command(message, bot, mongo, content, logstore):

    """
    (async)

    `prefix` command:

    Changes the server's prefix.
    Useful for an easier or memorable prefix or if it interferes with another bot.

    Returns True on a successful prefix change.

    :param: `message` - discord message

    :param: `bot` - discord bot

    :param: `mongo` - mongodb client

    :param: `content` - contents of the message

    :param: `logstore` - class containing log paths
    """

    # Check necessary permissions
    appinfo = await bot.application_info()
    if (verifier.is_server_admin(message.author, message.channel)
        or verifier.is_bot_admin(message.author, appinfo)):

        prefix = content.lstrip()

        # Prefix must be between 1 to 3 characters
        if len(prefix) > 0 and len(prefix) <= 3:
            updatequeries.update_prefix(mongo, message.server, prefix)
            log = 'Server prefix changed to \'{}\''.format(prefix)
            logwriter.write_log(log, logstore.userlog, logstore.serverlog)
            await bot.send_message(message.channel,
                ':bulb: | My prefix for this server has been set to \'**{}**\' '.format(prefix))
            return True
        else:
            log = 'Invalid input was sent => \'{}\''.format(content)
            logwriter.write_log(log, logstore.userlog)
            messenger.send_timed_message(bot, 5,
                config.ERR_WARNINGS['invalid_in'] + ' Prefix must be **1-3 characters**.',
                message.channel)
            return False

    else:
        log = 'User has insufficient permissions.'
        logwriter.write_log(log, logstore.userlog)
        messenger.send_timed_message(bot, 3,
            config.ERR_WARNINGS['no_perm'], message.channel)
        return False