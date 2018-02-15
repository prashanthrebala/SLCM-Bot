import bot_responses


def handle(message, current_user):

    if current_user.current_tab == "new user":
        current_user.current_tab = "asked for username"
        return False, bot_responses.ask_for_username

    if current_user.current_tab == "asked for username":
        current_user.username = message
        current_user.current_tab = "asked for password"
        return False, bot_responses.ask_for_password

    if current_user.current_tab == "asked for password":
        current_user.password = message
        current_user.logged_in = False
        return True, bot_responses.new_user_login

    command = message.split()[0]
    if command[0] == '/':
        r = current_user.perform_action(command[1:])
        return False, r
    else:
        return easter(message)


def easter(message):
    print "in easter"
    return 'Please enter a valid command'
