from time import sleep
from pprint import pprint
from scraper import User


def handle(msg, current_user):
    # if current_user is None:
    #     current_user = User()
    # print current_user.current_tab
    # if current_user.current_tab == "need_username":
    #     current_user.current_tab = "need_password"
    #     return 'Please enter your username', current_user
    # elif current_user.current_tab == "need_password":
    #     current_user.username = msg
    #     current_user.current_tab = "received_details"
    #     return 'Please enter your password (It\'s not visible to the bot)', current_user
    # elif current_user.current_tab == "received_details":
    #     current_user.password = msg
    #     return current_user.begin_session()
    # else:
    print msg
    command = msg.split()[0]
    if command[0] == '/':
        print command[1:]
        return current_user.perform_action(command[1:])
    else:
        return easter(msg)


def easter(msg):
    return 'Please enter a valid command'
