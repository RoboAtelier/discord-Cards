"""Contains core command configuration settings"""

from discord import Embed

ERR_WARNINGS = {
    'invalid_in': ':error: | Invalid input. ',
    'ambig': ':error: | Ambiguous input. ',
    'no_perm': ':no_entry_sign: | You don\'t have the necessary permissions. ',
    'no_act': ':no_entry_sign: | Can\'t do that. ',
    'exclamation': ':exclamation: | ',
    'error': ':no_entry_sign: | '
}

# Listen command
LISTEN_KEYWORDS = ('listen', 'lis')
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
    value='`no option` - adds current channel as a listening channel'
    + '\n`-m **OR** main` - changes an alt channel into the main channel',
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
    + '\n\nOptions: `no option` - adds current channel as a listening channel'
    + '\n`-m **OR** main` - changes an alt channel into the main channel'
    + '\n\nUsage: `cclisten (option)`'
    + '\n*(Optional)*'
    + '\n\nExamples: `cclisten` - adds current channel as a listening channel'
    + ' `cclisten main` - if current channel is an alt, it will now be the main channel'
    + '\n\nAliases: `reg`')

# Ignore commands
IGNORE_KEYWORDS = ('ignore', 'ig')
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
    + '\n\nUsage: `ccignore`'
    + '\n\nExample: `ccignore` - if current channel is an alt, it will no longer be an alt.'
    + '\n\nAliases: `ig`')

# Prefix command
PREFIX_KEYWORDS = ('prefix', 'pre')
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
    + '\n\nUsage: `ccprefix [new prefix]`'
    + '\n**[Required]**'
    + '\n\nExample: `ccprefix /` - changes prefix to \'/\''
    + '\n\nAliases: `pre`')