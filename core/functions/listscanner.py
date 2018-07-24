"""Scans through a list to find a specific item contained within"""

def find_item(searchlist, search):
    """
    Finds an item inside a list with a given search string.
    Checks by exact name or if a name starts with the search string.

    Returns an item if found or None if not.
    Returns 'ambig' string if a search input finds two items.

    :param `searchlist`: - list to scan

    :param `search`: - search string
    """

    found = None
    for item in searchlist:
        if item == search:
            return item
        elif item.startswith(search):
            if found:
                return 'ambig'
            else:
                found = item
    return found

def find_channel_by_name(channels, search):
    """
    Finds a discord channel by name.
    Checks by exact name or if a name starts with the search string.

    Returns a discord channel if found or None if not.
    Returns 'ambig' string if a search input finds two channels.

    :param `channels`: - list of discord channels

    :param `search`: - search string
    """

    found = None
    search = search.replace(' ', '-')
    for channel in channels:
        if channel.name == search:
            return channel
        elif channel.name.startswith(search):
            if found:
                return 'ambig'
            else:
                found = channel
    return found

def find_channel_by_id(channels, search):
    """
    Finds a discord channel by numerical id.

    Returns a discord channel if found or None if not.

    :param `channels`: - list of discord channels

    :param `search`: - search string
    """

    for channel in channels:
        if channel.id == search:
            return channel
    return None