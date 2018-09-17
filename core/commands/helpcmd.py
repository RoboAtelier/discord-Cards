"""
`help` command:

Help command module.
Provides help information about commands.
"""

from discord import Embed
from . import helpinfo, config
from ..functions import logwriter, messenger, verifier
from ..mongo import checkqueries

EMBED_HELP_INFO = {
    'listen': helpinfo.LISTEN_INFO_EMBED,
    'ignore': helpinfo.IGNORE_INFO_EMBED,
    'prefix': helpinfo.PREFIX_INFO_EMBED,
    'uno': helpinfo.UNO_INFO_EMBED
}

TEXT_HELP_INFO = {
    'listen': helpinfo.LISTEN_INFO,
    'ignore': helpinfo.IGNORE_INFO,
    'prefix': helpinfo.PREFIX_INFO,
    'uno': helpinfo.UNO_INFO
}

async def help_command(message, bot, mongo, content, logstore):
    """(async)

    Help command module.
    Provides help information about commands.
    
    Args:
        message (discord.Message): Discord message object
        bot (discord.Client): Discord bot client
        mongo (pymongo.MongoClient): MongoDB client connection
        content (str): String contents of the discord message without the command name
        logstore (LogStore): Object containing log file paths

    Returns:
        A bool indicating a successful process execution
    """

    option = 'embed'
    cmd = 'cmds'
    target = 'ch'
    if ' ' in content:
        csplit = content.split(' ', 1)
        option = csplit[0]
        cmd = csplit[1].lower()
    elif len(content) > 0:
        cmd = content

    if 'simple'.startswith(option) or option in ['-s']:
        print('TODO')
    else:
        hembed = None
        if cmd in config.LISTEN_KEYWORDS:
            if verifier.is_guild_admin(message.author, message.channel):
                hembed = EMBED_HELP_INFO['listen']
        elif cmd in config.IGNORE_KEYWORDS:
            if verifier.is_guild_admin(message.author, message.channel):
                hembed = EMBED_HELP_INFO['ignore']
        elif cmd in config.PREFIX_KEYWORDS:
            if verifier.is_guild_admin(message.author, message.channel):
                hembed = EMBED_HELP_INFO['prefix']
        elif cmd in config.UNO_KEYWORDS:
            hembed = EMBED_HELP_INFO['uno']
            if not checkqueries.is_listening_channel(mongo, message.server, message.channel):
                target = 'dm'
        elif cmd == 'cmds':
            hembed = Embed(
                **{
                    'title': '__commands__',
                    'description': 'Your available commands.',
                    'colour': 0x3498db
                }
            )
            if not checkqueries.check_discord_guild(mongo, message.server):
                hembed.add_field(
                    name='Administrative',
                    value='`listen`'
                )
                await bot.send_message(message.channel, embed=hembed)
                return True
            else:
                if verifier.is_guild_admin(message.author, message.channel):
                    hembed.add_field(
                        name='Administrative',
                        value='`listen`, `ignore`, `prefix`',
                        inline=False
                    )
                hembed.add_field(
                    name='Game',
                    value='`uno`',
                    inline=False
                )
        if hembed:
            if target == 'ch':
                await bot.send_message(message.channel, embed=hembed)
            elif target == 'dm':
                await bot.send_message(message.author, embed=hembed)
            return True
        return False
        
    return True