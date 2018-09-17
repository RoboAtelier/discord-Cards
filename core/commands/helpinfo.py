

from discord import Embed

# !!!
# Administrative commands
# !!!

# Listen help info
LISTEN_INFO_EMBED = Embed(
    **{
        'title': '__listen__',
        'description': 'Enables a channel to listen for this bot\'s commands.'
            + '\nRequired by all servers to be used on a channel.',
        'colour': 0x3498db
    }
)
LISTEN_INFO_EMBED.add_field(
    name='Options',
    value='`(no option)` - adds current channel as a listening channel'
    + '\n`-m`, `main` - changes an alt channel into the main channel',
    inline=False
)
LISTEN_INFO_EMBED.add_field(
    name='Usage',
    value='`cclisten (option)`'
    + '\n*(Optional)*',
    inline=False
)
LISTEN_INFO_EMBED.add_field(
    name='Examples',
    value='`cclisten` - adds current channel as a listening channel'
    + '\n`cclisten main` - if current channel is an alt, it will now be the main channel',
    inline=False
)
LISTEN_INFO_EMBED.add_field(
    name='Aliases',
    value='`lis`',
    inline=False
)
LISTEN_INFO = ('Enables a channel to listen for this bot\'s commands.'
    + '\nRequired by all servers to be used on a channel.'
    + '\n\n**Options:**'
    + '\n`no option` - adds current channel as a listening channel'
    + '\n`-m`, `main` - changes an alt channel into the main channel'
    + '\n\n**Usage:**'
    + '\n`cclisten (option)`'
    + '\n*(Optional)*'
    + '\n\n**Examples:**'
    + '\n`cclisten` - adds current channel as a listening channel'
    + ' `cclisten main` - if current channel is an alt, it will now be the main channel'
    + '\n\n**Aliases:**'
    + '\n`lis`')

# Ignore help info
IGNORE_INFO_EMBED = Embed(
    **{
        'title': '__ignore__',
        'description': 'Tells the bot to no longer listen for commmands on a channel.',
        'colour': 0x3498db
    }
)
IGNORE_INFO_EMBED.add_field(
    name='Usage',
    value='`ccignore`',
    inline=False
)
IGNORE_INFO_EMBED.add_field(
    name='Example',
    value='`ccignore` - if current channel is an alt, it will no longer be an alt.',
    inline=False
)
IGNORE_INFO_EMBED.add_field(
    name='Aliases',
    value='`ig`',
    inline=False
)
IGNORE_INFO = ('Tells the bot to no longer listen for commmands on a channel.'
    + '\n\n**Usage:**'
    + '\n`ccignore`'
    + '\n\n**Example:**'
    + '\n`ccignore` - if current channel is an alt, it will no longer be an alt.'
    + '\n\n**Aliases:**'
    + '\n`ig`')

# Prefix help info
PREFIX_INFO_EMBED = Embed(
    **{
        'title': '__prefix__',
        'description': ('Changes the command prefix for this particular server.'
            + '\nUseful if the current command prefix interferes with another bot.'),
        'colour': 0x3498db
    }
)
PREFIX_INFO_EMBED.add_field(
    name='Usage',
    value='`ccprefix [new prefix]`'
    + '\n**[Required]**',
    inline=False
)
PREFIX_INFO_EMBED.add_field(
    name='Example',
    value='`ccprefix /` - changes prefix to \'/\'',
    inline=False
)
PREFIX_INFO_EMBED.add_field(
    name='Aliases',
    value='`pre`',
    inline=False
)
PREFIX_INFO = ('Changes the command prefix for this particular server.'
    + '\nUseful if the current command prefix interferes with another bot.'
    + '\n\n**Usage:**'
    + '\n`ccprefix [new prefix]`'
    + '\n**[Required]**'
    + '\n\n**Example:**'
    + '\n`ccprefix /` - changes prefix to \'/\''
    + '\n\n**Aliases:**'
    + '\n`pre`')

# !!!
# Game commands
# !!!

# UNO help info
UNO_INFO_EMBED = Embed(
    **{
        'title': '__uno__',
        'description': 'Command to play UNO.',
        'colour': 0x3498db
    }
)
UNO_INFO_EMBED.add_field(
    name='Options',
    value='`(no option)`, `-j`, `join` - joins an UNO game in the channel'
    + '\n`-l`, `-q`, `leave`, `quit` - leaves an UNO game in the channel'
    + '\n`-p`, `play`, `pick` - plays a card from your hand'
    + '\n`-d`, `draw` - draws cards from the draw pile'
    + '\n`-k`, `keep` - keeps a drawn card (only for single draws)'
    + '\n`-C`, `color` - chooses a color for a played wild card'
    + '\n`-t`, `topcard` - checks the topmost card on the discard pile'
    + '\n`-h`, `-c`, `hand`, `cards` - checks your current hand'
    + '\n`-P`, `peek` - looks at the number of cards from each player\'s hand'
    + '\n`!` - calls UNO or call out someone for not saying UNO',
    inline=False
)
UNO_INFO_EMBED.add_field(
    name='Usage',
    value='`ccuno (option) (parameters)`'
    + '\n*(Optional)*',
    inline=False
)
UNO_INFO_EMBED.add_field(
    name='Examples',
    value='`ccuno` - joins an UNO game in a valid channel'
    + '\n`ccuno play r8` - plays a "Red 8" if it\'s the user\'s turn'
    + '\n`ccuno color blue` - changes the color of the recently played wild card to blue'
    + '\n`ccuno!` - calls UNO! to avoid call outs when having one card left'
    + '\n`ccuno! @User` - calls out User for not saying UNO!',
    inline=False
)
UNO_INFO = ('Command to play UNO.'
    + '\n**Options:**'
    + '\n`(no option)`, `-j`, `join` - joins an UNO game in the channel'
    + '\n`-l`, `-q`, `leave`, `quit` - leaves an UNO game in the channel'
    + '\n`-p`, `play`, `pick` - plays a card from your hand'
    + '\n`-d`, `draw` - draws cards from the draw pile'
    + '\n`-k`, `keep` - keeps a drawn card (only for single draws)'
    + '\n`-C`, `color` - chooses a color for a played wild card'
    + '\n`-t`, `topcard` - checks the topmost card on the discard pile'
    + '\n`-h`, `-c`, `hand`, `cards` - checks your current hand'
    + '\n`-P`, `peek` - looks at the number of cards from each player\'s hand'
    + '\n`!` - calls UNO or call out someone for not saying UNO'
    + '\n\n**Usage:**'
    + '\n`ccuno (option) (parameters)`'
    + '\n*(Optional)*'
    + '\n\n**Examples:**'
    + '\n`ccuno` - joins an UNO game in a valid channel'
    + '\n`ccuno play r8` - plays a "Red 8" if it\'s the user\'s turn'
    + '\n`ccuno color blue` - changes the color of the recently played wild card to blue'
    + '\n`ccuno!` - calls UNO! to avoid call outs when having one card left'
    + '\n`ccuno! @User` - calls out User for not saying UNO!'
    + '\n\n**Aliases:**'
    + '\n`pre`')