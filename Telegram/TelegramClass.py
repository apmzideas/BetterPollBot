#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib.request
import urllib.parse
import ssl
import json

import GlobalObjects
import LoggingClass
import ErrorClasses
import LanguageClass

import platform


class TelegramApi(object):
    def __init__(self, token, LoggingObject, LanguageObject):
        self.token = token
        self.url = "https://api.telegram.org/bot" + self.token
        self.LoggingObject = LoggingObject  # holds the logging Objekt
        self.SSLEncription = ssl.SSLContext(ssl.PROTOCOL_SSLv23) 
        self.Headers = {
                        'User-agent': (GlobalObjects.__name__ + '/'+  str(GlobalObjects.__version__) +' (' +
                                       '; '.join( platform.system_alias( platform.system(), platform.release(), platform.version() ) ) +
                                       ') Python-urllib/' + platform.python_version() +' from https://github.com/apmzideas/BetterPollBot'),
                        "Content-Type":" application/x-www-form-urlencoded;charset=utf-8"
                        }
        self.GetMe()
            
    
    def GetMe(self):
        #A methode to confirm the token exists                                                    
        Request = urllib.request.Request(self.url + "/getMe", headers=self.Headers)
        
        response = urllib.request.urlopen(Request, context = self.SSLEncription).read().decode("utf-8")
        
        JSONData = json.loads(response)
        
        if JSONData["ok"]:
            return JSONData
        else:
            raise ErrorClasses.TokenError( LanguageClass.GetString())
        
       
    def GetUpdates(self, CommentNumber = None):
        # a Methode to get the Updates as well to confirm the old comments from the Telegram API
        #Notes
        #1. This method will not work if an outgoing webhook is set up.
        #2. In order to avoid getting duplicate updates, recalculate offset after each server response.
        
        DataToBeSend = {
                        "limit": 1,
                        "timeout": 0
                        }
        
        if CommentNumber:
            DataToBeSend["offset"] = CommentNumber
        
        MessageData = urllib.parse.urlencode({"limit": 1}).encode('utf-8')  # data should be bytes
        
        response = urllib.request.urlopen(self.url + "/getUpdates", data=MessageData, context=self.SSLEncription).read().decode("utf-8")
        
        JSONData = json.loads(response)
        
        if JSONData["ok"]:
            return JSONData
        else:
            return None
        
        
    def SendMessage(self, Message, SendTo, DisableWebPagePreview = False,ReplyToId = None, ReplyMarkup = None):
        #a methode to send Messeges to the TelegramApi
        
        DataToBeSend = { 
                        "chat_id": SendTo, 
                        "text": bytes(Message.encode("uft-8")),
                        }
        
        if DisableWebPagePreview:
            DataToBeSend["disable_web_page_preview"] = True
        if ReplyToId.isdigit():
            DataToBeSend["reply_to_message_id"] = ReplyToId
            
        if isinstance(ReplyMarkup, dict):
            DataToBeSend["reply_markup"] = ReplyMarkup
        
        MessageData = urllib.parse.urlencode(DataToBeSend).encode('utf-8') # data should be bytes
    
        req = urllib.request.Request(self.url + "/sendMessage", data= MessageData, headers=self.Headers)
        
        with urllib.request.urlopen(req) as response:
           the_page = response.read()
        return True
    
    
if __name__ == "__main__":
    print('online')
    import pprint
    a = TelegramApi("80578257:AAEt5tHodsbD6P3hqumKYFJAyHTGWEgcyEY", LoggingClass.Logger(), LanguageClass.Languages("enGB"))
    if a:
        pprint.PrettyPrinter(indent=4).pprint((a.GetMe()))
        pprint.PrettyPrinter(indent=4).pprint((a.GetUpdates()))
    else:
        print("None")
    print('offline')