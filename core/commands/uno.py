"""
`uno` command:

UNO game module.
Contains the necessary components to run an UNO game session.
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
        self.host = ''
        self.players = players
        self.hands = {}
        self.dwpile = []
        self.dcpile = []
        self.direction = 'r'
        self.turn = []
        self.uno = {}

    @classmethod
    def restore_session(cls, session) -> 'UnoSession':
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
        """Finds a card with a given search string.

        Args:
            search (str): Search string

        Returns:
            An abbreviated card name.
        """

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
        """Gets the full name of a given abbreviated card name.

        Args:
            card (str): Abbreviated card

        Returns:
            A full card name.
        """

        cardname = UNO_CARD_WORDS[card[0]]
        if card[1].isalpha():
            cardname += ' ' + UNO_CARD_WORDS[card[1]]
        else:
            cardname += ' ' + card[1]
        if len(card) == 3:
            cardname += ' ' + card[2]
        return cardname

    @staticmethod
    def look_up_color(search) -> str:

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

    def draw_card(self, pid, draw = 1) -> None:
        """Draw cards from the draw pile and place into player hand.

        Args:
            pid (str): The player ID
            draw (int): Number of cards to draw

        Returns:
            Nothing.
        """
        if len(self.dwpile) < draw:
            self.dwpile.extend(self.dcpile[1:])
            self.dcpile = [self.dcpile[0]]
            shuffle(self.dwpile)
        self.hands[pid].extend(self.dwpile[:draw])
        self.dwpile = self.dwpile[draw:]

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
        elif card[1] in self.dcpile[1]:
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
            return self.players[pidlist.index(pid)][0]
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
                    npindex = self.get_next_player_index()
                    self.turn = [self.players[npindex][0], 'P']
                # Any Standard
                else:
                    self.turn = [self.players[npindex][0], 'P']

async def uno_command(message, bot, mongo, content, logstore):

    """
    (async)

    `uno` command:

    UNO game module.
    Contains the necessary components to run an UNO game session.
    Can be run in different game modes and deck variations.
    
    Returns True if the process was executed successfully and changes were made.

    :param: `message` - discord message

    :param: `bot` - discord bot

    :param: `mongo` - mongo client

    :param: `content` - contents of the message

    :param: `logstore` - class containing log paths
    """

    find = findqueries.find_channel_games(mongo, message.server, message.channel)
    if find.count(True) > 0:
        games = find[0]['channel_games']
        if ('uno' in games or len(games) == 0):
            csplit = content.split(' ', 1)
            option = csplit[0]
            params = csplit[1].lower()
            """if ('make'.startswith(option) or option in ['-m']):
                if checkqueries.check_guild_uno_session(mongo, message.server, message.channel):

                    log = 'Tried to start UNO session while one is already running.'
                    logwriter.write_log(log, logstore.userlog)
                    ensure_future(
                        messenger.send_timed_message(
                            bot, 5,
                            ERR_WARNINGS['error'] + 'There\'s already an ongoing game here! Join it instead.',
                            message.channel
                        )
                    )
                    return False
                else:
                    unodeck = STANDARD_DECK.copy()
                    shuffle(unodeck)
                    unosession = UNO_SESSION.copy()
                    unosession['guildid'] = message.server.id
                    unosession['channelid'] = message.channel.id
                    unosession['players'] = [[message.author.id, message.author.name]]
                    unosession['dwpile'] = unodeck
                    insertqueries.insert_guild_uno_session(mongo, unosession)
                    log = 'Created new UNO session in #{} (ID: {}).'.format(message.channel.name, message.channel.id)
                    logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                    await bot.send_message(
                        message.channel,
                        ':door: | UNO room created! Game will start when at least one other person joins in.'
                    )
                    return True"""
            if ('join'.startswith(option) or option in ['-j', 'jn']):
                return await join_action(message, bot, mongo, logstore)

            elif ('play'.startswith(option) or option in ['-p']):
                return await play_action(message, bot, mongo, params, logstore)

            elif ('color'.startswith(option) or option in ['-c']):
                return await color_action(message, bot, mongo, params, logstore)

            elif ('draw'.startswith(option) or option in ['-d']):
                return await draw_action(message, bot, mongo, logstore)

            elif ('keep'.startswith(option) or option in ['-k']):
                return await keep_action(message, bot, mongo, logstore)

            elif '!' in option:
                return await uno_action(message, bot, mongo, params, logstore)

            elif ('leave'.startswith(option) or 'quit'.startswith(option)
                or option in ['-l', '-q']):
                return await quit_action(message, bot, mongo, params, logstore)

        else:
            log = 'Tried to start UNO session while being in a non-UNO channel.'
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5,
                    ERR_WARNINGS['error'] + 'You cannot play UNO here.',
                    message.channel
                )
            )
            return True

async def play_action(message, bot, mongo, params, logstore):
    session = get_active_session(message, bot, mongo, logstore)
    if session:
        rsession = UnoSession.restore_session(session)
        ptcheck = rsession.check_player_action(message.author.id, 'Pd')
        if ptcheck[0]:
            card = 'NNN'
            cindex = 0
            if rsession.turn[1] == 'P':
                if params.isdigit():
                    cindex = int(params) - 1
                    hand = rsession.hands[message.author.id]
                    if (cindex > len(hand) - 1 or cindex < 0):
                        log = 'Passed invalid index.'
                        logwriter.write_log(log, logstore.userlog)
                        ensure_future(
                            messenger.send_timed_message(
                                bot, 5,
                                (ERR_WARNINGS['error']
                                    + 'Invalid card index.'),
                                message.channel
                            )
                        )
                        return False
                    else:
                        card = hand[cindex]
                else:
                    card = UnoSession.look_up_card(params)
                    hand = rsession.hands[message.author.id]
                    if card and card in hand:
                        cindex = hand.index(card)
                    else:
                        log = 'Tried to play a card not on hand.'
                        logwriter.write_log(log, logstore.userlog)
                        ensure_future(
                            messenger.send_timed_message(
                                bot, 5,
                                (ERR_WARNINGS['error']
                                    + 'You don\'t have that card.'),
                                message.channel
                            )
                        )
                        return False
            elif 'd' in rsession.turn[1]:
                cindex = int(rsession.turn[1][1:])
                card = rsession.hands[message.author.id][cindex]
            if rsession.check_card_match(card):
                rsession.discard_card(message.author.id, cindex)
                if len(rsession.hands[message.author.id]) == 0:
                    earn = rsession.score_cards(message.author.id)
                    rsession.stop_session()
                    rsession.pause_session()
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel,
                        {
                            'active': rsession.active,
                            'intermission': rsession.intermission,
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
                    ensure_future(
                        bot.send_message(message.author, dmsg)
                    )
                    await sleep(10)
                    dmsg = ':exclamation: | Game starting soon!...'
                    await bot.send_message(message.channel, dmsg)
                    await sleep(2)
                    session = findqueries.find_guild_uno_session(mongo, message.server, message.channel)[0]
                    rsession = UnoSession.restore_session(session)
                    if len(rsession.players) > 1:
                        rsession.start_session()
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
                                ':sparkles: | Top card: {}'.format(rsession.dcpile[0]),
                                ':mega: | Your move, <@{}>.'.format(rsession.turn[0])
                            ],
                            2,
                            message.channel
                        )
                        for pid in [p[0] for p in rsession.players]:
                            ouser = find(lambda u: u.id == pid, message.channel.server.members)
                            handmsg = (
                                ':notebook: | **Your hand:**\n\n'
                                + ' '.join(rsession.hands[pid])
                            )
                            await bot.send_message(ouser, handmsg)
                        return True
                    else:
                        rsession.stop_session()
                        updatequeries.update_guild_uno_session(
                            mongo, message.server, message.channel, vars(rsession)
                        )
                        dmsg = ':exclamation: | Game stopped prematurely...'
                        log = 'UNO session in #{} (ID: {}) was stopped.'.format(
                            message.channel.name, message.channel.id
                        )
                        logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                        await bot.send_message(message.channel, dmsg)
                        return False
                else:
                    rsession.freeze_turn()
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
                    pmsg = (
                        ':notebook: | Your hand: **'
                        + ' '.join(rsession.hands[0])
                        + '**'
                    )
                    ensure_future(
                        bot.send_message(message.author, pmsg)
                    )
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
                    rsession.set_next_turn()
                    rsession.monitor_uno_status()
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel, vars(rsession)
                    )
                    return True
        else:
            logwriter.write_log(ptcheck[1], logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5, ptcheck[2], message.channel
                )
            )
            return False
        
        """if check_player_turn(message, bot, logstore, session, 'Pp'):

            if 'P' in session['turn']:
                if params.isdigit():
                    index = int(params) - 1
                    hand = session['hands'][message.author.id]
                    if (index > len(hand) - 1 or index < 0):
                        log = 'Passed invalid index.'
                        logwriter.write_log(log, logstore.userlog)
                        ensure_future(
                            messenger.send_timed_message(
                                bot, 5,
                                (ERR_WARNINGS['error']
                                    + 'Invalid card index.'),
                                message.channel
                            )
                        )
                        return False
                    else:
                        card = hand[index]
                        if check_card_match(card, session['dcpile'][0]):

                            session = set_next_turn(card, session)
                            session['dcpile'].insert(
                                0, session['hands'][message.author.id].pop(index)
                            )
                            cardname = UNO_CARD_WORDS[card[0]]
                            if card[1].isalpha():
                                cardname += ' ' + UNO_CARD_WORDS[card[1]]
                            else:
                                cardname += ' ' + card[1]
                            if len(card) == 3:
                                cardname += ' ' + card[2]
                            if 'C' in session['turn'][1]:
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
                            elif 'D' in session['turn'][1]:
                                await messenger.send_interval_message(
                                    bot,
                                    [
                                        ':sparkles: | **{}** plays a **{}**!'.format(
                                            message.author.name, cardname
                                        ),
                                        ':mega: | You must draw {} cards <@{}>.'.format(
                                            session['turn'][1][1], session['turn'][0]
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
                                        ':mega: | Your turn <@{}>.'.format(session['turn'][0])
                                    ],
                                    2,
                                    message.channel
                                )
                            updatequeries.update_guild_uno_session(
                                mongo, message.server, message.channel, session
                            )
                            log = 'User {} (ID: {}) played {} in #{} (ID: {})'.format(
                                message.author.name, message.author.id, cardname,
                                message.channel.name, message.channel.id
                            )
                            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                            return True
                                
                        else:
                            log = 'Played a non-matching card.'
                            logwriter.write_log(log, logstore.userlog)
                            ensure_future(
                                messenger.send_timed_message(
                                    bot, 5,
                                    (ERR_WARNINGS['error']
                                        + 'That does not match the top card.'),
                                    message.channel
                                )
                            )
                            return False

                else:

                    card = look_up_card(params)
                    if card:
                        hand = session['hands'][message.author.id]
                        if card in hand:
                            index = hand.index(card)
                            if check_card_match(card, session['dcpile'][0]):

                                session = set_next_turn(card, session)
                                session['dcpile'].insert(
                                    0, session['hands'][message.author.id].pop(index)
                                )
                                cardname = UNO_CARD_WORDS[card[0]]
                                if card[1].isalpha():
                                    cardname += ' ' + UNO_CARD_WORDS[card[1]]
                                else:
                                    cardname += ' ' + card[1]
                                if len(card) == 3:
                                    cardname += ' ' + card[2]
                                if 'C' in session['turn'][1]:
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
                                elif 'D' in session['turn'][1]:
                                    await messenger.send_interval_message(
                                        bot,
                                        [
                                            ':sparkles: | **{}** plays a **{}**!'.format(
                                                message.author.name, cardname
                                            ),
                                            ':mega: | You must draw {} cards <@{}>.'.format(
                                                session['turn'][1][1], session['turn'][0]
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
                                            ':mega: | Your turn <@{}>.'.format(session['turn'][0])
                                        ],
                                        2,
                                        message.channel
                                    )
                                updatequeries.update_guild_uno_session(
                                    mongo, message.server, message.channel, session
                                )
                                log = 'User {} (ID: {}) played {} in #{} (ID: {})'.format(
                                    message.author.name, message.author.id, cardname,
                                    message.channel.name, message.channel.id
                                )
                                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                                return True

                            else:
                                log = 'Played a non-matching card.'
                                logwriter.write_log(log, logstore.userlog)
                                ensure_future(
                                    messenger.send_timed_message(
                                        bot, 5,
                                        (ERR_WARNINGS['error']
                                            + 'That is not a match with the top card.'),
                                        message.channel
                                    )
                                )
                            return False
                        else:
                            log = 'Tried to play a card not on hand.'
                            logwriter.write_log(log, logstore.userlog)
                            ensure_future(
                                messenger.send_timed_message(
                                    bot, 5,
                                    (ERR_WARNINGS['error']
                                        + 'You don\'t have that card.'),
                                    message.channel
                                )
                            )
                            return False

            elif 'p' in session['turn']:
                index = int(session['turn'][1][1:])
                card = session['hands'][message.author.id][index]
                if check_card_match(card, session['dcpile'][0]):
                    session = set_next_turn(card, session)
                    session['dcpile'].insert(
                        0, session['hands'][message.author.id].pop(index)
                    )
                    cardname = UNO_CARD_WORDS[card[0]]
                    if card[1].isalpha():
                        cardname += ' ' + UNO_CARD_WORDS[card[1]]
                    else:
                        cardname += ' ' + card[1]
                    if len(card) == 3:
                        cardname += ' ' + card[2]
                        session = set_next_turn(card, session)
                        session['dcpile'].insert(
                            0, session['hands'][message.author.id].pop(index)
                        )
                        cardname = UNO_CARD_WORDS[card[0]]
                        if card[1].isalpha():
                            cardname += ' ' + UNO_CARD_WORDS[card[1]]
                        else:
                            cardname += ' ' + card[1]
                        if len(card) == 3:
                            cardname += ' ' + card[2]
                        if 'C' in session['turn'][1]:
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
                        elif 'D' in session['turn'][1]:
                            await messenger.send_interval_message(
                                bot,
                                [
                                    ':sparkles: | **{}** plays a **{}**!'.format(
                                        message.author.name, cardname
                                    ),
                                    ':mega: | You must draw {} cards <@{}>.'.format(
                                        session['turn'][1][1], session['turn'][0]
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
                                    ':mega: | Your turn <@{}>.'.format(session['turn'][0])
                                ],
                                2,
                                message.channel
                            )
                        updatequeries.update_guild_uno_session(
                            mongo, message.server, message.channel, session
                        )
                        log = 'User {} (ID: {}) played {} in #{} (ID: {})'.format(
                            message.author.name, message.author.id, cardname,
                            message.channel.name, message.channel.id
                        )
                        logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                        return True
                                
                else:
                    log = 'Played a non-matching card.'
                    logwriter.write_log(log, logstore.userlog)
                    ensure_future(
                        messenger.send_timed_message(
                            bot, 5,
                            (ERR_WARNINGS['error']
                                + 'That is not a match with the top card.'),
                            message.channel
                        )
                    )
                    return False"""

async def color_action(message, bot, mongo, params, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        rsession = UnoSession.restore_session(session)
        ptcheck = rsession.check_player_action(message.author.id, 'C')
        if ptcheck[0]:
            color = UnoSession.look_up_color(params)
            if color:
                rsession.colorize_wild_card(color[0])
                rsession.freeze_turn()
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
                rsession.set_next_turn()
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, vars(rsession)
                )
                return True
            else:
                log = 'Tried to call invalid color.'
                logwriter.write_log(log, logstore.userlog)
                ensure_future(
                    messenger.send_timed_message(
                        bot, 5,
                        (ERR_WARNINGS['error']
                            + 'Pick either **Red**, **Yellow**, **Green**, or **Blue**.'),
                        message.channel
                    )
                )
                return False
        else:
            logwriter.write_log(ptcheck[1], logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5, ptcheck[2], message.channel
                )
            )
            return False
        """if check_player_turn(message, bot, logstore, session, 'C'):
            color = ''
            if params.startswith('r'):
                color = 'Red'
            elif params.startswith('y'):
                color = 'Yellow'
            elif params.startswith('g'):
                color = 'Green'
            elif params.startswith('b'):
                color = 'Blue'
            else:
                log = 'Tried to call invalid color.'
                logwriter.write_log(log, logstore.userlog)
                ensure_future(
                    messenger.send_timed_message(
                        bot, 5,
                        (ERR_WARNINGS['error']
                            + 'Pick either Red, Yellow, Green, or Blue.'),
                        message.channel
                    )
                )
                return False
            index = get_player_index(session)
            if session['direction'] == 'r':
                if index == len(session['players']) - 1:
                    index = 0
                else:
                    index += 1
            else:
                if index == 0:
                    index = len(session['players'] - 1)
                else:
                    index -= 1
            session['dcpile'][0] = color[0] + session['dcpile'][0]
            if session['turn'][1] == 'C':
                session['turn'] = [session['players'][index][0], 'P']
                await messenger.send_interval_message(
                    bot,
                    [
                        ':sparkles: | **{}** picks **{}** for the card color!'.format(
                            message.author.name, color
                        ),
                        ':mega: | Your turn <@{}>.'.format(session['turn'][0])
                    ],
                    2,
                    message.channel
                )
            else:
                session['turn'] = [session['players'][index][0], 'D4c']
                await messenger.send_interval_message(
                    bot,
                    [
                        ':sparkles: | **{}** picks **{}** for the card color!'.format(
                            message.author.name, color
                        ),
                        ':mega: | You must draw {} cards <@{}>... or challenge the play?'.format(
                            session['turn'][1][1], session['turn'][0]
                        )
                    ],
                    2,
                    message.channel
                )
            updatequeries.update_guild_uno_session(
                mongo, message.server, message.channel, session
            )
            log = 'User {} (ID: {}) chose color {} in #{} (ID: {})'.format(
                message.author.name, message.author.id, color,
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            return True"""

async def draw_action(message, bot, mongo, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        rsession = UnoSession.restore_session(session)
        ptcheck = rsession.check_player_action(message.author.id, 'DP')
        if ptcheck[0]:
            if 'D' in rsession.turn[1]:
                draw = int(session.turn[1][1:].rstrip('c'))
                rsession.draw_card(message.author.id, draw)
                rsession.freeze_turn()
                rsession.monitor_uno_status()
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, vars(rsession)
                )
                log = 'User {} (ID: {}) drew {} cards in #{} (ID: {})'.format(
                    message.author.name, message.author.id, draw,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                pmsg = (
                    ':notebook: | Your hand: **'
                    + ' '.join(rsession.hands[message.author.id])
                    + '**'
                )
                ensure_future(
                    bot.send_message(message.author, pmsg)
                )
                await messenger.send_interval_message(
                    bot,
                    [
                        ':sparkles: | **{}** has drawn {} cards.'.format(
                            message.author.name, draw
                        ),
                        ':mega: | Your turn <@{}>.'.format(rsession.turn[0])
                    ],
                    2,
                    message.channel
                )
                session = get_active_session(message, bot, mongo, logstore)
                rsession = UnoSession.restore_session(session)
                rsession.set_next_turn()
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, vars(rsession)
                )
            elif rsession.turn[1] == 'P':
                rsession.draw_card(message.author.id)
                rsession.set_next_turn(True)
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, vars(rsession)
                )
                log = 'User {} (ID: {}) drew a card in #{} (ID: {})'.format(
                    message.author.name, message.author.id,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                ensure_future(
                    bot.send_message(
                        message.channel,
                        ':sparkles: | **{}** has drawn a card.'.format(
                            message.author.name
                        )
                    )
                )
            return True
        else:
            logwriter.write_log(ptcheck[1], logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5, ptcheck[2], message.channel
                )
            )
            return False
            """if 'D' in session['turn'][1]:
                draw = int(session['turn'][1][1])
                index = get_player_index(session)
                if session['direction'] == 'r':
                    if index == len(session['players']) - 1:
                        index = 0
                    else:
                        index += 1
                else:
                    if index == 0:
                        index = len(session['players'] - 1)
                    else:
                        index -= 1
                if len(session['dwpile']) < int(draw):
                    session['dwpile'].extend(session['dcpile'][1:])
                    session['dcpile'] = [session['dcpile'][0]]
                    shuffle(session['dwpile'])
                session['hands'][message.author.id].extend(session['dwpile'][:draw])
                session['dwpile'] = session['dwpile'][draw:]
                session['turn'] = [session['players'][index][0], 'P']
                await messenger.send_interval_message(
                    bot,
                    [
                        ':sparkles: | **{}** has drawn {} cards.'.format(
                            message.author.name, draw
                        ),
                        ':mega: | Your turn <@{}>.'.format(session['turn'][0])
                    ],
                    2,
                    message.channel
                )
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, session
                )
                log = 'User {} (ID: {}) drew {} cards in #{} (ID: {})'.format(
                    message.author.name, message.author.id, draw,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                return True
            elif 'P' in session['turn'][1]:
                index = get_player_index(session)
                if len(session['dwpile']) < 1:
                    session['dwpile'].extend(session['dcpile'][1:])
                    session['dcpile'] = [session['dcpile'][0]]
                    shuffle(session['dwpile'])
                session['hands'][message.author.id].append(
                    session['dwpile'].pop(0)
                )
                session['turn'] = [
                    session['players'][index][0], 'p' + str(
                        len(session['hands'][message.author.id]) - 1
                    )
                ]
                ensure_future(
                    bot.send_message(
                        message.channel,
                        ':sparkles: | **{}** has drawn a card.'.format(
                            message.author.name
                        )
                    )
                )
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, session
                )
                log = 'User {} (ID: {}) drew a card in #{} (ID: {})'.format(
                    message.author.name, message.author.id,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                return True"""

async def keep_action(message, bot, mongo, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        rsession = UnoSession.restore_session(session)
        ptcheck = rsession.check_player_action(message.author.id, 'p')
        if ptcheck[0]:
            rsession.set_next_turn()
            rsession.monitor_uno_status()
            updatequeries.update_guild_uno_session(
                mongo, message.server, message.channel, vars(rsession)
            )
            log = 'User {} (ID: {}) kept their drawn card in #{} (ID: {})'.format(
                message.author.name, message.author.id,
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            pmsg = (
                ':notebook: | **Your hand:**\n\n'
                + ' '.join(rsession.hands[message.author.id])
            )
            ensure_future(
                bot.send_message(message.author, pmsg)
            )
            ensure_future(
                bot.send_message(
                    message.channel,
                    ':mega: | Your turn <@{}>.'.format(rsession.turn[0])
                )
            )
            return True
        else:
            logwriter.write_log(ptcheck[1], logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5, ptcheck[2], message.channel
                )
            )
            return False
        """if check_player_turn(message, bot, logstore, session, 'p'):
            pindex = get_next_player_index(session)
            session['turn'] = [session['players'][pindex][0], 'P']
            ensure_future(
                bot.send_message(
                    message.channel,
                    ':mega: | Your turn <@{}>.'.format(session['turn'][0])
                )
            )
            handmsg = (
                ':notebook: | Your hand:\n\n**'
                + ' '.join(session['hands'][0])
                + '**'
            )
            ensure_future(
                bot.send_message(
                    message.author,
                    handmsg
                )
            )
            updatequeries.update_guild_uno_session(
                mongo, message.server, message.channel, session
            )
            log = 'User {} (ID: {}) kept their drawn card in #{} (ID: {})'.format(
                message.author.name, message.author.id,
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            return True
    return False"""

async def peek_action(message, bot, mongo, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        rsession = UnoSession.restore_session(session)
        if message.author.id in [p[0] for p in rsession.players]:
            pmsg = (
                ':eyes: | **Player Hands:**\n\n'
                + '\n'.join(
                    [p[1]+ ': ' + str(len(rsession.hands[p[0]])) for p in rsession.players]
                )
            )
            ensure_future(
                bot.send_message(message.author, pmsg)
            )
            log = 'User {} (ID: {}) peeked at others\' cards.'.format(
                message.author.name, message.author.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            return True
        else:
            log = 'Tried to play UNO while not in the game.'
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5,
                    ERR_WARNINGS['error'] + 'You need to join the game!',
                    message.channel
                )
            )
            return False

async def uno_action(message, bot, mongo, params, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        rsession = UnoSession.restore_session(session)
        if message.author.id in [p[0] for p in rsession.players]:
            if params == '':
                ucheck = rsession.uno_call(message.author.id)
                if ucheck[0]:
                    log = 'User {} (ID: {}) called UNO! in #{} (ID: {})'.format(
                        message.author.name, message.author.id,
                        message.channel.name, message.channel.id
                    )
                    logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                    ensure_future(
                        bot.send_message(
                            message.channel,
                            ':one: | {} has one card left!'.format(message.author.name)
                        )
                    )
                    return True
                else:
                    logwriter.write_log(ucheck[1], logstore.userlog)
                    ensure_future(
                        messenger.send_timed_message(
                            bot, 5, ucheck[2], message.channel
                        )
                    )
                    return False
            elif params.startswith('<@') and params.endswith('>'):
                pid = params[2:len(params) - 1]
                pname = rsession.get_player_name(pid)
                ucheck = rsession.uno_callout(message.author.id)
                if ucheck[0]:
                    rsession.draw_card(pid, 2)
                    rsession.uno.pop(pid)
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel, vars(rsession)
                    )
                    log = 'User {} (ID: {}) called out {} (ID: {}) in #{} (ID: {})'.format(
                        message.author.name, message.author.id,
                        pname, pid,
                        message.channel.name, message.channel.id
                    )
                    logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                    ensure_future(
                        bot.send_message(
                            message.channel,
                            ':exclamation: | {} was called out for not saying UNO!'.format(
                                message.author.name
                            )
                        )
                    )
                    ouser = find(lambda u: u.id == pid, message.channel.server.members)
                    pmsg = (
                        ':notebook: | Your hand: **'
                        + ' '.join(rsession.hands[pid])
                        + '**'
                    )
                    ensure_future(
                        bot.send_message(ouser, pmsg)
                    )
                    return True
                else:
                    logwriter.write_log(ucheck[1], logstore.userlog)
                    ensure_future(
                        messenger.send_timed_message(
                            bot, 5, ucheck[2], message.channel
                        )
                    )
                    return False
            else:
                logwriter.write_log(ucheck[1], logstore.userlog)
                ensure_future(
                    messenger.send_timed_message(
                        bot, 5, 
                        ERR_WARNINGS['invalid_in'] + 'You must mention the player.',
                        message.channel
                    )
                )
                return False
        else:
            log = 'Tried to play UNO while not in the game.'
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5, 
                    ERR_WARNINGS['error'] + 'You need to join the game!',
                    message.channel
                )
            )
            return False
            """if len(session['hands'][message.author.id]) == 1:
                session['uno'].append(message.author.id)
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, session
                )
                log = 'User {} (ID: {}) has called UNO! in #{} (ID: {})'.format(
                    message.author.name, message.author.id,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                ensure_future(
                    bot.send_message(
                        message.channel,
                        ':exclamation: | **{}** has **UNO!**'.format(
                            message.author.name
                        )
                    )
                )
            else:
                if len(session['dwpile']) < 2:
                    session['dwpile'].extend(session['dcpile'][1:])
                    session['dcpile'] = [session['dcpile'][0]]
                    shuffle(session['dwpile'])
                session['hands'][message.author.id].extend(session['dwpile'][:2])
                session['dwpile'] = session['dwpile'][2:]
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, session
                )
                log = 'User {} (ID: {}) penalized for miscalling UNO! in #{} (ID: {})'.format(
                    message.author.name, message.author.id,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                ensure_future(
                    bot.send_message(
                        message.channel,
                        ':exclamation: | Miscalled UNO! You draw two cards.'
                    )
                )
        else:
            if (params.startswith('<@') and params.endswith('>')):
                pid = params[2:len(params) - 1]
                if pid in session['uno']:
                    ensure_future(
                        messenger.send_timed_message(
                            bot, 5,
                            ERR_WARNINGS['error'] + 'That player is safe.',
                            message.channel
                        )
                    )
                elif 't' + pid in session['uno']:
                    ensure_future(
                        messenger.send_timed_message(
                            bot, 5,
                            ERR_WARNINGS['error'] + 'That player is safe.',
                            message.channel
                        )
                    )
                else:
                    if len(session['dwpile']) < 2:
                        session['dwpile'].extend(session['dcpile'][1:])
                        session['dcpile'] = [session['dcpile'][0]]
                        shuffle(session['dwpile'])
                    session['hands'][pid].extend(session['dwpile'][:2])
                    session['dwpile'] = session['dwpile'][2:]
                    pname = get_player_name(session, pid)
                    updatequeries.update_guild_uno_session(
                        mongo, message.server, message.channel, session
                    )
                    log = 'User {} (ID: {}) penalized for not calling UNO! in #{} (ID: {})'.format(
                        pname, pid,
                        message.channel.name, message.channel.id
                    )
                    logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                    ensure_future(
                        bot.send_message(
                            message.channel,
                            ':exclamation: | **{}** was caught not calling UNO! They draw two cards.'.format(
                                pname
                            )
                        )
                    )"""

async def join_action(message, bot, mongo, logstore):
    if checkqueries.check_guild_uno_session(mongo, message.server, message.channel):

        go = True
        unosessions = findqueries.findall_guild_uno_session(mongo, message.server)
        cursession = None
        dmsg = ''
        for session in unosessions:

            # Check players in every running session
            # If a user is playing an UNO session, they must leave or finish that session
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
            if rsession.intermission:
                dmsg = ':door: | You\'ve joined the room!'
                await bot.send_message(message.channel, dmsg)
                if lpcount == 1:
                    dmsg = ':exclamation: | Game starting soon!...'
                    await bot.send_message(message.channel, dmsg)
                    await sleep(2)
                    session = findqueries.find_guild_uno_session(mongo, message.server, message.channel)[0]
                    rsession = UnoSession.restore_session(session)
                    if len(rsession.players) > 1:
                        rsession.start_session()
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
                                ':sparkles: | Top card: {}'.format(rsession.dcpile[0]),
                                ':mega: | Your move, <@{}>.'.format(rsession.turn[0])
                            ],
                            2,
                            message.channel
                        )
                        for pid in [p[0] for p in rsession.players]:
                            ouser = find(lambda u: u.id == pid, message.channel.server.members)
                            handmsg = (
                                ':notebook: | **Your hand:**\n\n'
                                + ' '.join(rsession.hands[pid])
                            )
                            await bot.send_message(ouser, handmsg)
                        return True
                    else:
                        rsession.stop_session()
                        updatequeries.update_guild_uno_session(
                            mongo, message.server, message.channel, vars(rsession)
                        )
                        dmsg = ':exclamation: | Game stopped prematurely...'
                        log = 'UNO session in #{} (ID: {}) was stopped.'.format(
                            message.channel.name, message.channel.id
                        )
                        logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                        await bot.send_message(message.channel, dmsg)
                        return False
        else:
            log = 'Tried to join an UNO session but was denied.'
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(bot, 5, dmsg, message.channel)
            )
            return False
            """
                for user in cursession['players']:
                    hand = cursession['dwpile'][0:6]
                    cursession['dwpile'] = cursession['dwpile'][6:]
                    cursession['hands'][user[0]] = hand
                cursession['dcpile'].append(cursession['dwpile'].pop(0))
                cursession['active'] = True
                cursession = set_first_turn(cursession['dcpile'][0], cursession)
                cardname = UNO_CARD_WORDS[cursession['dcpile'][0][0]]
                if cursession['dcpile'][0][1].isalpha():
                    cardname += ' ' + UNO_CARD_WORDS[cursession['dcpile'][0][1]]
                else:
                    cardname += ' ' + cursession['dcpile'][0][1]
                if len(cursession['dcpile'][0]) == 3:
                    cardname += ' ' + cursession['dcpile'][0][2]
                await messenger.send_interval_message(
                    bot,
                    [
                        ':bellhop: | UNO game is starting...!',
                        ':sparkles: | Top card: {}'.format(cursession['dcpile'][0])
                    ],
                    2,
                    message.channel
                )
                await sleep(2)
                updatequeries.update_guild_uno_session(
                    mongo, message.server, message.channel, cursession
                )
                for user in cursession['players']:
                    handmsg = (
                        'Your hand:\n\n**'
                        + ' '.join(cursession['hands'][0])
                        + '**'
                    )
                    ensure_future(
                        bot.send_message(
                            bot.get_user_info(user[0]),
                            handmsg
                        )
                    )
                log = 'UNO session in #{} (ID: {}) has started.'.format(message.channel.name, message.channel.id)
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                await bot.send_message(
                    message.channel,
                    ':mega: | Game start! Your move, <@{}>.'.format(cursession['turn'][0])
                )
            return True"""

    else:
        nsession = UnoSession(
            message.server.id, message.channel.id,
            [message.author.id, message.author.name], []
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

async def quit_action(message, bot, mongo, params, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        rsession = UnoSession.restore_session(session)
        if rsession.check_player_presence:
            rsession.remove_player(message.author.id)
            updatequeries.update_guild_uno_session(
                mongo, message.server, message.channel, vars(rsession)
            )
            log = 'Left UNO session in #{} (ID: {}).'.format(
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            ensure_future(
                bot.send_message(
                    message.channel,
                    ':walking: | You have left the UNO game!'
                )
            )
            return True
        else:
            log = 'Tried to play UNO while not in the game.'
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5, 
                    ERR_WARNINGS['error'] + 'You need to join the game!',
                    message.channel
                )
            )
            return False

def get_active_session(message, bot, mongo, logstore):

    """Retrieves an active session in a channel from MongoDB.

    :param message: Discord message reference.

    :param bot: Discord bot client.

    :param mongo: Mongo client connection.

    :param logstore: Object containing log paths.

    :type message: discord.Message

    :type bot: discord.Client

    :type mongo: pymongo.MongoClient

    :type logstore: LogStore

    :returns: An active UNO session dict or None.

    :rtype: dict or None
    """

    find = findqueries.find_guild_uno_session(
        mongo, message.server, message.channel
    )
    if find.count(True) > 0:
        if find[0]['active']:
            return find[0]
        else:
            log = 'Tried to play on an inactive UNO session.'
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5,
                    (ERR_WARNINGS['error']
                        + 'Game has not started yet!'),
                    message.channel
                )
            )
    else:
        log = 'Tried to play UNO while there is no running session.'
        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(
                bot, 5,
                (ERR_WARNINGS['error']
                    + 'There is no running UNO session here. Start one!'),
                message.channel
            )
        )
    return None

def get_player_name(session, pid) -> str:

    """Retrieves the player name associated with their id
    in the given UNO game session.

    Args:
        session (dict): UNO game session
        pid (str): Player ID string

    Returns:
        Name of the player associated with the id.
    """

    pidlist = [player[0] for player in session['players']]
    if pid in pidlist:
        return session['players'][pidlist.index(pid)][0]
    return None

def get_player_index(session: dict) -> int:

    for user in session['players']:
        if session['turn'][0] in user:
            return session['players'].index(user)
    return None

def get_next_player_index(session: dict, skip: bool = False) -> int:

    pindex = get_player_index(session)

    if not skip:
        if session['direction'] == 'r':
            if pindex == len(session['players']) - 1:
                return 0
            else:
                return pindex + 1
        else:
            if pindex == 0:
                return len(session['players'] - 1)
            else:
                return pindex - 1
    else:
        if session['direction'] == 'r':
            if pindex == len(session['players']) - 2:
                return 0
            elif pindex == len(session['players']) - 1:
                return 1
            else:
                return pindex + 2
        else:
            if pindex == 0:
                return len(session['players']) - 2
            elif pindex == 1:
                return len(session['players']) - 1
            else:
                return pindex - 2

def look_up_card(search: str) -> str:

    """Finds a card with a given search string.

    Args:
        search (str): Search string

    Returns:
        An abbreviated card name.
    """

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
                return None
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
            else:
                return None

def set_first_turn(card, session):

    """Sets the first turn of an UNO session.

    :param card: First card shown on the discard pile.

    :param session: The starting UNO session.

    :type card: str

    :type session: dict

    :returns: An updated UNO session dict.

    :rtype: dict
    """

    # If a wild draw four is the first card, deck is reshuffled
    if card == 'WD4':
        session['dwpile'].append(session['dcpile'].pop())
        shuffle(session['dwpile'])
        session['dcpile'].append(session['dwpile'].pop(0))
        return set_first_turn(card, session)

    # If a regular wild is the first card, starting player must pick a starting color
    elif card == 'W':
        session['turn'] = [session['players'][0][0], 'C']

    # If draw 2 is the first card, starting player must start by drawing 2 cards
    elif 'D2' in card:
        session['hands'][session['players'][0][0]].extend(session['dwpile'][:2])
        session['dwpile'] = session['dwpile'][2:]
        session['turn'] = [session['players'][1][0], 'P']

    # If skip is the first card, skip starting player
    elif 'S' in card:
        session['turn'] = [session['players'][1][0], 'P']

    # If reverse is the first card, starting direction is left instead of right
    elif 'r' in card:
        session['direction'] = 'l'
        session['turn'] = [session['players'][len(session['players']) - 1][0], 'P']

    else:
        session['turn'] = [session['players'][0][0], 'P']

    return session

def set_next_turn(card, session):

    """Sets the next turn of an UNO session.

    :param card: Top card on the discard pile.

    :param session: The running UNO session.

    :type card: str

    :type session: dict

    :returns: An updated UNO session dict.

    :rtype: dict
    """

    index = get_player_index(session)

    # Wild Draw 4
    if card == 'WD4':
        session['turn'] = [session['players'][index][0], 'CD4']

    # Wild Card
    elif card == 'W':
        session['turn'] = [session['players'][index][0], 'C']

    # Any Draw 2
    elif 'D2' in card:
        if session['direction'] == 'r':
            if index == len(session['players']) - 1:
                session['turn'] = [session['players'][0][0], 'D2']
            else:
                session['turn'] = [session['players'][index + 1][0], 'D2']
        else:
            if index == 0:
                session['turn'] = [session['players'][len(session['players'] - 1)][0], 'D2']
            else:
                session['turn'] = [session['players'][index - 1][0], 'D2']
        

    # Any Skip
    elif 'S' in card:
        if session['direction'] == 'r':
            if index == len(session['players']) - 2:
                session['turn'] = [session['players'][0][0], 'P']
            elif index == len(session['players']) - 1:
                session['turn'] = [session['players'][1][0], 'P']
            else:
                session['turn'] = [session['players'][index + 2][0], 'P']
        else:
            if index == 0:
                session['turn'] = [session['players'][len(session['players']) - 2][0], 'P']
            elif index == 1:
                session['turn'] = [session['players'][len(session['players']) - 1][0], 'P']
            else:
                session['turn'] = [session['players'][index - 2][0], 'P']

    # Any Reverse
    elif 'r' in card:
        if session['direction'] == 'r':
            session['direction'] = 'l'
            if len(session['players']) > 2:
                if index == 0:
                    session['turn'] = [session['players'][len(session['players'] - 1)][0], 'P']
                else:
                    session['turn'] = [session['players'][index - 1][0], 'P']
        else:
            session['direction'] = 'r'
            if len(session['players']) > 2:
                if index == len(session['players']) - 1:
                    session['turn'] = [session['players'][0][0], 'P']
                else:
                    session['turn'] = [session['players'][index + 1][0], 'P']

    # Any Standard
    else:
        session['turn'] = [session['players'][0][0], 'P']

    return session

def check_player_turn(message, bot, logstore, session, turn):

    found = False
    for user in session['players']:
        if message.author.id in user:
            found = True
            break

    if found:
        if message.author.id in session['turn']:
            if session['turn'][1][0] in turn:
                return True
            elif 'P' in session['turn'][1]:
                log = 'Tried to do a different action on play turn.'
                logwriter.write_log(log, logstore.userlog)
                ensure_future(
                    messenger.send_timed_message(
                        bot, 5,
                        (ERR_WARNINGS['no_act'] 
                            + 'You need to play a card!'),
                        message.channel
                    )
                )
            elif 'C' in session['turn'][1]:
                log = 'Tried to do a different action on color turn.'
                logwriter.write_log(log, logstore.userlog)
                ensure_future(
                    messenger.send_timed_message(
                        bot, 5,
                        (ERR_WARNINGS['no_act'] 
                            + 'You need to choose a card color!'),
                        message.channel
                    )
                )
            elif 'D' in session['turn'][1]:
                log = 'Tried to do a different action on draw turn.'
                logwriter.write_log(log, logstore.userlog)
                ensure_future(
                    messenger.send_timed_message(
                        bot, 5,
                        (ERR_WARNINGS['no_act']
                            + 'You need to draw cards!'),
                        message.channel
                    )
                )
        else:
            log = 'Tried to play UNO out of turn.'
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5,
                    ERR_WARNINGS['no_act'] + 'It\'s not your turn!',
                    message.channel
                )
            )
    else:
        log = 'Tried to play UNO while not in a running session.'
        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(
                bot, 5,
                (ERR_WARNINGS['error']
                    + 'You\'re not in this UNO session. Join in!'),
                message.channel
            )
        )
    return False

def check_card_match(card, topcard):

    """Sets the next turn of an UNO session.

    :param card: A given card to try and match the top card.

    :param topcard: The card on the discard pile to match.

    :type card: str

    :type topcard: str

    :returns: A bool indicating if a match is made.

    :rtype: bool
    """

    if card in ['W', 'WD4']:
        return True

    elif card[0] in topcard[0]:
        return True

    elif card[1] in topcard[1]:
        return True

    else:
        return False