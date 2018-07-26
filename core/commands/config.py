"""Contains core command configuration settings"""

from discord import Embed

ERR_WARNINGS = {
    'invalid_in': ':exclamation: | Invalid input. ',
    'ambig': ':exclamation: | Ambiguous input. ',
    'no_perm': 'no_entry_sign: | You don\'t have the necessary  permissions. ',
    'exception': ':exclamation: | ',
    'error': ':no_entry_sign: | '
}

# Register command
register_keywords = ['register', 'reg']
register_info_embed = Embed(
    **{
        'title': '__register__',
        'description': ('Registers the server to allow usage of bot commands.'
            + '\nRequired by all servers.'),
        'colour': 0x3498db
    }
)
register_info_embed.add_field(
    name='Options',
    value='`no option` - changes primary channel (use command on a new channel)'
    + '\n`-a` - adds an alt channel'
    + '\n`-d` - deletes an alt channel'
    + '\n(Mutually Exclusive)',
    inline=False
)
register_info_embed.add_field(
    name='Usage',
    value='`,register (option (channels))`'
    + '\n*(Optional)*',
    inline=False
)
register_info_embed.add_field(
    name='Examples',
    value='`,register` - registers the server, or changes primary channel'
    + '\n`,register -a bots` - sets channel \'bots\' as an alt channel'
    + '\n`,register -d lobby` - sets channel \'lobby\' to no longer be an alt channel',
    inline=False
)
register_info_embed.add_field(
    name='Aliases',
    value='`reg`',
    inline=False
)
register_info = ('Registers the server to allow usage of bot commands.'
    + '\nRequired by all servers.'
    + '\n\nOptions: `no option` - change primary channel (use command on a new channel),'
    + '\n`-a` - adds an alt channel, `-d` - deletes an alt channel'
    + '\n(Mutually Exclusive)'
    + '\n\nUsage: `,register (option (channels))`'
    + '\n*(Optional)*'
    + '\n\nExamples: `,register` - registers the server, or changes primary channel,'
    + ' `,register -a lobby` - registers a new alt channel \'lobby\''
    + '\n\nAliases: `reg`') 

# Prefix command
prefix_keywords = ['prefix', 'pre']
prefix_info_embed = Embed(
    **{
        'title': '__prefix__',
        'description': ('Changes the command prefix for this particular server.'
            + '\nUseful if the current command prefix interferes with another bot.'),
        'colour': 0x3498db
    }
)
prefix_info_embed.add_field(
    name='Usage',
    value='`,prefix [new prefix]`'
    + '\n**[Required]**',
    inline=False
)
prefix_info_embed.add_field(
    name='Example',
    value='`,prefix /` - changes prefix to \'/\'',
    inline=False
)
prefix_info_embed.add_field(
    name='Aliases',
    value='`pre`',
    inline=False
)
prefix_info = ('Changes the command prefix for this particular server.'
    + '\nUseful if the current command prefix interferes with another bot.'
    + '\n\nUsage: `,prefix [new prefix]`'
    + '\n**[Required]**'
    + '\n\nExample: `,prefix /` - changes prefix to \'/\''
    + '\n\nAliases: `pre`')