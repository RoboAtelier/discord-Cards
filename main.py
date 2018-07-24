import asyncio
import discord
import logging
import re
from token import BOT_TOKEN
from core.commands import cmdconfig, practice, prefix, register
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
    authSource=credentials.AUTHSRC
)

# Create new bot object.
BOT = discord.Client()

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
    log = ('Miss Fey has been initialized!'
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

pi = '3.141592653589793'#238462643383279502884197169399375
e = '2.718281828459045'

def to_postfix(expr):
    prec = {
        'sin': 5,
        'cos': 5,
        'tan': 5,
        'sqrt': 5,
        '^': 4,
        '*': 3,
        '/': 3,
        '+': 2,
        '-': 2,
        '(': 1
    }

    stack = []
    postfix = []
    lastchar = ' '
    number = ''
    i = 0
    jump = 1

    while i < len(expr):
        #'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

        # Scan for numbers
        if expr[i] in '0123456789.':
            if lastchar in ')abcdefghijklmnopqrstuvwxyz':
                stack.append('*')
            number += expr[i]

        # Scan for variables/keywords
        elif expr[i] in 'abcdefghijklmnopqrstuvwxyz':

            constant = False
            function = False

            # Append current number
            if len(number) > 0:
                postfix.append(number)
                number = ''

            # Cosine
            if expr[i:i+3] == 'cos':
                stack.append('cos')
                if expr[i+4] == '(':
                    jump += 3
                else:
                    jump += 2
                function = True

            # Euler's number e
            elif expr[i] == 'e':
                postfix.append(e)
                constant = True

            # pi π
            elif expr[i:i+2] == 'pi':
                postfix.append(pi)
                jump += 1
                constant = True

            # Square root √
            elif expr[i:i+4] == 'sqrt':
                stack.append('sqrt')
                if expr[i+5] == '(':
                    jump += 4
                else:
                    jump += 3
                function = True

            # Sine
            elif expr[i:i+3] == 'sin':
                stack.append('sin')
                if expr[i+4] == '(':
                    jump += 3
                else:
                    jump += 2
                function = True

            # Tangent
            elif expr[i:i+3] == 'tan':
                stack.append('tan')
                if expr[i+4] == '(':
                    jump += 3
                else:
                    jump += 2
                function = True

            if constant:
                if not lastchar in '+-*/^(' or not expr[i+1] in '+-*/^)':
                    stack.append('*')
        
        # Exact symbol match pi π
        elif expr[i] == 'π':

            # Append current number
            if len(number) > 0:
                postfix.append(number)
                number = ''

            if not lastchar in '+-*/^(' or not expr[i+1] in '+-*/^)':
                stack.append('*')
            postfix.append(pi)

        # Exact symbol match square root √
        elif expr[i] == '√':

            # Append current number
            if len(number) > 0:
                postfix.append(number)
                number = ''
 
            stack.append('sqrt')

        # Scan for other operators and other symbols
        elif not expr[i] == ' ':

            # Append current number
            if len(number) > 0:
                postfix.append(number)
                number = ''

            # Check for negation
            if expr[i] == '-':

                if lastchar in '+-*/^(':
                    postfix.append('-1')
                    stack.append('*')

                # If not negation, add subtraction operator
                else:
                    while not len(stack) == 0 and prec[expr[i]] <= prec[stack[len(stack)-1]]:
                        postfix.append(stack.pop())
                    stack.append(expr[i])

            # Scan left parenthesis
            elif expr[i] == '(':
                if lastchar in '0123456789)':
                    stack.append('*')
                stack.append(expr[i])

            # Scan right parenthesis
            elif expr[i] == ')':
                top = stack.pop()
                while not top == '(':
                    postfix.append(top)
                    top = stack.pop()

            # Scan for operators
            else:
                while not len(stack) == 0 and prec[expr[i]] <= prec[stack[len(stack)-1]]:
                    postfix.append(stack.pop())
                stack.append(expr[i])

        if not expr[i] == ' ':
            if expr[i] in 'abcdefghijklmnopqrstuvwxyz':
                lastchar = '('
            else:    
                lastchar = expr[i]
        i += jump
        if jump > 1:
            jump = 1
        print(stack)
        print(postfix)
    
    while not len(stack) == 0:
        postfix.append(stack.pop())

    return postfix

def eval_postfix(postfix):
    nums = []

    for c in postfix:
        if re.match(r'\-?\d+', c):
            nums.append(float(c))
        else:
            if c == 'sqrt':
                result = perform_operation(c, nums.pop(), 0.5)
                nums.append(result)
            elif c in ['sin', 'cos', 'tan']:
                result = perform_operation(c, nums.pop(), 0)
                nums.append(result)
            else:
                num2 = nums.pop()
                num1 = nums.pop()
                result = perform_operation(c, num1, num2)
                nums.append(result)
    result = nums.pop()
    if result < 99.9999999999999999:
        return '{:.15g}'.format(float('{:.15f}'.format(result)))
    else:
        return '{:.15g}'.format(result)

def perform_operation(operation, num1, num2):
    if operation == '+':
        return num1 + num2
    elif operation == '-':
        return num1 - num2
    elif operation == '*':
        return num1 * num2
    elif operation == '/':
        return num1 / num2
    elif operation == '^':
        return num1 ** num2
    elif operation == 'sqrt':
        return num1 ** num2
    elif operation == 'sin':
        return sin(num1)
    elif operation == 'cos':
        return cos(num1)
    elif operation == 'tan':
        return tan(num1)
    else:
        return 0

bot.run(token)