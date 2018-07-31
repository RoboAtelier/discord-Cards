import asyncio
import discord
import logging
import re
from core import token
from core.commands import config, ignore, listen, prefix
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

    __slots__ = ['userlog', 'serverlog', 'dmlog']

    def __init__(self, userlog, serverlog, dmlog):
        self.userlog = userlog
        self.serverlog = serverlog
        self.dmlog = dmlog

@bot.event
async def on_ready():
    log = ('Cards are stacked and ready!'
        + '\n\tBot name: {}#{}\n\tBot ID: {}'.format(bot.user.name, 
        bot.user.discriminator, bot.user.id))
    logwriter.write_log(log, BOT_LOG)

@bot.event
async def on_message(message):

    # Prevent echos
    if not message.author.id == bot.user.id:

        try:
            userlog = logwriter.USER_LOG_DIR + '\\{}-{}#{}.log'.format(message.author.id,
                message.author.name, message.author.discriminator)       

            msgsplit = message.content.split(' ', 1)
            cmd = msgsplit[0]
            content = ''
            if len(msgsplit) > 1:
                content = msgsplit[1].strip()

            if message.channel.is_private:
                dmlog = logwriter.DM_LOG_DIR + '{}-{}#{}.log'.format(message.author.id,
                message.author.name, message.author.discriminator)
                logstore = LogStore(userlog, '', dmlog)
                print('private time')
                #await call_command(message, cmd, content, logstore)
            else:
                serverlog = logwriter.SERVER_LOG_DIR + '{}-{}.log'.format(message.server.id,
                message.server.name)
                logstore = LogStore(userlog, serverlog, '')
                find = findqueries.find_prefix(mongo, message.server)
                if find.count(True) > 0:
                    prefix = find[0]['prefix']
                    if message.content.startswith(prefix):
                        await call_command(message, cmd[len(prefix):], content, logstore)
                    elif message.content == 'ccprefix?':
                        if checkqueries.is_listening_channel(mongo, message.server, message.channel):
                            messenger.send_timed_message(bot, 5,
                                ':bulb: | My command prefix for this server: \'**{}**\''.format(prefix), message.channel)
                        #else: 
                            #messenger.send_timed_message(bot, 5,
                                #':bulb: | My command prefix for *{}*: \'**{}**\''.format(message.server.name, prefix),
                                #message.author)
                elif message.content.startswith('cc'):
                    print('not registered')
                    await call_command(message, cmd[2:], content, logstore)

        except Exception as err:
            print('oof')
            print(err)

async def call_command(message, command, content, logstore):

    log = ('User {} attempted to call => \'{}\''.format(message.author.id, command)
        + '\n\tInput passed => \'{}\'\n '.format(content))
    logwriter.write_log(log, logstore.userlog)

    if message.channel.is_private:
        print('hi')
    else:
        if command in config.LISTEN_KEYWORDS:
            await listen.listen_command(message, bot, mongo, content, logstore)
        elif checkqueries.is_listening_channel:
            if command in config.IGNORE_KEYWORDS:
                await ignore.ignore_command(message, bot, mongo, content, logstore)
            if command in config.PREFIX_KEYWORDS:
                await prefix.prefix_command(message, bot, mongo, content, logstore)

bot.run(token.BOT_TOKEN)
