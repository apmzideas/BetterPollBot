#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib.request
import urllib.parse
import ssl
import json
import platform


import GlobalObjects
import LoggingClass
import ErrorClasses
import LanguageClass

# import the _() function!
import LanguageClassTheSecond
_ = LanguageClassTheSecond.CreateTranslationObject("de_DE").gettext


class TelegramApi(object):
    def __init__(self, token,):
        self.token = token
        self.BotApiUrl = "https://api.telegram.org/bot" + self.token
        
        self.LoggingObject = GlobalObjects.ObjectHolder["LoggingClass"] # holds the logging Objekt
        self.LanguageObject = GlobalObjects.ObjectHolder["LanguageClass"]
        
        self.SSLEncription = ssl.SSLContext(ssl.PROTOCOL_SSLv23) 
        self.Headers = {
                        'User-agent': (GlobalObjects.__AppName__ + '/'+  str(GlobalObjects.__version__) +' (' +
                                       '; '.join( platform.system_alias( platform.system(), platform.release(), platform.version() ) ) +
                                       ') Python-urllib/' + str(platform.python_build()) +' from ' + GlobalObjects.__hosted__),
                        "Content-Type":" application/x-www-form-urlencoded;charset=utf-8"
                        }
        try:
            self.GetMe()
        except urllib.error.HTTPError as Error:
            if Error.code == 400:
                GlobalObjects.ObjectHolder["LoggingClass"].create_log( _("The webserver returned the HTTPError \"{0}\":").format(Error) + _("The token you are using has not been found in the system. Try later or check the token for spelling errors."), "Error" ) 
            elif Error.code == 401:   
                GlobalObjects.ObjectHolder["LoggingClass"].create_log( _("The webserver returned the HTTPError \"{0}\":").format(Error) + _("The token you are using has not been found in the system. Try later or check the token for spelling errors."), "Error" ) 
            elif Error.code == 403:
                GlobalObjects.ObjectHolder["LoggingClass"].create_log( _("The webserver returned the HTTPError \"{0}\":").format(Error) + _("The adress is forbidden to access, please try later."), "error" )
            elif Error.code == 404:
                GlobalObjects.ObjectHolder["LoggingClass"].create_log( _("The webserver returned the HTTPError \"{0}\":").format(Error) + _("The requested resource was not found. This status code can also be used to reject a request without closer reason. Links, which refer to those error pages, also referred to as dead links"), "Error")
            elif Error.code == 502:
                GlobalObjects.ObjectHolder["LoggingClass"].create_log( _("The webserver returned the HTTPError \"{0}\":").format(Error) + _("The server could not fulfill its function as a gateway or proxy, because it has itself obtained an invalid response. Please try later."), "Error" )
            elif Error.code == 504:
                GlobalObjects.ObjectHolder["LoggingClass"].create_log( _("The webserver returned the HTTPError \"{0}\":").format(Error) + _("The server could not fulfill its function as a gateway or proxy, because it has not received a reply from it's servers or services within a specified period of time."), "Error" )
            exit()     
            
    def GetMe(self):
        #A methode to confirm the token exists                                                    
        Request = urllib.request.Request(self.BotApiUrl + "/getMe", headers=self.Headers)
        
        response = urllib.request.urlopen(Request, context = self.SSLEncription).read().decode("utf-8")
        
        JSONData = json.loads(response)

             
              
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
        
        Request = urllib.request.urlopen(self.BotApiUrl + "/getUpdates",
                                          data=MessageData, 
                                          context=self.SSLEncription)
        
        Response = Request.read().decode("utf-8")
        
        JSONData = json.loads(Response)
        
        if JSONData["ok"]:
            return JSONData
        else:
            return None
        
    def SendMessage(self, MessageObject):
        #a methode to send Messeges to the TelegramApi
        
        MessageData = urllib.parse.urlencode(MessageObject.getMessage()).encode('utf-8') # data should be bytes
    
        req = urllib.request.Request(self.BotApiUrl + "/sendMessage", data= MessageData, headers=self.Headers)
        
        with urllib.request.urlopen(req) as response:
           the_page = response.read()
        return True      
     
    def SendMessageOld(self, Message, SendTo, DisableWebPagePreview = False,ReplyToId = None, ReplyMarkup = None):
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
    
        req = urllib.request.Request(self.BotApiUrl + "/sendMessage", data= MessageData, headers=self.Headers)
        
        with urllib.request.urlopen(req) as response:
           the_page = response.read()
        return True
    
    
if __name__ == "__main__":
    print('online')
    import pprint
    import Main
    Main.ObjectInitialiser()
    OrgTok = "80578257:AAEt5tHodsbD6P3hqumKYFJAyHTGWEgcyEY"
    FalTok = "80578257:AAEt5aH64bD6P3hqumKYFJAyHTGWEgcyEY"
    a = TelegramApi(FalTok,)
    if a:
        pprint.PrettyPrinter(indent=4).pprint((a.GetMe()))
        pprint.PrettyPrinter(indent=4).pprint((a.GetUpdates()))
    else:
        print("None")
    print('offline')