from pprint import pprint
from user import User

import bot_responses
import json
import requests
import message_handler
import time
import urllib
import prashanth

TOKEN = '441669105:AAH3Brfz_jw0np86aPv7AKgPzOA6kzkb4fs'
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
USERS = {}


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def send_message(chat_id, text):
    text = text.encode('utf8')
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=markdown".format(text, chat_id)
    get_url(url)


def echo_all(updates):
    global USERS
    for update in updates["result"]:
        try:
            chat_id = update["message"]["chat"]["id"]
            if chat_id != 438683844:
                continue
            if chat_id not in USERS:
                send_message(chat_id, "Hi! This is SLCM Bot.")
                USERS[chat_id] = User()
            current_user = USERS[chat_id]

            if 'text' not in update["message"]:
                send_message(chat_id, 'Please enter a valid command')
                continue

            text = update["message"]["text"]
            db_edit, reply = message_handler.handle(text, current_user)

            for each_reply in reply.split(":::"):
                send_message(chat_id, urllib.quote_plus(each_reply.strip().encode("utf8")))

            if db_edit:
                if reply == bot_responses.new_user_login:
                    logged_in, reply = current_user.begin_session()
                    if logged_in:
                        print "Add items to database"
                    send_message(chat_id, reply)

            # if current_user.current_tab == "new user":
            #     current_user.current_tab = "asked for username"
            #     send_message(chat_id, 'Enter your registration number.')
            #     continue

            # if current_user.current_tab == "asked for username":
            #     current_user.username = text
            #     current_user.current_tab = "asked for password"
            #     send_message(chat_id, 'Enter your SLCM password. \n(The bot can\'t view it)')
            #     continue
            # if current_user.current_tab == "asked for password":
            #     current_user.password = text
            #     current_user.logged_in = False
            #     reply = "..."
            #     send_message(chat_id, 'It is recommended that you delete your password for your own privacy.')

            # if not current_user.logged_in:
            #     current_user.username = prashanth.username
            #     current_user.password = prashanth.password
            #     reply = "."
            #     send_message(chat_id, 'Please wait while we are logging you in...')
            #     send_message(chat_id, current_user.begin_session())
            # if reply is None:

        except Exception as err:
            print err


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
