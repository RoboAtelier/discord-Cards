"""`listen` command:

Listen command module.
Allows the bot to listen for commands on a chosen channel.
Required for all servers to use first before other commands are unlocked.
"""

from . import config
from ..functions import logwriter, messenger, parameterizer, verifier
from ..mongo import checkqueries, deletequeries, insertqueries, updatequeries

async def listen_command(message, bot, mongo, content, logstore):
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

    # Check necessary permissions and guild registration.
    if verifier.is_guild_admin(message.author, message.channel):

        log = ''
        dmsg = ''
        option = ''
        params = ''
        if len(content) > 0:
            csplit = content.split(' ', 1)
            option = csplit[0]
            if len(csplit) > 1:
                params = csplit[1]

        if checkqueries.is_main_channel(mongo, message.server, message.channel):

            if 'main'.startswith(option) or option in ('-m'):
                log = 'Nothing happened.'
                dmsg = config.ERR_WARNINGS['error'] + 'This is already the main channel.'
            elif 'games'.startswith(option) or option in ('-g'):
                # Change channel games
                return await change_channel_games(message, bot, mongo, params, logstore)
            else:
                log = 'Nothing happened.'
                dmsg = config.ERR_WARNINGS['error'] + 'I\'m already listening on this channel.'
            logwriter.write_log(log, logstore.userlog)
            await messenger.send_timed_message(bot, 5, dmsg, message.channel)
            return False

        elif checkqueries.is_alt_channel(mongo, message.server, message.channel):

            if option in ('-m', 'main'):
                # Set new main channel and change old main channel to alt channel
                updatequeries.change_alt_main(mongo, message.server, message.channel)
                log = 'Set new main channel for {} (ID: {}) guild.'.format(
                    message.server.name, message.server.id
                )
                logwriter.write_log(log, logstore.userlog)
                log = 'Main channel has been changed to #{} (ID: {})'.format(
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.guildlog)
                dmsg = ':tada: This is now the main channel! Bot announcements will be posted here.'
                await bot.send_message(message.channel, dmsg)
                return True
            elif 'games'.startswith(option) or option in ('-g'):
                # Change channel games
                return await change_channel_games(message, bot, mongo, params, logstore)
            else:
                log = 'Nothing happened.'
                dmsg = ':no_entry_sign: I\'m already listening on this channel.'
            logwriter.write_log(log, logstore.userlog)
            await messenger.send_timed_message(bot, 5, dmsg, message.channel)
            return False

        elif checkqueries.check_discord_guild(mongo, message.server):

            if option in ('-m', 'main'):
                # Set new main channel and change old main channel to alt channel
                updatequeries.change_alt_main(mongo, message.server, message.channel)
                log = 'Set new main channel for {} (ID: {}) guild.'.format(
                    message.server.name, message.server.id
                )
                logwriter.write_log(log, logstore.userlog)
                log = 'Main channel has been changed to #{} (ID: {})'.format(
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.guildlog)
                dmsg = ':tada: This is now the main channel! Bot announcements will be posted here.'
                await bot.send_message(message.channel, dmsg)
                return True
            else:
                # Insert new alt channel
                insertqueries.insert_alt_channel(mongo, message.server, message.channel)
                log = 'Added new alt channel for {} (ID: {}) guild.'.format(
                    message.server.name, message.server.id
                )
                logwriter.write_log(log, logstore.userlog)
                log = '#{} (ID: {}) has been added as a new alt channel.'.format(
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.guildlog)
                dmsg = ':tada: I will now listen for commands on this channel.'
                await bot.send_message(message.channel, dmsg)
                if 'games'.startswith(option) or option in ('-g'):
                    # Change channel games
                    await change_channel_games(message, bot, mongo, params, logstore)
                return True

        else:

            # Insert new discord guild into the database
            insertqueries.insert_discord_guild(mongo, message.server, message.channel)
            log = 'Added {} (ID: {}) guild into the discord guild database.'.format(
                message.server.name, message.server.id
            )
            logwriter.write_log(log, logstore.userlog)
            log = 'Guild added into the database. #{} (ID: {}) has been set as the main channel.'.format(
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.guildlog)
            dmsg = ':tada: Main channel set! I will listen for commands and post my announcements on this channel.'
            await bot.send_message(message.channel, dmsg)
            return True

    else:
        log = 'User had insufficient permissions.'
        logwriter.write_log(log, logstore.userlog)
        await messenger.send_timed_message(
            bot, 5,
            config.ERR_WARNINGS['no_perm'],
            message.channel)
        return False

async def change_channel_games(message, bot, mongo, params, logstore):
    """(async)

    Changes the available games on a listening channel.
    
    Args:
        message (discord.Message): Discord message object
        bot (discord.Client): Discord bot client
        mongo (pymongo.MongoClient): MongoDB client connection
        params (str): String of parameters for game names
        logstore (LogStore): Object containing log file paths

    Returns:
        A bool indicating a successful process execution and changes were made
    """

    if params == '':
        log = 'Nothing happened.'
        dmsg = ':no_entry_sign: You must mention at least one game.'
        logwriter.write_log(log, logstore.userlog)
        await messenger.send_timed_message(bot, 5, dmsg, message.channel)
        return False
    else:
        games = []
        if config.UNO_KEYWORDS[0] in params:
            games.append('uno')
        if params.strip() in ('none', 'nothing'):
            games = ['none']
        if len(games) == 0:
            dmsg = ':mega: All of my games are available on this channel!'
        elif 'none' in games:
            dmsg = ':mega: No games are avaiable on this channel!'
        else:
            gnames = [g.upper() for g in games]
            dmsg = (
                ':mega: This channel now has the following games:'
                + '\n\n**' + '**\n**'.join(gnames) + '**'
            )
        if checkqueries.is_main_channel(mongo, message.server, message.channel):
            updatequeries.update_main_channel_games(
                mongo, message.server, message.channel, *games
            )
        else:
            updatequeries.update_alt_channel_games(
                mongo, message.server, message.channel, *games
            )
        log = 'Changed available games for a channel in {} (ID: {}) guild.'.format(
            message.server.name, message.server.id
        )
        logwriter.write_log(log, logstore.userlog)
        log = 'Changed available games for #{} (ID: {}) channel.'.format(
            message.channel.name, message.channel.id
        )
        logwriter.write_log(log, logstore.guildlog)
        await bot.send_message(message.channel, dmsg)
        return True