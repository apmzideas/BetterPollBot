#!/usr/bin/python
# -*- coding: utf-8 -*-

#python standard library
import urllib.request
import urllib.parse
import ssl
import json
import platform

#my own babys
import GlobalObjects
import LoggingClass
import ErrorClasses
import MessageClass
import LanguageClass # imports the _() function! (the translation feature.

class TelegramApi(object):
    #This class is responsable for contacting the telegram servers.
    def __init__(self, ApiToken, **OptionalObjects):
        self.ApiToken = ApiToken
        self.BotApiUrl = "https://api.telegram.org/bot" + self.ApiToken
        
        #Predefining attribute so that it later can be used for evil.
        self.LanguageObject = None
        self.LogggingObject = None
        
        if "LanguageObject" in OptionalObjects:
            self.LanguageObject = OptionalObjects["LanguageObject"]
        else:
            self.LanguageObject = LanguageClass.CreateTranslationObject()
        if "LoggingObject" in OptionalObjects:
            self.LogggingObject = OptionalObjects["LoggingObject"]
        else:
            self.LogggingObject = LoggingClass.Logger()
        
        #Hier we are initialising the function for the translations 
        self._ = self.LanguageObject.gettext

#         #creates the language translation object
#         global _
#         _ = LanguageObject.gettext
        
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
            #Response = .read().decode("utf-8")
            
            TheResponse = ''
            with urllib.request.urlopen(Request, context = self.SSLEncription) as Request:
                TheResponse = Request.read()
            return json.loads(TheResponse.decode("utf-8"))
        
        except urllib.error.HTTPError as Error:
            if Error.code == 400:
                self.LoggingObject.create_log( self._("The webserver returned the HTTPError \"{Error}\".").format(Error=(str(Error.code) + " " + Error.reason)) +" " + self._("The ApiToken you are using has not been found in the system. Try later or check the ApiToken for spelling errors."), "Error" ) 
            elif Error.code == 401:   
                self.LoggingObject.create_log( self._("The webserver returned the HTTPError \"{Error}\".").format(Error=(str(Error.code) + " " + Error.reason)) +" " +  self._("The ApiToken you are using has not been found in the system. Try later or check the ApiToken for spelling errors."), "Error" ) 
            elif Error.code == 403:
                self.LoggingObject.create_log( self._("The webserver returned the HTTPError \"{Error}\".").format(Error=(str(Error.code) + " " + Error.reason)) +" " +  self._("The adress is forbidden to access, please try later."), "error" )
            elif Error.code == 404:
                self.LoggingObject.create_log( self._("The webserver returned the HTTPError \"{Error}\".").format(Error=(str(Error.code) + " " + Error.reason)) +" " +  self._("The requested resource was not found. This status code can also be used to reject a request without closer reason. Links, which refer to those error pages, also referred to as dead links."), "Error")
            elif Error.code == 502:
                self.LoggingObject.create_log( self._("The webserver returned the HTTPError \"{Error}\".").format(Error=(str(Error.code) + " " + Error.reason)) +" " +  self._("The server could not fulfill its function as a gateway or proxy, because it has itself obtained an invalid response. Please try later."), "Error" )
            elif Error.code == 504:
                self.LoggingObject.create_log( self._("The webserver returned the HTTPError \"{Error}\".").format(Error=(str(Error.code) + " " + Error.reason)) +" " + self._("The server could not fulfill its function as a gateway or proxy, because it has not received a reply from it's servers or services within a specified period of time."), "Error" )
            
            #For the recursive loop, so that the system can handel itself better
            if ExitOnError:
                exit()  
            
    def GetMe(self):
        #A methode to confirm the ApiToken exists                                                    
        Request = urllib.request.Request(self.BotApiUrl + "/getMe", headers=self.Headers)
        
        return self.SendRequest(Request)
             
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
        #a method to send Messeges to the TelegramApi
        
        MessageData = urllib.parse.urlencode(MessageObject.GetMessage()).encode('utf-8') # data should be bytes
    
        Request = urllib.request.Request(self.BotApiUrl + "/sendMessage", 
                                         data= MessageData,
                                          headers=self.Headers)
        
        return self.SendRequest(Request, ExitOnError=False)       

    def ForwardMessage(self, ChatId, FromChatId, MessageId):
        #A method to forward a message
        MessageData = {}
    
if __name__ == "__main__":
    print('online')
    import pprint
    import Main
    Main.ObjectInitialiser()
    OrgTok = "80578257:AAEt5tHodsbD6P3hqumKYFJAyHTGWEgcyEY"
    FalTok = "80578257:AAEt5aH64bD6P3hqumKYFJAyHTGWEgcyEY"
    a = TelegramApi(OrgTok, 
                    LanguageObject = LanguageClass.CreateTranslationObject("de"),)
    
    Update = a.GetUpdates()
    #print(Update)
    #print(Update["result"][0]["message"]["chat"]["id"])
    
    MessageObject = MessageClass.MessageToBeSend(Update["result"][len(Update["result"])-1]["message"]["chat"]["id"], 
                                         "Hier könnte Ihre Werbung stehen.")
    print(a.SendMessage(MessageObject))
#     if a:
#         pprint.PrettyPrinter(indent=4).pprint((a.GetMe()))
#         pprint.PrettyPrinter(indent=4).pprint((a.GetUpdates()))
#     else:
#         print("None")
    print('offline')