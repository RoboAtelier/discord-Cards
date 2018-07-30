"""
`blackjack` command:

Start or play a game of blackjack.
Games are hosted through channels.
"""

from . import config
from ..functions import logwriter, messenger
from ..mongo import checkqueries, deletequeries, insertqueries, updatequeries

async def blackjack_command(message, bot, mongo, content, logstore):

    """
    (async)

    `blackjack` command:

    Contains functions for playing blackjack.
    Games are hosted through discord servers only.

    :param: `message` - discord message

    :param: `bot` - discord bot

    :param: `mongo` - mongodb client

    :param: `content` - contents of the message

    :param: `logstore` - class containing log paths
    """

    