from bs4 import BeautifulSoup as bs

import prashanth
import user
import sections


me = user.User()
me.username = prashanth.username
me.password = prashanth.password
me.begin_session()
"""
from telepot.loop import MessageLoop
import telepot


def handle(msg):
    telepot.glance(msg)
    print msg['text']


def flush():
    bot = telepot.Bot('441669105:AAH3Brfz_jw0np86aPv7AKgPzOA6kzkb4fs')
    MessageLoop(bot, handle).run_as_thread()
flush()
"""