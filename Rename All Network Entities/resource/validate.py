"""
Simple script to obtain user input and validate it immediately
"""


def integer(valid_range):
    """
    Requests and validates an integer against a specified range
    :param valid_range: integer value that checks for
                        input between 0 and valid_range
    :return: returns validated user input
    """
    valid = False
    user_input = ''
    while not valid:
        user_input = raw_input('\t> ')
        try:
            user_input = int(user_input)
            if 0 < user_input <= valid_range:
                valid = True
            else:
                print 'Invalid Selection'
        except IOError as io_error:
            valid = False
            print '\n{}\nInvalid Input.\nPlease enter numbers only'.format(io_error)
        except ValueError as value_error:
            valid = False
            print '\n{}\nInvalid Input.\nPlease enter a number'.format(value_error)
    return user_input


def confirmation(confirm='confirm'):
    """
    Requests and validates a confirmation command
    :param confirm: The value that should be entered when the user wishes to confirm
    default: 'confirm'
    :return: Boolean of whether or not user has confirmed
    """
    valid = False
    while not valid:
        user_input = raw_input('\t> ')
        if user_input.lower() == confirm.lower():
            valid = True
            return True
        return False


def yes_no():
    """
    Requests and validates a Y/N answer from the user
    :return: Boolean Y/y = True
                    N/n = False
    """
    valid = False
    while not valid:
        user_input = raw_input('\t> ')
        if user_input.lower() == 'y':
            valid = True
            return True
        elif user_input.lower() == 'n':
            valid = True
            return False
        else:
            print 'Invalid Selection. Please enter "y" or "n".'
