"""
`uno` command:

UNO game module.
Contains the necessary components to run an UNO game session.
"""

from asyncio import ensure_future, sleep
from random import shuffle
from . import config
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

UNO_SESSION = {
    'guild_id': '',
    'channel_id': '',
    'active': False,
    'intermission': False,
    'mode': 'classic',
    'players': [],
    'hands': {},
    'dwpile': [],
    'dcpile': [],
    'direction': 'r',
    'turn': [],
    'uno': {}
}

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

    class UnoSession:

        def __init__(self, active, mode, players, hands, dwpile, dcpile, direction, turn):
            self.active = active
            self.mode = mode
            self.players = players
            self.hands = hands
            self.dwpile = dwpile
            self.dcpile = dcpile
            self.direction = direction
            self.turn = turn

        def execute_turn(self, action):
            if action == 'draw':
                self.hands[self.turn].append(self.dwpile[0])
                self.dwpile.pop(0)
                if len(self.dwpile) == 0:
                    new_dwpile = self.dcpile.copy()
                    topcard = self.dcpile[0]
                    new_dwpile.pop(0)
                    shuffle(new_dwpile)
                    self.dwpile = new_dwpile
                    self.dcpile = [topcard]
            if self.mode == 'classic':
                pos = self.players.index(self.turn)
                if self.direction == 'left':
                    if pos == 0:
                        self.turn = self.players[len(self.players) - 1]
                    else:
                        self.turn = self.players[pos - 1]
                elif self.direction == 'right':
                    if pos == len(self.players) - 1:
                        self.turn = self.players[0]
                    else:
                        self.turn = self.players[pos + 1]

    find = findqueries.find_channel_games(mongo, message.server, message.channel)
    if find.count(True) > 0:
        games = find[0]['channel_games']
        if ('uno' in games or len(games) == 0):
            csplit = content.split(' ', 1)
            option = csplit[0]
            params = csplit[1].lower()
            if ('make'.startswith(option) or option in ['-m']):
                if checkqueries.check_guild_uno_session(mongo, message.server, message.channel):

                    log = 'Tried to start UNO session while one is already running.'
                    logwriter.write_log(log, logstore.userlog)
                    ensure_future(
                        messenger.send_timed_message(
                            bot, 5,
                            config.ERR_WARNINGS['error'] + 'There\'s already an ongoing game here! Join it instead.',
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
                    return True
            elif ('join'.startswith(option) or option in ['-j', 'jn']):
                if checkqueries.check_guild_uno_session(mongo, message.server, message.channel):

                    go = True
                    unosessions = findqueries.findall_guild_uno_session(mongo, message.server)
                    cursession = None
                    for session in unosessions:

                        # Check players in every running session
                        # If a user is playing an UNO session, they must leave or finish that session
                        if message.channel.id == session['channel_id']:
                            if len(session['players']) == 10:
                                ensure_future(
                                    messenger.send_timed_message(
                                        bot, 5,
                                        config.ERR_WARNINGS['error'] + 'This session is full!',
                                        message.channel
                                    )
                                )
                                go = False
                            else:
                                cursession = session.copy()
                        for user in session['players']:
                            if message.author.id in user:
                                ensure_future(
                                    messenger.send_timed_message(
                                        bot, 5,
                                        config.ERR_WARNINGS['no_act'] + 'You\'re currently playing an UNO session in <#{}>'.format(
                                            session['channel_id']),
                                        message.channel
                                    )
                                )
                                go = False
                                break
                        if not go:
                            break
                    if go:
                        cursession['players'].append([message.author.id, message.author.name])
                        log = 'User {} (ID: {}) has joined an UNO session in #{} (ID: {}).'.format(
                            message.author.name, message.author.id, message.channel.name, message.channel.id)
                        logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                        if cursession['intermission']:
                            ensure_future(
                                messenger.send_timed_message(
                                    bot, 5,
                                    ':door: | You\'ve joined the session! Please wait until the next round starts.',
                                    message.channel))
                        elif not cursession['active'] and len(cursession['players']) >= 2:
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
                                mongo, message.server, message.channel, cursession)
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
                        return True
                    else:
                        log = 'Tried to join an UNO session but was denied.'
                        logwriter.write_log(log, logstore.userlog)
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
                    ensure_future(
                        bot.send_message(
                            message.channel,
                            ':door: | UNO room created! Game will start when at least one other person joins in.'
                        )
                    )
                    return True

            elif ('play'.startswith(option) or option in ['-p']):
                return await play_action(message, bot, mongo, params, logstore)

            elif ('color'.startswith(option) or option in ['-c']):
                return await color_action(message, bot, mongo, params, logstore)

            elif ('draw'.startswith(option) or option in ['-d']):
                return await draw_action(message, bot, mongo, params, logstore)

            elif ('keep'.startswith(option) or option in ['-k']):
                return await keep_action(message, bot, mongo, logstore)

        else:
            log = 'Tried to start UNO session while being in a non-UNO channel.'
            logwriter.write_log(log, logstore.userlog)
            ensure_future(
                messenger.send_timed_message(
                    bot, 5,
                    config.ERR_WARNINGS['error'] + 'You cannot play UNO here.',
                    message.channel
                )
            )
            return True

async def play_action(message, bot, mongo, params, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        if check_player_turn(message, bot, logstore, session, 'Pp'):

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
                                (config.ERR_WARNINGS['error']
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
                            updatequeries.update_guild_uno_session(session)
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
                                    (config.ERR_WARNINGS['error']
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
                                updatequeries.update_guild_uno_session(session)
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
                                        (config.ERR_WARNINGS['error']
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
                                    (config.ERR_WARNINGS['error']
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
                            updatequeries.update_guild_uno_session(session)
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
                            (config.ERR_WARNINGS['error']
                                + 'That is not a match with the top card.'),
                            message.channel
                        )
                    )
                    return False

async def color_action(message, bot, mongo, params, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        if check_player_turn(message, bot, logstore, session, 'C'):
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
                        (config.ERR_WARNINGS['error']
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
            updatequeries.update_guild_uno_session(session)
            log = 'User {} (ID: {}) chose color {} in #{} (ID: {})'.format(
                message.author.name, message.author.id, color,
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            return True

async def draw_action(message, bot, mongo, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        if check_player_turn(message, bot, logstore, session, 'DP'):
            if 'D' in session['turn'][1]:
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
                updatequeries.update_guild_uno_session(session)
                log = 'User {} (ID: {}) drew {} cards in #{} (ID: {})'.format(
                    message.author.name, message.author.id, draw,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                return True
            elif 'P' in session['turn'][1]:
                index = get_player_index(session)
                if len(session['dwpile']) < int(draw):
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
                updatequeries.update_guild_uno_session(session)
                log = 'User {} (ID: {}) drew a card in #{} (ID: {})'.format(
                    message.author.name, message.author.id,
                    message.channel.name, message.channel.id
                )
                logwriter.write_log(log, logstore.userlog, logstore.guildlog)
                return True

async def keep_action(message, bot, mongo, logstore):
    """(async) Method called when using the `keep` UNO action

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
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        if check_player_turn(message, bot, logstore, session, 'p'):
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
                + ' '.join(cursession['hands'][0])
                + '**'
            )
            ensure_future(
                bot.send_message(
                    message.author,
                    handmsg
                )
            )
            updatequeries.update_guild_uno_session(session)
            log = 'User {} (ID: {}) kept their drawn card in #{} (ID: {})'.format(
                message.author.name, message.author.id,
                message.channel.name, message.channel.id
            )
            logwriter.write_log(log, logstore.userlog, logstore.guildlog)
            return True
    return False

async def uno_action(message, bot, mongo, logstore):
    session = get_active_session(message, bot, mongo, logstore) 
    if session:
        if check_player_turn(message, bot, logstore, session, 'p'):

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
                    (config.ERR_WARNINGS['error']
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
                (config.ERR_WARNINGS['error']
                    + 'There is no running UNO session here. Start one!'),
                message.channel
            )
        )
    return None

def get_player_index(session):

    for user in session['players']:
        if session['turn'][0] in user:
            return session['players'].index(user)
    return None

def get_next_player_index(session, skip=False):

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

def look_up_card(search):

    """Finds a card with a given search string.

    :param search: A string to use, find, and return a valid card name.

    :type search: str

    :returns: A card name string or None.

    :rtype: str or None
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
            if index == 0:
                session['turn'] = [session['players'][len(session['players'] - 1)][0], 'P']
            else:
                session['turn'] = [session['players'][index - 1][0], 'P']
        else:
            session['direction'] = 'r'
            if index == len(session['players']) - 1:
                session['turn'] = [session['players'][0][0], 'P']
            else:
                session['turn'] = [session['players'][index + 1][0], 'P']

    # Any Standard
    else:
        session['turn'] = [session['players'][0][0], 'P']

    return session

def check_uno_status(message, bot, logstore, session):

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
                        (config.ERR_WARNINGS['no_act'] 
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
                        (config.ERR_WARNINGS['no_act'] 
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
                        (config.ERR_WARNINGS['no_act']
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
                    config.ERR_WARNINGS['no_act'] + 'It\'s not your turn!',
                    message.channel
                )
            )
    else:
        log = 'Tried to play UNO while not in a running session.'
        logwriter.write_log(log, logstore.userlog)
        ensure_future(
            messenger.send_timed_message(
                bot, 5,
                (config.ERR_WARNINGS['error']
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