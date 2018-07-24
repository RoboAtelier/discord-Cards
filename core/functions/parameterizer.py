"""Returns a list of parameters with a given string separated with specific delimeters"""

import re

def parameterize(paramstring):
    """
    Converts a string into a list of parameters by splitting on specific delimiters:

    `" "`, `,`, `;`, ` ` - double quotations, commas, semi-colons, and spaces

    Delimiters are checked in the given order.

    Returns a list of string parameters.

    :param: `paramstring` - string to process
    """
 
    if re.search(r'"(.+?)"', paramstring):
        # Capture all parts of the string that are in between quotation marks

        # Find words that are in quotes
        return re.findall(r'"(.+?)"', paramstring)
    elif re.search(';', paramstring):
        # Capture all parts of the string that are not preceded by whitespace or semicolons
        # Optionally can have repeating group patterns of whitespace and characters respectively
        # Capture group must be followed with whitespace and a semicolon respectively

        # Find words or phrases separated by semicolon
        return re.findall(r'[^\s;]+(?:\s+[^\s;]+)*(?=\s*;)', paramstring + ';')
    elif re.search(',', paramstring):
        # Capture all parts of the string that are not preceded by whitespace or commas
        # Optionally can have repeating group patterns of whitespace and characters respectively
        # Capture group must be followed with whitespace and a comma respectively

        # Find words or phrases separated by commas
        return re.findall(r'[^\s,]+(?:\s+[^\s,]+)*(?=\s*,)', paramstring + ',')
    else:
        # Capture all parts of the string that are not whitespace

        # Find words that are separated by spaces
        return re.findall(r'[^\s]+', paramstring)
