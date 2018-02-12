from pprint import pprint
from scraper import User

import json
import requests
import message_handler
import time
import urllib

TOKEN = '441669105:AAH3Brfz_jw0np86aPv7AKgPzOA6kzkb4fs'
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
USER = None


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
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def echo_all(updates):
    global USER
    for update in updates["result"]:
        try:
            chat = update["message"]["chat"]["id"]
            if 'text' not in update["message"]:
                send_message(chat, 'Please enter a valid command')
                continue
            text = update["message"]["text"]
            reply = message_handler.handle(text, USER)
            if isinstance(reply, tuple):
                USER = reply[1]
                reply = reply[0]
            send_message(chat, reply)
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
