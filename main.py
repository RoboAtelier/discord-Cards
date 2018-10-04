import asyncio
import discord
import logging
import re
from core import token
from core.commands import config, ignore, helpcmd, listen, prefix, uno
from core.functions import logwriter, messenger
from core.mongo import credentials, checkqueries, findqueries
from pymongo import MongoClient, errors
from os import path

# Log discord events while bot is running.
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discordverbose.log', mode='a', encoding='utf-8')
handler.setFormatter(logging.Formatter(fmt='%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Mongo database connection
mongo = MongoClient(credentials.HOST, 
    port=credentials.PORT,  
    username=credentials.USERNAME,
    password=credentials.PASSWORD,
    authSource=credentials.AUTH_SRC
)

# Create new bot object.
bot = discord.Client()

BOT_LOG = logwriter.LOG_DIR + '\\cards.log'
DISCORD_ERR_LOG = logwriter.ERR_LOG_DIR + '\\discord.err'
MONGO_ERR_LOG = logwriter.ERR_LOG_DIR + '\\mongo.err'

class LogStore:

    __slots__ = ['userlog', 'guildlog', 'dmlog']

    def __init__(self, userlog, guildlog, dmlog):
        self.userlog = userlog
        self.guildlog = guildlog
        self.dmlog = dmlog

@bot.event
async def on_ready():
    status = discord.Game(
        name='a dangerous game.'
    )
    await bot.change_presence(game=status)
    log = 'Cards are stacked and ready!'
    logwriter.write_log(log, BOT_LOG)

@bot.event
async def on_message(message):

    # Prevent echos
    if not message.author.id == bot.user.id:

        try:
            userlog = logwriter.USER_LOG_DIR + '\\{}-{}#{}.log'.format(message.author.id,
                message.author.name, message.author.discriminator)       
            msgsplit = message.content.split(' ', 1)
            cmd = msgsplit[0].lower()
            content = ''
            if len(msgsplit) > 1:
                content = msgsplit[1].strip()

            if message.channel.is_private:
                dmlog = logwriter.DM_LOG_DIR + '\\{}-{}#{}.log'.format(message.author.id,
                message.author.name, message.author.discriminator)
                logstore = LogStore(userlog, '', dmlog)
                print('private time')
                #await call_command(message, cmd, content, logstore)
            else:
                guildlog = logwriter.GUILD_LOG_DIR + '\\{}-{}.log'.format(message.server.id,
                message.server.name)
                logstore = LogStore(userlog, guildlog, '')
                find = findqueries.find_prefix(mongo, message.server)
                if find.count(True) > 0:
                    prefix = find[0]['prefix']
                    if message.content.startswith(prefix):
                        await call_command(message, cmd[len(prefix):], mongo, content, logstore)
                    elif message.content == 'ccprefix?':
                        if checkqueries.is_listening_channel(mongo, message.server, message.channel):
                            await messenger.send_timed_message(
                                bot, 5,
                                ':bulb: | My command prefix for this server: \'**{}**\''.format(prefix),
                                message.channel)
                        #else: 
                            #messenger.send_timed_message(bot, 5,
                                #':bulb: | My command prefix for *{}*: \'**{}**\''.format(message.server.name, prefix),
                                #message.author)
                elif message.content.startswith('cc'):
                    print('not registered')
                    await call_command(message, cmd[2:], mongo, content, logstore)

        except Exception as err:
            print('oof')
            print(err)

async def call_command(message, command, mongo, content, logstore):

    log = ('User {} (ID: {}) attempted to call => \'{}\''.format(message.author.name, message.author.id, command)
        + '\n\tInput passed => \'{}\''.format(content))
    logwriter.write_log(log, logstore.userlog)

    if message.channel.is_private:
        print('hi')
    else:
        if command in config.LISTEN_KEYWORDS:
            await listen.listen_command(message, bot, mongo, content, logstore)
        elif command in config.HELP_KEYWORDS:
            await helpcmd.help_command(message, bot, mongo, content, logstore)
        elif checkqueries.is_listening_channel(mongo, message.server, message.channel):
            if command in config.IGNORE_KEYWORDS:
                await ignore.ignore_command(message, bot, mongo, content, logstore)
            elif command in config.PREFIX_KEYWORDS:
                await prefix.prefix_command(message, bot, mongo, content, logstore)
            elif command in config.UNO_KEYWORDS:
                if '!' in command:
                    await uno.uno_command(message, bot, mongo, '! ' + content, logstore)
                else:
                    await uno.uno_command(message, bot, mongo, content, logstore)

bot.run(token.BOT_TOKEN)