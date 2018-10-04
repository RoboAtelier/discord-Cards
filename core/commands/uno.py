"""`uno` command:

UNO command module.
Contains the necessary components to create, edit, and run an UNO game session.
"""

from asyncio import ensure_future, sleep
from discord.utils import find
from random import shuffle
from .config import ERR_WARNINGS
from ..functions import logwriter, messenger, verifier
from ..mongo import checkqueries, deletequeries, findqueries, insertqueries, updatequeries

STANDARD_DECK = [
    'R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'Rr', 'RS', 'RD2',
    'Y0', 'Y1', 'Y2', 'Y3', 'Y4', 'Y5', 'Y6', 'Y7', 'Y8', 'Y9', 'Yr', 'YS', 'YD2',
    'G0', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'Gr', 'GS', 'GD2',
    'B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'Br', 'BS', 'BD2',
    'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'Rr', 'RS', 'RD2',
    'Y1', 'Y2', 'Y3', 'Y4', 'Y5', 'Y6', 'Y7', 'Y8', 'Y9', 'Yr', 'YS', 'YD2',
    'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'Gr', 'GS', 'GD2',
    'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'Br', 'BS', 'BD2',
    'W', 'W', 'W', 'W', 'WD4', 'WD4', 'WD4', 'WD4'
]

UNO_CARD_WORDS = {
    'R': 'Red',
    'Y': 'Yellow',
    'G': 'Green',
    'B': 'Blue',
    'W': 'Wild',
    'D': 'Draw',
    'r': 'Reverse',
    'S': 'Skip'
}

UNO_SESSION = {
    'guild_id': '',
    'channel_id': '',
    'active': False,
    'intermission': False,
    'hrules': [],
    'players': [],
    'hands': {},
    'dwpile': [],
    'dcpile': [],
    'direction': 'r',
    'turn': [],
    'uno': []
}

class UnoSession:

    def __init__(self, gid, cid, players, hrules) -> None:
        self.guild_id = gid
        self.channel_id = cid
        self.active = False
        self.intermission = False
        self.scores = {}
        self.mode = 's'
        self.hrules = hrules
        self.players = players
        self.hands = {}
        self.dwpile = []
        self.dcpile = []
        self.direction = 'r'
        self.turn = []
        self.uno = {}

    @classmethod
    def restore_session(cls, session) -> 'UnoSession':
        """Restores an UNO session object with a given retrieved session dict"""

        rsession = cls(
            session['guild_id'], session['channel_id'],
            session['players'], session['hrules']
        )
        rsession.active = session['active']
        rsession.intermission = session['intermission']
        rsession.mode = session['mode']
        rsession.hands = session['hands']
        rsession.dwpile = session['dwpile']
        rsession.dcpile = session['dcpile']
        rsession.direction = session['direction']
        rsession.turn = session['turn']
        rsession.uno = session['uno']
        return rsession

    @staticmethod
    def look_up_card(search) -> str:
        """Finds a valid card with a given search string."""

        card = ''
        if search.upper() in STANDARD_DECK:
            return search.upper()
        else:
            slist = []
            if ';' in search:
                slist = [s for s in search.split(';', 1) if s]
            elif ',' in search:
                slist = [s for s in search.split(';', 1) if s]
            else:
                slist = [s for s in search.split(' ', 1) if s]
            if len(slist) < 2:
                if 'red' in slist[0]:
                    card += 'R'
                elif 'y' in slist[0]:
                    card += 'Y'
                elif 'g' in slist[0]:
                    card += 'G'
                elif 'b' in slist[0]:
                    card += 'B'
                elif 'w' in slist[0]:
                    card += 'W'
                if 'rev' in slist[0]:
                    card += 'r'
                elif 's' in slist[0]:
                    card += 'S'
                elif ('d' in slist[0] and '2' in slist[0]):
                    card += 'D2'
                elif ('d' in slist[0] and '4' in slist[0]):
                    card += 'D4'
                else:
                    for n in range(10):
                        if str(n) in slist[0]:
                            card += str(n)
                            break
                if card in STANDARD_DECK:
                    return card
            else:
                if 'r' in slist[0]:
                    card += 'R'
                elif 'y' in slist[0]:
                    card += 'Y'
                elif 'g' in slist[0]:
                    card += 'G'
                elif 'b' in slist[0]:
                    card += 'B'
                elif 'w' in slist[0]:
                    card += 'W'
                if 'r' in slist[1]:
                    card += 'r'
                elif 's' in slist[1]:
                    card += 'S'
                elif ('d' in slist[1] and '2' in slist[1]):
                    card += 'D2'
                elif ('d' in slist[1] and '4' in slist[1]):
                    card += 'D4'
                elif slist[1].isdigit():
                    card += slist[1]
                if card in STANDARD_DECK:
                    return card
            return None

    @staticmethod
    def get_card_name(card) -> str:
        """Gets the full name of a given abbreviated card name."""

        cardname = UNO_CARD_WORDS[card[0]]
        if len(card) >= 2:
            if card[1].isalpha():
                cardname += ' ' + UNO_CARD_WORDS[card[1]]
            else:
                cardname += ' ' + card[1]
        if len(card) == 3:
            cardname += ' ' + card[2]
        return cardname

    @staticmethod
    def look_up_color(search) -> str:
        """Finds a valid color with a given search string."""

        if search.startswith('r'):
            return 'Red'
        elif search.startswith('y'):
            return 'Yellow'
        elif search.startswith('g'):
            return 'Green'
        elif search.startswith('b'):
            return 'Blue'
        else:
            return None

    def colorize_wild_card(self, color) -> None:
        """Changes a wild card to a specific color."""

        self.dcpile[0] = self.dcpile[0].replace('W', color)

    def revert_wild_card(self) -> None:
        """Changes a colored wild card back to its normal state."""

        if self.dcpile[0] in ['R', 'Y', 'G', 'B']:
            self.dcpile[0] = 'W'
        elif self.dcpile[0] in ['RD4', 'YD4', 'GD4', 'BD4']:
            self.dcpile[0] = 'WD4'

    def draw_card(self, pid, draw = 1) -> list:
        """Draw cards from the draw pile and place into player hand.

        Args:
            pid (str): The player ID
            draw (int): Number of cards to draw

        Returns:
            The cards drawn.
        """

        cards = []

        if len(self.dwpile) < draw:
            self.dwpile.extend(self.dcpile[1:])
            self.dcpile = [self.dcpile[0]]
            shuffle(self.dwpile)
        self.hands[pid].extend(self.dwpile[:draw])
        cards.extend(self.dwpile)
        self.dwpile = self.dwpile[draw:]
        return cards

    def discard_card(self, pid, cindex) -> None:
        """Places a card onto the top of the discard pile.

        Args:
            pid (str): The player ID
            cindex (int): Card index to pull from player hand

        Returns:
            Nothing.
        """
        self.revert_wild_card()
        self.dcpile.insert(0, self.hands[pid].pop(cindex))

    def uno_callout(self, pid) -> tuple:
        """Attempts to penalize a player for not calling UNO.
        
        Args:
            pid (str): The player ID
        Returns:
            A tuple with a bool indicating if a player was called out
            and two strings for outputting error messages.
            [0] is bool
            [1] is str (log message)
            [2] is str (discord message)
        """

        log = ''
        dmsg = ''

        if pid in self.uno:
            if self.uno[pid] == 'n':
                return (True, log, dmsg)
            else:
                log = 'Tried to call out a safe player.'
                dmsg = (ERR_WARNINGS['no_act'] 
                    + 'That player is safe!')
        elif len(self.hands[pid]) > 1:
            log = 'Tried to call out a player with more than one card.'
            dmsg = (ERR_WARNINGS['no_act'] 
                + 'That player has more than one card.')
        return (False, log, dmsg)

    def uno_call(self, pid) -> tuple:
        """A call when a player only has one card left.
        Used for preventing callouts by other players.
        
        Args:
            pid (str): The player ID
        Returns:
            A tuple with a bool indicating a if a call was successful
            and two strings for outputting error messages.
            [0] is bool
            [1] is str (log message)
            [2] is str (discord message)
        """

        log = ''
        dmsg = ''

        if pid in self.uno:
            if self.uno[pid] == 's':
                log = 'Tried to call UNO! while safe.'
                dmsg = (':exclamation: | You are already safe!')
            elif self.uno[pid] == 'p':
                log = 'Tried to call UNO! again after penalty.'
            elif self.uno[pid] in ['t', 'n']:
                self.uno[pid] = 's'
                return (True, log, dmsg)
        elif len(self.hands[pid]) > 1:
            self.draw_card(pid, 2)
            self.uno[pid] = 'p'
            log = 'Tried to call UNO! while having more than one card.'
            dmsg = (ERR_WARNINGS['error'] 
                + 'Called UNO! while having more than one card. '
                + 'You must draw two cards as a penalty.')
        return (False, log, dmsg)

    def monitor_uno_status(self) -> None:
        """Monitors players' UNO statuses after each turn."""

        pidlist = [player[0] for player in self.players]
        for pid in pidlist:
            if pid in self.uno:
                if self.uno[pid] == 't':
                    self.uno[pid] = 'n'
                elif self.uno[pid] == 'n':
                    self.uno[pid] = 's'
                elif (len(self.hands[pid]) > 1
                    and not self.uno[pid] == 'p'):
                        self.uno.pop(pid)
            elif len(self.hands[pid]) == 1:
                self.uno[pid] = 't'

    def add_player(self, pid, pname):
        """Adds a player into the game session."""

        self.players.append([pid, pname])
        if len(self.players) > 1:
            if not self.active and not self.intermission:
                self.pause_session()
            elif self.active:
                self.hands[pid] = []
                self.draw_card(pid, 7)

    def remove_player(self, pid) -> None:
        """Removes a player from the game session."""

        pidlist = [player[0] for player in self.players]
        del self.players[pidlist.index(pid)]
        if self.active:
            if len(self.players) < 2:
                self.stop_session()
            else:
                if pid in self.turn:
                    npindex = self.get_next_player_index()
                    self.turn = [self.players[npindex][0], 'P']
                if pid in self.hands:
                    self.dcpile.extend(self.hands[pid])
                    del self.hands[pid]
                if pid in self.uno:
                    del self.uno[pid]

    def start_session(self) -> None:
        self.dwpile = STANDARD_DECK.copy()
        shuffle(self.dwpile)
        for pid in [player[0] for player in self.players]:
            self.hands[pid] = []
            self.draw_card(pid, 7)
        self.dcpile.append(self.dwpile.pop(0))
        self.active = True
        self.intermission = False

    def stop_session(self) -> None:
        self.active = False
        self.intermission = False
        self.hands = {}
        self.dwpile = []
        self.dcpile = []
        self.direction = 'r'
        self.turn = []
        self.uno = {}

    def pause_session(self) -> None:
        self.active = False
        self.intermission = True

    def score_cards(self, winner) -> int:
        """Adds up card values to the winner's total points"""

        pts = 0

        if not winner in self.scores:
            self.scores[winner] = 0
        for pid in [p[0] for p in self.players]:
            if not pid == winner:
                for card in self.hands[pid]:
                    if 'W' in card:
                        self.scores[winner] += 50
                        pts += 50
                    elif 'r' in card or 'D' in card or 'S' in card:
                        self.scores[winner] += 20
                        pts += 20
                    else:
                        self.scores[winner] += int(card[1])
                        pts += int(card[1])
        return pts

    def check_player_presence(self, pid) -> None:

        if pid in [p[0] for p in self.players]:
            return True
        return False

    def check_player_action(self, pid, act) -> tuple:
        """Checks if it is a player's turn
        and that they are performing a valid action.
        
        Args:
            pid (str): The player ID
            act (str): Player action

        Returns:
            A tuple with a bool indicating if it's the player's turn
            and two strings for outputting error messages.
            [0] is bool
            [1] is str (log message)
            [2] is str (discord message)
        """

        log = ''
        dmsg = ''

        if pid in self.turn:
            if self.turn[1][0] in act:
                return (True, log, dmsg)
            elif 'd' in self.turn[1]:
                log = 'Tried to do a different action on draw one turn.'
                dmsg = (ERR_WARNINGS['no_act'] 
                    + 'You need to play or keep the card you drew!')
            elif 'P' in self.turn[1]:
                log = 'Tried to do a different action on play turn.'
                dmsg = (ERR_WARNINGS['no_act'] 
                    + 'You need to play a card!')
            elif 'C' in self.turn[1]:
                log = 'Tried to do a different action on color turn.'
                dmsg = (ERR_WARNINGS['no_act'] 
                    + 'You need to choose a card color!')
            elif 'D' in self.turn[1]:
                log = 'Tried to do a different action on draw turn.'
                dmsg = (ERR_WARNINGS['no_act']
                    + 'You need to draw cards!')
        elif not pid in [p[0] for p in self.players]:
            log = 'Tried to play UNO while not in the game.'
            dmsg = ERR_WARNINGS['error'] + 'You need to join the game!'
        else:
            log = 'Tried to play UNO out of turn.'
            dmsg = ERR_WARNINGS['no_act'] + 'It\'s not your turn!'
        return (False, log, dmsg)

    def check_card_match(self, card) -> bool:
        """Checks if a given card can match with the top discard card."""

        if card in ['W', 'WD4']:
            return True
        elif card[0] in self.dcpile[0]:
            return True
        elif card[1] in self.dcpile[0]:
            return True
        return False

    def get_player_index(self) -> int:
        """Gets the position of the current player."""

        pidlist = [player[0] for player in self.players]
        if self.turn[0] in pidlist:
            return pidlist.index(self.turn[0])
        return None

    def get_next_player_index(self, skip = False) -> int:
        """Gets the next player's position in the game session."""

        pindex = self.get_player_index()

        if not skip:
            if self.direction == 'r':
                return 0 if pindex == len(self.players) - 1 else pindex + 1
            else:
                return len(self.players) - 1 if pindex == 0 else pindex - 1
        else:
            if self.direction == 'r':
                if pindex == len(self.players) - 2:
                    return 0
                elif pindex == len(self.players) - 1:
                    return 1
                else:
                    return pindex + 2
            else:
                if pindex == 0:
                    return len(self.players) - 2
                elif pindex == 1:
                    return len(self.players) - 1
                else:
                    return pindex - 2

    def get_player_name(self, pid) -> str:
        """Gets the player name associated with their ID in the session."""

        pidlist = [player[0] for player in self.players]
        if pid in pidlist:
            return self.players[pidlist.index(pid)][1]
        return None

    def freeze_turn(self) -> None:
        """Freezes a player's turn to disable actions."""

        self.turn = [self.turn[0], '']

    def set_first_turn(self) -> None:
        """Sets the first turn of an UNO session."""

        # Wild Draw 4: deck is reshuffled
        if self.dcpile[0] == 'WD4':
            self.dwpile.append(self.dcpile.pop())
            shuffle(self.dwpile)
            self.dcpile.append(self.dwpile.pop(0))
            self.set_first_turn()
            return

        # Wild: starting player must pick a card color
        elif self.dcpile[0] == 'W':
            self.turn = [self.players[0][0], 'C']

        # Any Draw 2: initial player draws 2 cards then next player starts
        elif 'D2' in self.dcpile[0]:
            self.hands[self.players[0][0]].extend(self.dwpile[:2])
            self.dwpile = self.dwpile[2:]
            self.turn = [self.players[1][0], 'P']

        # Any Skip: skip starting player
        elif 'S' in self.dcpile[0]:
            self.turn = [self.players[1][0], 'P']

        # Any Reverse: starting direction is left instead of right
        elif 'r' in self.dcpile[0]:
            self.direction = 'l'
            self.turn = [self.players[len(self.players) - 1][0], 'P']

        else:
            self.turn = [self.players[0][0], 'P']

    def set_next_turn(self, drawone = False) -> None:
        """Sets the next turn of an UNO session."""

        npindex = self.get_next_player_index()

        if 'CD' in self.turn[1]:
            self.turn = [self.players[npindex][0], 'D' + self.turn[1][2:] + 'c']
        elif 'C' in self.turn[1] or self.turn[1] == 'D':
            self.turn = [self.players[npindex][0], 'P']
        else:
            if drawone:
                if 'd' in self.turn:
                    self.turn = [self.players[npindex][0], 'P']
                else:
                    cindex = len(self.hands[self.turn[0]]) - 1
                    self.turn = [self.turn[0], 'd' + str(cindex)]
            # Wild Draw 4
            elif self.dcpile[0] == 'WD4':
                self.turn = [self.turn[0], 'CD4']
            # Wild Card
            elif self.dcpile[0] == 'W':
                self.turn = [self.turn[0], 'C']
            else:
                # Any Draw 2
                if 'D2' in self.dcpile[0]:
                    if 'D' in self.turn[1] or 'd' in self.turn[1]:
                        self.turn = [self.players[npindex][0], 'P']
                    else:
                        self.turn = [self.players[npindex][0], 'D2']
                # Any Skip
                elif 'S' in self.dcpile[0]:
                    npindex = self.get_next_player_index(skip = True)
                    self.turn = [self.players[npindex][0], 'P']
                # Any Reverse
                elif 'r' in self.dcpile[0]:
                    if self.direction == 'r':
                        self.direction = 'l'
                    else:
                        self.direction = 'r'
                    if len(self.players) > 2:
                        npindex = self.get_next_player_index()
                        self.turn = [self.players[npindex][0], 'P']
                # Any Standard
                else:
                    self.turn = [self.players[npindex][0], 'P']

def get_active_session(message, bot, mongo, logstore):
    """Retrieves an active session in a channel from MongoDB."""

    find = findqueries.find_guild_uno_session(
        mongo, message.server, message.channel
    )
    if find.count(True) > 0:
        if find[0]['active']:
            return find[0]
        else:
            log = 'Tried to use UNO command in an inactive session.'
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5, 
                    ERR_WARNINGS['no_act'] + 'Game isn\'t active right now!',
                    message.channel
                )
            )
    return None

async def uno_command(message, bot, mongo, content, logstore):
    """(async)

    UNO command module.
    Contains the necessary components to create, edit, and run an UNO game session.
    Users interact in the game using actions with the appropriate option.
    
    Args:
        message (discord.Message): Discord message object
        bot (discord.Client): Discord bot client
        mongo (pymongo.MongoClient): MongoDB client connection
        content (str): String contents of the discord message without the command name
        logstore (LogStore): Object containing log file paths

    Returns:
        A bool indicating a successful process execution and changes were made
    """

    find = findqueries.find_channel_games(mongo, message.server, message.channel)
    if find.count(True) > 0:
        games = find[0]['channel_games']
        if len(games) == 0 or 'uno' in games:
            option = ''
            params = ''
            if len(content) > 0:
                csplit = content.split(' ', 1)
                option = csplit[0]
                if len(csplit) > 1:
                    params = csplit[1].lower()
            if 'join'.startswith(option) or option in ['-j', 'jn']:
                return await join_action(message, bot, mongo, logstore)
            elif ('leave'.startswith(option) or 'quit'.startswith(option)
                or option in ['-l', '-q', 'lv', 'qt']):
                return await leave_action(message, bot, mongo, logstore)
            elif ('play'.startswith(option) or 'pick'.startswith(option)
                or option in ['-p', 'pk']):
                return await play_action(message, bot, mongo, params, logstore)
            elif 'draw'.startswith(option) or option in ['-d', 'dw']:
                return await draw_action(message, bot, mongo, logstore)
            elif 'keep'.startswith(option) or option in ['-k', 'kp']:
                return await keep_action(message, bot, mongo, logstore)
            elif 'color'.startswith(option) or option in ['-C', 'cl']:
                return await color_action(message, bot, mongo, params, logstore)
            elif 'topcard'.startswith(option) or option in ['-t', 'tc']:
                return await topcard_action(message, bot, mongo, logstore)
            elif ('hand'.startswith(option) or 'cards'.startswith(option)
                or option in ['-h', '-c', 'hd']):
                return await hand_action(message, bot, mongo, logstore)
            elif 'peek'.startswith(option) or option in ['-P']:
                return await peek_action(message, bot, mongo, logstore)
            elif '!' in option:
                return await uno_action(message, bot, mongo, params, logstore)
        else:
            log = 'Tried to use UNO commands in a non-UNO channel.'
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5,
                    ERR_WARNINGS['error'] + 'You cannot play UNO here!',
                    message.channel
                )
            )
            return False

async def join_action(message, bot, mongo, logstore):
    """(async)

    Allows users to join an UNO session.
    
    Args:
        message (discord.Message): Discord message object
        bot (discord.Client): Discord bot client
        mongo (pymongo.MongoClient): MongoDB client connection
        logstore (LogStore): Object containing log file paths

    Returns:
        A bool indicating a successful join and changes were made
    """
    if checkqueries.check_guild_uno_session(mongo, message.server, message.channel):

        go = True
        unosessions = findqueries.findall_guild_uno_session(mongo, message.server)
        cursession = None
        log = 'Tried to join an UNO session but was denied.'
        dmsg = ''
        for session in unosessions:

            # If a user is already playing UNO in another channel
            # they must leave or finish that other UNO game.
            if message.author.id in [p[0] for p in session['players']]:
                if message.channel.id == session['channel_id']:
                    dmsg = ERR_WARNINGS['no_act'] + 'You\'re currently playing here!'
                else:
                    dmsg = (ERR_WARNINGS['no_act']
                        + 'You\'re currently playing UNO in <#{}>!'.format(session['channel_id'])
                    )
                go = False
                break
            elif (message.channel.id == message.channel.id == session['channel_id']
                and len(session['players']) > 9):
                dmsg = ERR_WARNINGS['error'] + 'This session is full!'
                go = False
                break
            else:
                cursession = session.copy()

        if go:
            rsession = UnoSession.restore_session(cursession)
            lpcount = len(rsession.players)
            rsession.add_player(message.author.id, message.author.name)
            updatequeries.update_guild_uno_session(
                mongo, message.server, message.channel, vars(rsession)
            )
            log = 'User {} (ID: {}) has joined an UNO session in #{} (ID: {}).'.format(
                message.author.name, message.author.id,
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            dmsg = ':door: | You\'ve joined the room!'
            await bot.send_message(message.channel, dmsg)
            if rsession.intermission and lpcount == 1:
                dmsg = ':exclamation: | Game starting soon!...'
                await bot.send_message(message.channel, dmsg)
                await sleep(2)
                session = findqueries.find_guild_uno_session(mongo, message.server, message.channel)[0]
                rsession = UnoSession.restore_session(session)
                if len(rsession.players) > 1:
                    rsession.start_session()
                    rsession.set_first_turn()
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel, vars(rsession)
                    )
                    log = 'UNO session in #{} (ID: {}) has started.'.format(
                        message.channel.name, message.channel.id
                    )
                    logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                    await messenger.send_interval_message(
                        bot,
                        [
                            ':sparkles: | Top card: ' + UnoSession.get_card_name(
                                rsession.dcpile[0]
                            ),
                            ':mega: | Your move, <@{}>.'.format(rsession.turn[0])
                        ],
                        2,
                        message.channel
                    )
                    for pid in [p[0] for p in rsession.players]:
                        ouser = find(lambda u: u.id == pid, message.channel.server.members)
                        dmsg = 'Your hand: ' + ', '.join(rsession.hands[pid])
                        await bot.send_message(ouser, dmsg)
                    return True
                else:
                    rsession.stop_session()
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel, vars(rsession)
                    )
                    log = 'UNO session in #{} (ID: {}) was stopped.'.format(
                        message.channel.name, message.channel.id
                    )
                    logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                    dmsg = ':exclamation: | Game stopped prematurely...'
                    await bot.send_message(message.channel, dmsg)
                    return False

        else:
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(bot, 5, dmsg, message.channel)
            )
            return False

    else:
        nsession = UnoSession(
            message.server.id, message.channel.id,
            [[message.author.id, message.author.name]], []
        )
        insertqueries.insert_guild_uno_session(mongo, vars(nsession))
        log = 'Created new UNO session in #{} (ID: {}).'.format(
            message.channel.name, message.channel.id
        )
        logwriter.write_log(log, logstore.userlog, logstore.guildlog)
        ensure_future(
            bot.send_message(
                message.channel,
                ':door: | UNO room created! Game will start when at least one other person joins in.'
            )
        )
        return True

async def leave_action(message, bot, mongo, logstore):
    find = findqueries.find_guild_uno_session(
        mongo, message.server, message.channel
    )
    log = 'Tried to leave UNO session while one is not running.'
    dmsg = ERR_WARNINGS['no_act'] + 'There is no UNO game here!'
    if find.count(True) > 0:
        rsession = UnoSession.restore_session(find[0])
        if rsession.check_player_presence(message.author.id):
            rsession.remove_player(message.author.id)
            updatequeries.update_guild_uno_session(
                mongo, message.server, message.channel, vars(rsession)
            )
            log = 'User {} (ID: {}) left UNO session in #{} (ID: {}).'.format(
                message.author.name, message.author.id,
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            dmsg = ':walking: | You have left the UNO game!'
            await bot.send_message(message.channel, dmsg)
            return True
        else:
            log = 'Tried to use UNO command while not in the session.'
            dmsg = ERR_WARNINGS['no_act'] + 'You need to be in the game!'
    logwriter.write_log(log, logstore.userlog)
    ensure_future(
        messenger.send_timed_message(bot, 5, dmsg, message.channel)
    )
    return False

async def play_action(message, bot, mongo, params, logstore):
    session = get_active_session(message, bot, mongo, logstore)
    if session:
        rsession = UnoSession.restore_session(session)
        ptcheck = rsession.check_player_action(message.author.id, 'Pd')
        log = ptcheck[1]
        dmsg = ptcheck[2]
        if ptcheck[0]:
            card = 'NNN'
            cindex = 0
            if rsession.turn[1] == 'P':
                if params.isdigit():
                    cindex = int(params) - 1
                    hand = rsession.hands[message.author.id]
                    if (cindex > len(hand) - 1 or cindex < 0):
                        log = 'Passed invalid index.'
                        dmsg = ERR_WARNINGS['error'] + 'Invalid card index.'
                    else:
                        card = hand[cindex]
                else:
                    card = UnoSession.look_up_card(params)
                    hand = rsession.hands[message.author.id]
                    if card and card in hand:
                        cindex = hand.index(card)
                    else:
                        log = 'Tried to play a card not on hand.'
                        dmsg = ERR_WARNINGS['error'] + 'You don\'t have that card.'
            elif 'd' in rsession.turn[1]:
                cindex = int(rsession.turn[1][1:])
                card = rsession.hands[message.author.id][cindex]
            if rsession.check_card_match(card):
                rsession.discard_card(message.author.id, cindex)
                if len(rsession.hands[message.author.id]) == 0:
                    earn = rsession.score_cards(message.author.id)
                    rsession.stop_session()
                    rsession.players.append(rsession.players.pop(0))
                    rsession.pause_session()
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel,
                        {
                            'active': rsession.active,
                            'intermission': rsession.intermission,
                            'players': rsession.players,
                            'hands': rsession.hands,
                            'dwpile': rsession.dwpile,
                            'dcpile': rsession.dcpile,
                            'direction': rsession.direction,
                            'turn': rsession.turn,
                            'uno': rsession.uno
                        }
                    )
                    log = 'User {} (ID: {}) won an UNO game in #{} (ID: {}), scoring {} points!'.format(
                        message.author.name, message.author.id,
                        message.channel.name, message.channel.id, str(earn)
                    )
                    logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                    dmsg = ':tada: | {} won! They earn {} points. 10 second intermission...'.format(
                        message.author.name, str(earn)
                    )
                    await bot.send_message(message.author, dmsg)
                    await sleep(10)
                    dmsg = ':exclamation: | Game starting soon!...'
                    await bot.send_message(message.channel, dmsg)
                    await sleep(2)
                    session = findqueries.find_guild_uno_session(mongo, message.server, message.channel)[0]
                    rsession = UnoSession.restore_session(session)
                    if len(rsession.players) > 1:
                        rsession.start_session()
                        rsession.set_first_turn()
                        updatequeries.update_guild_uno_session(
                            mongo, message.server, message.channel, vars(rsession)
                        )
                        log = 'UNO session in #{} (ID: {}) has started.'.format(
                            message.channel.name, message.channel.id
                        )
                        logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                        await messenger.send_interval_message(
                            bot,
                            [
                                ':sparkles: | Top card: ' + UnoSession.get_card_name(
                                    rsession.dcpile[0]
                                ),
                                ':mega: | Your move, <@{}>.'.format(rsession.turn[0])
                            ],
                            2,
                            message.channel
                        )
                        for pid in [p[0] for p in rsession.players]:
                            ouser = find(lambda u: u.id == pid, message.channel.server.members)
                            dmsg = 'Your hand: ' + ', '.join(rsession.hands[pid])
                            await bot.send_message(ouser, dmsg)
                        return True
                    else:
                        rsession.stop_session()
                        updatequeries.update_guild_uno_session(
                            mongo, message.server, message.channel, vars(rsession)
                        )
                        log = 'UNO session in #{} (ID: {}) was stopped.'.format(
                            message.channel.name, message.channel.id
                        )
                        logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                        dmsg = ':exclamation: | Game stopped prematurely...'
                        await bot.send_message(message.channel, dmsg)
                        return False
                else:
                    rsession.set_next_turn()
                    rsession.monitor_uno_status()
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel, vars(rsession)
                    )
                    cardname = UnoSession.get_card_name(card)
                    log = 'User {} (ID: {}) played {} in #{} (ID: {})'.format(
                        message.author.name, message.author.id, cardname,
                        message.channel.name, message.channel.id
                    )
                    logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                    dmsg = (
                        ':book: | Your hand: **'
                        + ', '.join(rsession.hands[message.author.id]) + '**\n-'
                    )
                    await bot.send_message(message.author, dmsg)
                    if 'C' in rsession.turn[1]:
                        await messenger.send_interval_message(
                            bot,
                            [
                                ':sparkles: | **{}** plays a **{}**!'.format(
                                    message.author.name, cardname
                                ),
                                ':mega: | Choose a color for the next turn.'
                            ],
                            2,
                            message.channel
                        )
                    elif 'D' in rsession.turn[1]:
                        await messenger.send_interval_message(
                            bot,
                            [
                                ':sparkles: | **{}** plays a **{}**!'.format(
                                    message.author.name, cardname
                                ),
                                ':mega: | You must draw {} cards <@{}>.'.format(
                                    rsession.turn[1][1], rsession.turn[0]
                                )
                            ],
                            2,
                            message.channel
                        )
                    else:
                        await messenger.send_interval_message(
                            bot,
                            [
                                ':sparkles: | **{}** plays a **{}**!'.format(
                                    message.author.name, cardname
                                ),
                                ':mega: | Your turn <@{}>.'.format(rsession.turn[0])
                            ],
                            2,
                            message.channel
                        )
                    session = get_active_session(message, bot, mongo, logstore)
                    rsession = UnoSession.restore_session(session)
                    rsession.monitor_uno_status()
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel, {'uno': rsession.uno}
                    )
                    return True
        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(bot, 5, dmsg, message.channel)
        )
        return False

async def draw_action(message, bot, mongo, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        rsession = UnoSession.restore_session(session)
        ptcheck = rsession.check_player_action(message.author.id, 'DP')
        log = ptcheck[1]
        dmsg = ptcheck[2]
        if ptcheck[0]:
            if 'D' in rsession.turn[1]:
                draw = int(rsession.turn[1][1:].rstrip('c'))
                rsession.draw_card(message.author.id, draw)
                rsession.set_next_turn()
                rsession.monitor_uno_status()
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, {
                        'hands': rsession.hands,
                        'dwpile': rsession.dwpile,
                        'dcpile': rsession.dcpile,
                        'turn': rsession.turn,
                        'uno': rsession.uno
                    }
                )
                log = 'User {} (ID: {}) drew {} cards in #{} (ID: {})'.format(
                    message.author.name, message.author.id, draw,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                dmsg = (
                    ':book: | Your hand: **'
                    + ', '.join(rsession.hands[message.author.id]) + '**\n-'
                )
                await bot.send_message(message.author, dmsg)
                await sleep(2)
                dmsg = ':sparkles: | **{}** has drawn {} cards.'.format(
                    message.author.name, draw
                )
                await bot.send_message(message.channel, dmsg)
                session = get_active_session(message, bot, mongo, logstore)
                rsession = UnoSession.restore_session(session)
                dmsg = ':mega: | Your turn <@{}>.'.format(rsession.turn[0])
                await bot.send_message(message.channel, dmsg)
            elif rsession.turn[1] == 'P':
                card = rsession.draw_card(message.author.id)[0]
                rsession.set_next_turn(True)
                rsession.monitor_uno_status()
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, {
                        'hands': rsession.hands,
                        'dwpile': rsession.dwpile,
                        'dcpile': rsession.dcpile,
                        'turn': rsession.turn,
                        'uno': rsession.uno
                    }
                )
                log = 'User {} (ID: {}) drew a card in #{} (ID: {})'.format(
                    message.author.name, message.author.id,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                dmsg = ':sparkles: | **' + message.author.name + '** has drawn a card.'
                await bot.send_message(message.channel, dmsg)
                dmsg = ':sparkles: | You drew a **' + UnoSession.get_card_name(card) + '**'
                await bot.send_message(message.author, dmsg)
            return True
        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(bot, 5, dmsg, message.channel)
        )
        return False

async def keep_action(message, bot, mongo, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        rsession = UnoSession.restore_session(session)
        ptcheck = rsession.check_player_action(message.author.id, 'd')
        log = ptcheck[1]
        dmsg = ptcheck[2]
        if ptcheck[0]:
            rsession.set_next_turn()
            rsession.monitor_uno_status()
            updatequeries.update_guild_uno_session(
                mongo, message.server, message.channel, {
                    'hands': rsession.hands,
                    'turn': rsession.turn,
                    'uno': rsession.uno
                }
            )
            log = 'User {} (ID: {}) kept their drawn card in #{} (ID: {})'.format(
                message.author.name, message.author.id,
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            dmsg = (
                ':book: | Your hand: **'
                + ', '.join(rsession.hands[message.author.id]) + '**\n-'
            )
            await bot.send_message(message.author, dmsg)
            dmsg = ':mega: | Your turn <@{}>.'.format(rsession.turn[0])
            await bot.send_message(message.channel, dmsg)
            return True
        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(bot, 5, dmsg, message.channel)
        )
        return False

async def color_action(message, bot, mongo, params, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        rsession = UnoSession.restore_session(session)
        ptcheck = rsession.check_player_action(message.author.id, 'C')
        log = ptcheck[1]
        dmsg = ptcheck[2]
        if ptcheck[0]:
            color = UnoSession.look_up_color(params)
            if color:
                rsession.colorize_wild_card(color[0])
                rsession.set_next_turn()
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, vars(rsession)
                )
                log = 'User {} (ID: {}) chose color {} in #{} (ID: {})'.format(
                    message.author.name, message.author.id, color,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                if rsession.turn[1] == 'P':
                    await messenger.send_interval_message(
                        bot,
                        [
                            ':sparkles: | **{}** picks **{}**!'.format(
                                message.author.name, color
                            ),
                            ':mega: | Your turn <@{}>.'.format(rsession.turn[0])
                        ],
                        2,
                        message.channel
                    )
                elif 'c' in rsession.turn[1]:
                    await messenger.send_interval_message(
                        bot,
                        [
                            ':sparkles: | **{}** picks **{}**!'.format(
                                message.author.name, color
                            ),
                            ':mega: | Draw {} cards <@{}>... or do you challenge the card?'.format(
                                rsession.turn[1][1], rsession.turn[0]
                            )
                        ],
                        2,
                        message.channel
                    )
                session = get_active_session(message, bot, mongo, logstore)
                rsession = UnoSession.restore_session(session)
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, {'uno': rsession.uno}
                )
                return True
            else:
                log = 'Tried to call invalid color.'
                dmsg = (ERR_WARNINGS['error']
                    + 'Pick either **Red**, **Yellow**, **Green**, or **Blue**.')
        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(bot, 5, dmsg, message.channel)
        )
        return False

async def topcard_action(message, bot, mongo, logstore):
    session = get_active_session(message, bot, mongo, logstore)
    if session:
        log = 'Tried to use UNO command while not in the session.'
        dmsg = ERR_WARNINGS['error'] + 'You need to be in the game!'
        rsession = UnoSession.restore_session(session)
        if rsession.check_player_presence(message.author.id):
            log = 'User {} (ID: {}) looked at the top card.'.format(
                message.author.name, message.author.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            dmsg = ':sparkles: | Top card: ' + UnoSession.get_card_name(
                rsession.dcpile[0]
            )
            await bot.send_message(message.channel, dmsg)
            return True
        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(bot, 5, dmsg, message.channel)
        )
        return False

async def hand_action(message, bot, mongo, logstore):
    session = get_active_session(message, bot, mongo, logstore)
    if session:
        log = 'Tried to use UNO command while not in the session.'
        dmsg = ERR_WARNINGS['error'] + 'You need to be in the game!'
        rsession = UnoSession.restore_session(session)
        if rsession.check_player_presence(message.author.id):
            log = 'User {} (ID: {}) checked cards on hand.'.format(
                message.author.name, message.author.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            cards = [
                '**' + str(i + 1) + ':** ' + UnoSession.get_card_name(c)
                for i, c in enumerate(rsession.hands[message.author.id])
            ]
            dmsg = (
                ':book: | Your hand: **'
                + ', '.join(rsession.hands[message.author.id])
                + '**\n\n' + '\n'.join(cards) + '\n-'
            )
            await bot.send_message(message.author, dmsg)
            return True
        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(bot, 5, dmsg, message.channel)
        )
        return False

async def peek_action(message, bot, mongo, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        log = 'Tried to use UNO command while not in the session.'
        dmsg = ERR_WARNINGS['error'] + 'You need to be in the game!'
        rsession = UnoSession.restore_session(session)
        if message.author.id in [p[0] for p in rsession.players]:
            log = 'User {} (ID: {}) peeked at others\' cards.'.format(
                message.author.name, message.author.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            dmsg = (
                ':eyes: | **Player Hands:**\n\n'
                + '\n'.join(
                    [p[1]+ ': ' + str(len(rsession.hands[p[0]])) for p in rsession.players]
                )
                + '\n-'
            )
            await bot.send_message(message.author, dmsg)
            return True
        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(bot, 5, dmsg, message.channel)
        )
        return False

async def uno_action(message, bot, mongo, params, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        log = 'Tried to use UNO command while not in the session.'
        dmsg = ERR_WARNINGS['error'] + 'You need to be in the game!'
        rsession = UnoSession.restore_session(session)
        if rsession.check_player_presence(message.author.id):
            if params == '':
                ucheck = rsession.uno_call(message.author.id)
                if ucheck[0]:
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel, {
                            'uno': rsession.uno
                        }
                    )
                    log = 'User {} (ID: {}) called UNO! in #{} (ID: {})'.format(
                        message.author.name, message.author.id,
                        message.channel.name, message.channel.id
                    )
                    dmsg = ':one: | ' + message.author.name + ' has one card left!'
                    logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                    await bot.send_message(message.channel, dmsg)
                    return True
                else:
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel, {
                            'dwpile': rsession.dwpile,
                            'hands': rsession.hands,
                            'uno': rsession.uno
                        }
                    )
                    logwriter.write_log(ucheck[1], logstore.userlog)
                    if not ucheck[2] == '':
                        await bot.send_message(message.channel, ucheck[2])
                    dmsg = (
                        ':book: | Your hand: **'
                        + ', '.join(rsession.hands[message.author.id]) + '**\n-'
                    )
                    await bot.send_message(message.author, dmsg)
                    return True
            elif params.startswith('<@') and params.endswith('>'):
                pid = ''.join([i for i in params if i.isdigit()])
                pname = rsession.get_player_name(pid)
                ucheck = rsession.uno_callout(pid)
                if ucheck[0]:
                    rsession.draw_card(pid, 2)
                    rsession.uno.pop(pid)
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel, {
                            'dwpile': rsession.dwpile,
                            'hands': rsession.hands,
                            'uno': rsession.uno
                        }
                    )
                    log = 'User {} (ID: {}) called out {} (ID: {}) in #{} (ID: {})'.format(
                        message.author.name, message.author.id,
                        pname, pid,
                        message.channel.name, message.channel.id
                    )
                    logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                    dmsg = ':exclamation: | ' + pname + ' was called out for not saying UNO!'
                    await bot.send_message(message.channel, dmsg)
                    ouser = find(lambda u: u.id == pid, message.channel.server.members)
                    dmsg = 'Your hand: ' + ', '.join(rsession.hands[pid])
                    await bot.send_message(ouser, dmsg)
                    return True
                else:
                    log = ucheck[1]
                    dmsg = ucheck[2]
            else:
                log = ucheck[1]
                dmsg = ERR_WARNINGS['invalid_in'] + 'You must mention the player.'
        logwriter.write_log(log, logstore.userlog)
        if not dmsg == '':
            ensure_future(
                messenger.send_timed_message(bot, 5, dmsg, message.channel)
            )
        return False