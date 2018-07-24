import asyncio
import discord
import logging
import re
from token import BOT_TOKEN
#from core.commands import cmdconfig, practice, prefix, register
#from core.functions import logwriter, messenger
#from core.mongo import credentials, checkqueries, findqueries
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
    authSource=credentials.AUTHSRC
)

# Create new bot object.
BOT = discord.Client()

"""
logdir = '{}\\{}'.format(path.dirname(__file__), 'logs')
errlogdir = logdir + '\\error'
botlog = logdir + '\\feybot.log'
discorderrlog = errlogdir + '\\discorderror.log'
mongoerrlog = errlogdir + '\\mongoerror.log'

class LogStore:

    def __init__(self):
        self.mainlogdir = logdir
        self.userlog = None
        self.serverlog = None
        self.pmlog = None

    def set_user_log(self, userlog):
        self.userlog = '{}\\user\\{}'.format(self.mainlogdir, userlog)

    def set_server_log(self, serverlog):
        self.serverlog = '{}\\server\\{}'.format(self.mainlogdir, serverlog)

    def set_pm_log(self, pmlog):
        self.pmlog = '{}\\pm\\{}'.format(self.mainlogdir, pmlog)

@bot.event
async def on_ready():
    log = ('Cards are stacked and ready!'
        + '\n\tBot name: {}#{}\n\tBot ID: {}\n'.format(bot.user.name, bot.user.discriminator, bot.user.id))
    logwriter.write_log(log, botlog)

@bot.event
async def on_message(message):

    # Prevent echos
    if not message.author.id == bot.user.id:

        try:
            logstore = LogStore()
            logstore.set_user_log('{}-{}#{}.log'.format(message.author.id,
                message.author.name, message.author.discriminator))
            if message.channel.is_private:
                logstore.set_pm_log('{}-{}#{}.log'.format(message.author.id,
                message.author.name, message.author.discriminator))
            else:
                logstore.set_server_log('{}-{}.log'.format(message.server.id, message.server.name))

            msgsplit = message.content.split(' ', 1)
            cmd = msgsplit[0]
            content = ''
            if len(msgsplit) > 1:
                content = msgsplit[1].strip()

            if message.channel.is_private and message.content.startswith(','):
                print('private time')
            else:
                find = findqueries.find_prefix(mongo, message.server)
                if find.count(True) > 0:
                    prefix = find[0]['prefix']
                    if message.content.startswith(prefix):
                        await call_command(message, cmd[len(prefix):], content, logstore)
                    elif message.content == ',prefix?':
                        if checkqueries.is_listening_channel(mongo, message.server, message.channel):
                            messenger.send_timed_message(bot, 5,
                                ':bulb: | My command prefix for this server: \'**{}**\''.format(prefix), message.channel)
                        else:
                            messenger.send_timed_message(bot, 5,
                                ':bulb: | My command prefix for *{}*: \'**{}**\''.format(message.server.name, prefix),
                                message.author)
                elif message.content.startswith(','):
                    print('not registered')
                    await call_command(message, cmd[1:], content, logstore)

        except Exception as err:
            print('oof')
            print(err)
    '''
    if message.content.startswith(','):
        content = '(' + message.content[1:].lstrip() + ')'
        content = content.replace('=', '')
        content = content.replace(' ', '')
        left = 0
        right = 0
        for c in content:
            if c == '(':
                left += 1
            elif c == ')':
                right += 1
        if not left == right:
            print('Unclosed expression')
        else:
            postfix = to_postfix(content)
            print(postfix)
            print(eval_postfix(postfix))
            await bot.send_message(message.channel, eval_postfix(postfix))

        print(left)
        print(right)'''

async def call_command(message, command, content, logstore):

    log = ('User {} attempted to call => \'{}\''.format(message.author.id, command)
        + '\n\tInput passed => \'{}\'\n '.format(content))
    logwriter.write_log(log, logstore.userlog)

    if message.channel.is_private:
        print('hi')
    else:
        if command in cmdconfig.register_keywords:
            await register.register_command(message, bot, mongo, content, logstore)
        elif checkqueries.is_listening_channel:
            if command in cmdconfig.prefix_keywords:
                await prefix.prefix_command(message, bot, mongo, content, logstore)
            elif command in cmdconfig.practice_keywords:
                await practice.practice_command(message, bot, mongo, content, logstore)
"""
bot.run(BOT_TOKEN)
