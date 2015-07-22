#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import json
import LoggingClass
import ErrorClasses
import LanguageClass

class TelegramApi(object):
    def __init__(self, token, LoggingObject, LanguageObject):
        self.token = token
        self.url = "https://api.telegram.org/bot" + self.token
        self.LoggingObject = LoggingObject  # holds the logging Objekt
        
        self.GetMe()
            
    
    def GetMe(self):
        #A methode to confirm the token exists
        
        response = urllib.request.urlopen(self.url + "/getMe").read().decode("utf-8")
        
        JSONData = json.loads(response)
        
        if JSONData["ok"]:
            return True
        else:
            raise ErrorClasses.TokenError( LanguageClass.GetStringName())
        
       
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
        
        response = urllib.request.urlopen(self.url + "/getUpdates", data=MessageData).read().decode("utf-8")
        
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
    
        req = urllib.request.Request(self.url + "/sendMessage", data= MessageData )
        
        with urllib.request.urlopen(req) as response:
           the_page = response.read()
           print(the_page)
    
if __name__ == "__main__":
    import pprint
    a = TelegramApi("80578257:AAEt5tHodsbD6P3hqumKYFJAyHTGWEgcyEY", LoggingClass.Logger(), LanguageClass.Languages("enGB"))
    if a:
        pprint.PrettyPrinter(indent=4).pprint((a.GetUpdates()))
    else:
        print("None")