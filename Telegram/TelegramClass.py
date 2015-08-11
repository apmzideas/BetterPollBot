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
_ = LanguageClassTheSecond.CreateTranslationObject(["en_US"]).gettext


class TelegramApi(object):
    def __init__(self, ApiToken, LanguageObject, LoggingObject):
        self.ApiToken = ApiToken
        self.BotApiUrl = "https://api.telegram.org/bot" + self.ApiToken
        
         # holds the logging Objekt
        self.LoggingObject = LoggingObject

        
        self.SSLEncription = ssl.SSLContext(ssl.PROTOCOL_SSLv23) 
        self.Headers = {
                        'User-agent': (
                                       GlobalObjects.__AppName__ + '/'+ str(GlobalObjects.__version__) 
                                       +' (' +
                                       '; '.join( platform.system_alias(
                                                            platform.system(), 
                                                            platform.release(),
                                                            platform.version()
                                                            ) 
                                                 ) +
                                       ') Python-urllib/' +
                                        str(platform.python_build()) +
                                        ' from ' + GlobalObjects.__hosted__
                                        ),
                        "Content-Type":
                        "application/x-www-form-urlencoded;charset=utf-8"
                        }
        
        self.GetMe() 
    
    def SendRequest(self, Request, ExitOnError=True):
        try:
            Response = urllib.request.urlopen(Request, context = self.SSLEncription).read().decode("utf-8")
            return json.loads(Response)
        
        except urllib.error.HTTPError as Error:
            if Error.code == 400:
                self.LoggingObject.create_log( _("The webserver returned the HTTPError \"{0}\":").format(str(Error.code) + " " + Error.reason) +" " + _("The ApiToken you are using has not been found in the system. Try later or check the ApiToken for spelling errors."), "Error" ) 
            elif Error.code == 401:   
                self.LoggingObject.create_log( _("The webserver returned the HTTPError \"{0}\":").format(str(Error.code) + " " + Error.reason) +" " +  _("The ApiToken you are using has not been found in the system. Try later or check the ApiToken for spelling errors."), "Error" ) 
            elif Error.code == 403:
                self.LoggingObject.create_log( _("The webserver returned the HTTPError \"{0}\":").format(str(Error.code) + " " + Error.reason) +" " +  _("The adress is forbidden to access, please try later."), "error" )
            elif Error.code == 404:
                self.LoggingObject.create_log( _("The webserver returned the HTTPError \"{0}\":").format(str(Error.code) + " " + Error.reason) +" " +  _("The requested resource was not found. This status code can also be used to reject a request without closer reason. Links, which refer to those error pages, also referred to as dead links"), "Error")
            elif Error.code == 502:
                self.LoggingObject.create_log( _("The webserver returned the HTTPError \"{0}\":").format(str(Error.code) + " " + Error.reason) +" " +  _("The server could not fulfill its function as a gateway or proxy, because it has itself obtained an invalid response. Please try later."), "Error" )
            elif Error.code == 504:
                self.LoggingObject.create_log( _("The webserver returned the HTTPError \"{0}\":").format(str(Error.code) + " " + Error.reason) +" " +  _("The server could not fulfill its function as a gateway or proxy, because it has not received a reply from it's servers or services within a specified period of time."), "Error" )
            
            #For the recursive loop, so that the system can handel itself better
            if ExitOnError:
                exit()  
            else:
                pass
    
    def GetMe(self):
        #A methode to confirm the ApiToken exists                                                    
        Request = urllib.request.Request(self.BotApiUrl + "/getMe", headers=self.Headers)
        
        return self.SendRequest(Request,)
             
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
            
        Request = urllib.request.Request(self.BotApiUrl + "/getUpdates",
                                              data=MessageData, 
                                              headers=self.Headers)
        
        #send Request and get JSONData    
        JSONData = self.SendRequest(Request)
        
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
     
    def SendMessageOld(self, Message, SendTo, DisableWebPagePreview = False, ReplyToId = None, ReplyMarkup = None):
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
    a = TelegramApi(OrgTok, 
                    LanguageClassTheSecond.CreateTranslationObject(),
                    GlobalObjects.ObjectHolder["LoggingClass"])
    if a:
        pprint.PrettyPrinter(indent=4).pprint((a.GetMe()))
        pprint.PrettyPrinter(indent=4).pprint((a.GetUpdates()))
    else:
        print("None")
    print('offline')