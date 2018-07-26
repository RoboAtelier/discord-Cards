"""Send messages that are removed after a certain period of time."""

from discord import DiscordException
from asyncio import sleep
from . import logwriter

async def send_timed_message(bot, time, message, *targets):

    """
    (async)

    Sends a single timed message to target channel(s).

    Returns True if successful.

    :param `bot`: - bot that will send the message

    :param `time`: - time (in seconds) that the message will last

    :param `message`: - message string

    :param `targets`: - target channel(s) to send to
    """

    # Container that will store sent messages to delete later
    msgs = []

    try:
        for channel in targets:
            msg = await bot.send_message(channel, message)
            msgs.append(msg)
        await sleep(time)
        for msg in msgs:
            await bot.delete_message(msg)
        return True
    except DiscordException as err:
        log = ('Error occurred: There was an issue processing a message.'
            + '\nMessage: {} Channel: {}'.format(message, channel.id)
            + '\nServer: {}'.format(channel.server.id)
            + '\n{}'.format(err))
        logwriter.write_log(log, logwriter.ERR_LOG_DIR + '\\messenger.err')
        return False

async def send_timed_interval_message(bot, time, messages, interval=1, *targets):

    """
    (async)
    
    Sends multiple timed message strings in intervals to target channel(s).

    Returns True if successful.

    :param `bot`: - bot that will send the message

    :param `time`: - time (in seconds) that the entire message will last

    :param `messages`: - message strings compiled in a list.

    Example: ['hello', 'world!']

    :param `interval`: - time (in seconds) to wait before adding the next message

    :param `targets`: - target channel(s) to send to
    """

    # Container that will store sent messages to delete later
    msgs = []

    # Must only accept lists, not strings
    if isinstance(messages, str):
        log = ('Error occurred: Invalid message input was passed.'
            + '\nInput: {}'.format(str(messages)))
        logwriter.write_log(log, logwriter.ERR_LOG_DIR + '\\messenger.log')
        return False
    else:
        try:
            for channel in targets:
                msg = await bot.send_message(channel, messages[0])
                msgs.append(msg)

            if len(messages) > 1:
                for i in range(1, len(messages)):
                    newmsg = msgs[0].content + '\n{}'.format(messages[i])
                    for j in range (len(msgs)):
                        await sleep(interval)
                        msgs[j] = await bot.edit_message(msgs[j], newmsg)

            await sleep(time)

            for msg in msgs:
                await bot.delete_message(msg)
            return True
        except DiscordException as err:
            log = ('Error occurred: There was an issue processing a message.'
                + '\nMessages: {} Channel: #{}'.format(str(messages), channel.id)
                + '\nServer: {}'.format(channel.server.id)
                + '\n{}'.format(err))
            logwriter.write_log(log, logwriter.ERR_LOG_DIR + '\\messenger.err')
            return False
    
