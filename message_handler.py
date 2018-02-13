from time import sleep
from pprint import pprint
from scraper import User


def handle(msg, current_user):
    command = msg.split()[0]
    if command[0] == '/':
        r = current_user.perform_action(command[1:])
        print r
        return r
    else:
        return easter(msg)


def easter(msg):
    print "in easter"
    return 'Please enter a valid command'
