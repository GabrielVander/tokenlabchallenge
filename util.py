import string
import random
import sys

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def print_to_console(x):
    print('\n\n-' + str(x) + '-\n\n', file=sys.stdout)


