"""
`listen` command:

Allows the bot to listen for commands on the channel.
Required for all servers to use first to allow bot usage.
"""

import re
from . import config
from ..functions import logwriter, messenger, verifier, listscanner, parameterizer
from ..mongo import checkqueries, deletequeries, insertqueries, updatequeries

async def listen_command(message, bot, mongo, content, logstore):

    """
    (async)

    `register` command:

    Adds server into the database to authorize usage of bot commands.
    Required by all servers that add the bot in.
    Can be used in ANY channel, even after using it to register for the first time.
    
    Returns True if the process was executed successfully and changes were made.

    :param: `message` - discord message

    :param: `bot` - discord bot

    :param: `mongo` - mongo client

    :param: `content` - contents of the message

    :param: `logstore` - class containing log paths

    :param: `option` - specifies command behavior.
    Must be used with a '-' symbol followed by the appropriate letter(s).
    Options are mutually exclusive.

    :option: `-a` => adds a new alt channel

    :option: `-d` => deletes an alt channel
    """

    # Check necessary permissions and server registration
    appinfo = await bot.application_info()
    if (verifier.is_server_admin(message.author, message.channel)
        or verifier.is_bot_admin(message.author, appinfo)):

        if checkqueries.check_discord_server(mongo, message.server):

            option = ''
            params = ''
            if len(content) > 0:
                contsplit = content.split(' ', 1)
                option = contsplit[0]
                if len(contsplit) > 1:
                    params = contsplit[1]

            # Options include: 
            # Adding and deleting alt channels
            # Changing the primary channel

            if len(option) > 0:

                if option == '-a':

                    # Add alt channel(s) with given parameters
                    if len(params) > 0:

                        # Control variables
                        channelparams = parameterizer.parameterize(params)
                        firstiter = True
                        totalchange = 0
                        discordmsg = ''

                        for channelparam in channelparams:

                            # Find a valid channel
                            channel = listscanner.find_channel_by_name(message.server.channels, channelparam.lower())
                            if channel and (not channel == 'ambig'):

                                # Database checking
                                altchannel = checkqueries.is_alt_channel(mongo, message.server, channel)
                                primchannel = checkqueries.is_primary_channel(mongo, message.server, channel)

                                # Add alt channel if it's not the primary channel and is not already an alt
                                if (not altchannel) and (not primchannel):
                                    insertqueries.insert_alt_channel(mongo, message.server, channel)
                                    log = ('Server {} added an alt channel: {}'.format(message.server.id, channel.id))
                                    logwriter.write_log(log, logstore.userlog, logstore.serverlog)
                                    if firstiter:
                                        discordmsg += ':sparkles: | Alt channel added: <#{}>'.format(channel.id)
                                        firstiter = False
                                    else:
                                        discordmsg += '\n:sparkles: | Alt channel added: <#{}>'.format(channel.id)
                                    totalchange += 1
                                else:
                                    if altchannel:
                                        if firstiter:
                                            discordmsg += '{} Already an alt channel: <#{}>'.format(
                                                errorwarn.error_warnings['generic_err'], channel.id)
                                            firstiter = False
                                        else:
                                            discordmsg += '\n{} Already an alt channel: <#{}>'.format(
                                                errorwarn.error_warnings['generic_err'], channel.id)
                                    else:
                                        if firstiter:
                                            discordmsg += '{} Can\'t set primary channel as alt: <#{}>'.format(
                                                errorwarn.error_warnings['generic_err'], channel.id)
                                            firstiter = False
                                        else:
                                            discordmsg += '\n{} Can\'t set primary channel as alt: <#{}>'.format(
                                                errorwarn.error_warnings['generic_err'], channel.id)

                            else:
                                if channel == 'ambig':
                                    if firstiter:
                                        discordmsg += '{} Two or more channels start with \'**{}**\''.format(
                                            errorwarn.error_warnings['ambig'], channelparam)
                                        firstiter = False
                                    else:
                                        discordmsg += '\n{} Two or more channels start with \'**{}**\''.format(
                                            errorwarn.error_warnings['ambig'], channelparam)
                                else:
                                    if firstiter:
                                        discordmsg += '{} Cannot find a channel with given input: \'**{}**\''.format(
                                            errorwarn.error_warnings['generic_exc'], channelparam)
                                        firstiter = False
                                    else:
                                        discordmsg += '\n{} Cannot find a channel with given input: \'**{}**\''.format(
                                            errorwarn.error_warnings['generic_exc'], channelparam)
                        
                        # Send results to discord
                        if totalchange > 0:
                            if totalchange > 1:
                                discordmsg += '\n:bulb: | {} channels have been added!'.format(totalchange)
                            else:
                                discordmsg += '\n:bulb: | 1 channel has been added!'
                            await bot.send_message(message.channel, discordmsg)
                            return True
                        else:
                            discordmsg += '\n:exclamation: | No changes were made.'
                            await bot.send_message(message.channel, discordmsg)
                            return False

                    else:

                        # Add current channel as alt channel

                        # Database checking
                        altchannel = checkqueries.is_alt_channel(mongo, message.server, message.channel)
                        primchannel = checkqueries.is_primary_channel(mongo, message.server, message.channel)

                        # Add alt channel if it's not the primary channel and is not already an alt
                        if (not altchannel) and (not primchannel):
                            insertqueries.insert_alt_channel(mongo, message.server, message.channel)
                            log = ('Server {} added an alt channel: {}'.format(message.server.id, message.channel.id))
                            logwriter.write_log(log, logstore.userlog, logstore.serverlog)
                            await bot.send_message(message.channel,
                                ':bulb: | Alt channel added! Commands can now be used here.')
                            return True
                        else:
                            log = ('No changes were made.')
                            logwriter.write_log(log, logstore.userlog)
                            if altchannel:
                                await messenger.send_timed_message(bot, 5, 
                                    errorwarn.error_warnings['action_deny'] + ' This is already an alt channel!',
                                    message.channel)
                            else:
                                await messenger.send_timed_message(bot, 5, 
                                    errorwarn.error_warnings['action_deny'] + ' Can\'t set primary channel as alt!',
                                    message.channel)
                            return False

                elif option == '-d':

                    # Delete alt channel(s) with given parameters
                    if len(params) > 0:

                        # Control variables
                        channelparams = parameterizer.parameterize(params)
                        firstiter = True
                        totalchange = 0
                        discordmsg = ''

                        for channelparam in channelparams:

                            # Find a valid channel
                            channel = listscanner.find_channel_by_name(message.server.channels, channelparam.lower())
                            if channel and (not channel == 'ambig'):

                                # Deletes alt channel from database if it's an alt channel
                                if checkqueries.is_alt_channel(mongo, message.server, channel):
                                    deletequeries.delete_alt_channel(mongo, message.server, channel)
                                    log = ('Server {} deleted an alt channel: {}'.format(message.server.id, channel.id))
                                    logwriter.write_log(log, logstore.userlog, logstore.serverlog)
                                    if firstiter:
                                        discordmsg += ':wastebasket: | Alt channel deleted: <#{}>'.format(channel.id)
                                        firstiter = False
                                    else:
                                        discordmsg += '\n:wastebasket: | Alt channel deleted: <#{}>'.format(channel.id)
                                    totalchange += 1
                                else:
                                    if firstiter:
                                        discordmsg += '{} Not an alt channel: <#{}>'.format(
                                            errorwarn.error_warnings['generic_err'], channel.id)
                                        firstiter = False
                                    else:
                                        discordmsg += '\n{} Not an alt channel: <#{}>'.format(
                                            errorwarn.error_warnings['generic_err'], channel.id)

                            else:
                                if channel == 'ambig':
                                    if firstiter:
                                        discordmsg += '{} Two or more channels start with \'**{}**\''.format(
                                            errorwarn.error_warnings['ambig'], channelparam)
                                        firstiter = False
                                    else:
                                        discordmsg += '\n{} Two or more channels start with \'**{}**\''.format(
                                            errorwarn.error_warnings['ambig'], channelparam)
                                else:
                                    if firstiter:
                                        discordmsg += '{} Cannot find a channel with given input: \'**{}**\''.format(
                                            errorwarn.error_warnings['generic_exc'], channelparam)
                                        firstiter = False
                                    else:
                                        discordmsg += '\n{} Cannot find a channel with given input: \'**{}**\''.format(
                                            errorwarn.error_warnings['generic_exc'], channelparam)

                        # Send results to discord
                        if totalchange > 0:
                            if totalchange > 1:
                                discordmsg += '\n:bulb: | {} channels have been deleted!'.format(totalchange)
                            else:
                                discordmsg += '\n:bulb: | 1 channel has been deleted!'
                            await bot.send_message(message.channel, discordmsg)
                            return True
                        else:
                            discordmsg += '\n:exclamation: | No changes were made.'
                            await bot.send_message(message.channel, discordmsg)
                            return False

                    else:

                        # Attempt to delete current channel from alt channel table
                        # Current channel must be an alt channel
                        if checkqueries.is_alt_channel(mongo, message.server, message.channel):
                            deletequeries.delete_alt_channel(mongo, message.server, message.channel)
                            log = ('Server {} deleted an alt channel: {}'.format(message.server.id, message.channel.id))
                            logwriter.write_log(log, logstore.userlog, logstore.serverlog)
                            await bot.send_message(message.channel,
                                ':bulb: | Alt channel deleted. Commands can no longer be used here.')
                            return True
                        else:
                            log = ('No changes were made.')
                            logwriter.write_log(log, logstore.userlog)
                            await messenger.send_timed_message(bot, 5, 
                                errorwarn.error_warnings['action_deny'] + ' This is not an alt channel!',
                                message.channel)
                            return False
                else:
                    log = ('Invalid input was sent => {}'.format(content)
                        + '\n{} is not an available option'.format(option))
                    logwriter.write_log(log, logstore.userlog)
                    await messenger.send_timed_message(bot, 5,
                        errorwarn.error_warnings['invalid_input'] + ' \'**{}**\' is not an available option.'.format(option),
                        message.channel)
                    return False

            # If no options are given, the primary channel can be changed
            # Command must be called on a channel that is not the primary channel

            else:

                if not checkqueries.is_primary_channel(mongo, message.server, message.channel):
                    if checkqueries.is_alt_channel(mongo, message.server, message.channel):
                        deletequeries.delete_alt_channel(mongo, message.server, message.channel)
                    updatequeries.update_primary_channel(mongo, message.server, message.channel)
                    log = ('Primary channel for server {} has been changed to channel {}'.format(
                        message.server.id, message.channel.id))
                    logwriter.write_log(log, logstore.userlog, logstore.serverlog)
                    await bot.send_message(message.channel,
                        ':bulb: | Primary channel set: <#{}>'.format(message.channel.id))
                    return True
                else:
                    log = ('No changes were made.')
                    logwriter.write_log(log, logstore.userlog)
                    await messenger.send_timed_message(bot, 5, 
                        ':bulb: | No changes were made.', message.channel)
                    return False

        else:

            # Insert new discord server into the database
            insertqueries.insert_discord_server(mongo, message.server, message.channel)
            log = ('Server {} is now registered into the server database.'.format(message.server.id))
            logwriter.write_log(log, logstore.userlog, logstore.serverlog)
            await bot.send_message(message.channel,
                ':tada: | Server successfully registered! I can now listen on this channel.')
            return True

    else:
        log = ('User had insufficient permissions.')
        logwriter.write_log(log, logstore.userlog)
        await messenger.send_timed_message(bot, 3,
            config.ERR_WARNINGS['no_perm'], message.channel)
        return False