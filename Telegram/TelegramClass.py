#!/usr/bin/python

class TelegramApi(object):
    def __init__(self, token):
        self.token = token
        self.url = "https://api.telegram.org/bot"