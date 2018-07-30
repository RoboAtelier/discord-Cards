"""
`blackjack` command:

Start or play a game of blackjack.
Games are hosted through channels.
"""

from . import config
from ..functions import logwriter, messenger
from ..mongo import checkqueries, deletequeries, insertqueries, updatequeries

async def uno_command(message, bot, mongo, content, logstore):

    """
    (async)

    `uno` command:

    Contains functions for playing UNO and options for rule variations.
    Games are hosted through discord servers only.

    :param: `message` - discord message

    :param: `bot` - discord bot

    :param: `mongo` - mongodb client

    :param: `content` - contents of the message

    :param: `logstore` - class containing log paths
    """

    