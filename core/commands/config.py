"""Contains core command configuration settings"""

ERR_WARNINGS = {
    'invalid_in': ':no_entry_sign: Invalid input. ',
    'ambig': ':no_entry_sign: Ambiguous input. ',
    'no_perm': ':no_entry_sign: You don\'t have the necessary permissions. ',
    'no_act': ':no_entry_sign: Can\'t do that. ',
    'error': ':no_entry_sign: '
}

# Listen command
LISTEN_KEYWORDS = ('listen', 'lis')
LISTEN_COOLDOWN = 1

# Ignore command
IGNORE_KEYWORDS = ('ignore', 'ig')
IGNORE_COOLDOWN = 1

# Prefix command
PREFIX_KEYWORDS = ('prefix', 'pre')
PREFIX_COOLDOWN = 1

# UNO command
UNO_KEYWORDS = ('uno', 'uno!')
UNO_COOLDOWN = 1

# Help command
HELP_KEYWORDS = ('help', '?')
HELP_COOLDOWN = 2