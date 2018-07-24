"""
Writes log entries during bot operation.

Records user command usage, server changes, errors, and more.
"""

from os import path
from datetime import datetime

FUNC_ERR_LOG = path.dirname(path.dirname(__file__)) + '\\logs\\error\\logwriter.err'

def write_log(log, *paths):

    '''
    Writes a log entry with given absolute path(s).
    
    Returns True if execution was successful.

    :param `log`: - log entry string

    :param `paths`: - file path(s) to write to
    '''

    timestamp = datetime.now().strftime('[%b-%d-%Y %H:%M:%S] ')
    try:
        for path in paths:
            logfile = open(path, 'a+', encoding='utf-8')
            logfile.write(timestamp + log + '\n')
            logfile.close()
        print(timestamp + log)
        return True
    except IOError as err:
        errormsg = 'Error occurred: IOError'
            + '\nCould not open file at: {}'.format(path)
            + '\n{}'.format(err))
        try:
            logfile = open(FUNC_ERR_LOG, 'a+', encoding='utf-8')
            logfile.write(timestamp + log + '\n')
            logfile.close()
        except:
            print('Could not write to error log.')
        finally:
            print(timestamp + errormsg)
            return False
    except UnicodeEncodeError as err:
        errormsg = 'Error occurred: UnicodeEncodeError'
            + '\n\tCould not write: {}'.format(log)
            + '\n\t{}'.format(err))
        try:
            logfile = open(FUNC_ERR_LOG, 'a+', encoding='utf-8')
            logfile.write(timestamp + log + '\n')
            logfile.close()
        except:
            print('Could not write to error log.')
        finally:
            print(timestamp + errormsg)
            return False