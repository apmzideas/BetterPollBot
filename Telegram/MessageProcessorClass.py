#!/usr/bin/python
# -*- coding: utf-8 -*-
import GlobalObjects
import json
import LanguageClass # imports the _() function! (the translation feature).
import LoggingClass
import SqlClass
import ErrorClasses

class MessageProcessor(object):
    def __init__(self, MessageObject, **OptionalObjects):
        
# The MessageObject will only contains a single message object, so that this class will be thread save 
#        {
#                        'message': {
#                                    'date': 1439471738, 
#                                    'text': '/newpoll',
#                                    'from': {
#                                             'id': 32301786, 
#                                             'last_name': 'Hornung', 
#                                             'first_name': 'Adrian', 
#                                             'username': 'TheRedFireFox'
#                                             }, 
#                                    'message_id': 111, 
#                                    'chat': {
#                                             'id': -7903240, 
#                                             'title': 'Drive'
#                                             }
#                                    },
#                         'update_id': 469262057
#                         }
        
        
#         #check if any updates came in
#         if self.MessageObject["results"] == []:
#             return False
        
        #Predefining attribute so that it later can be used for evil.
        self.LoggingObject = None
        
        #SqlObjects
        self.SqlObject = None
        self.SqlCursor = None
        
        if "LoggingObject" in OptionalObjects:
            self.LoggingObject = OptionalObjects["LoggingObject"]
        else:
            self.LoggingObject = LoggingClass.Logger()
        if "SqlObject" in OptionalObjects:
            self.SqlObject= OptionalObjects["SqlObject"]
            
            self.SqlCursor = self.SqlObject.CreateCursor()
        else:
            self.LoggingObject.create_log( self._( "The sql obejct is missing, please contact your administrator." ), "Error")
            raise ErrorClasses.MissingArguments(self._( "The sql obejct is missing, please contact your administrator." ) )
        
        if "update_id" in MessageObject:
            self.UpdateId = MessageObject["update_id"]
        
        if "message_id" in MessageObject["message"]:
            self.MessageID = MessageObject["message"]["message_id"]

        #get the user of the message
        #get user data from the message
        if "first_name" in MessageObject["message"]["from"]:
            self.UserFirstName = MessageObject["message"]["from"]["first_name"]
        else:
            self.UserFirstName = ""
        if "last_name" in MessageObject["message"]["from"]:
            self.UserLastName = MessageObject["message"]["from"]["last_name"]
        else:
            self.UserLastName = ""
        if "username" in MessageObject["message"]["from"]:
            self.UserName = MessageObject["message"]["from"]["username"]
        else:
            self.UserName = ""
        if "id" in MessageObject["message"]["from"]:
            self.UserId = MessageObject["message"]["from"]["id"]
        
        #print(self.UserExists())
        #Add user to the system if not exists
        if self.UserExists() == False:
            self.AddUser()
        
        self.LanguageObject = None
        if "LanguageObject" in OptionalObjects:
            self.LanguageObject = OptionalObjects["LanguageObject"]
        else:
            self.LanguageObject = LanguageClass.CreateTranslationObject()
        
            
        
        #Hier we are initialising the function for the translations 
        self._ = self.LanguageObject.gettext
        
        
        #Get the textmessage with the commands
        if "text" in MessageObject["message"]:
            self.Text = MessageObject["message"]["text"]
        
        #where was the message send from the user or the group
        #Get the chat id
        if "id" in MessageObject["message"]["chat"]:
            self.ChatId = MessageObject["message"]["chat"]["id"]
        
        if self.ChatId != self.UserId:
            self.InGroup = False
        else:
            self.InGroup = True
        
#         if "from_user" in Message:
#             self.FromUser = Message["from_user"]
#         if "date" in Message:
#             self.date = Message["date"]
#         if "chat" in Message:
#             self.chat = Message["chat"]
#         if "date" in Message:
#             self.date = Message["date"]
#         if "chat" in Message:
#             self.chat = Message["chat"]
#         if "forward_from" in Message:
#             self.forward_from in Message["forward_from"]
#         if "forward_date" in Message:
#             self.forward_date = Message["forward_date"]
#         if "reply_to_message" in Message:
#             self.reply_to_message = Message["reply_to_message"]
#         if "text" in Message:
#             self.text = Message["text"]
#         if "audio" in Message:
#             self.audio = Message["audio"]
#         if "document" in Message:
#             self.document = Message["document"]
#         if "photo" in Message:
#             self.photo = Message["photo"]
#         if "sticker" in Message:
#             self.sticker =  Message["sticker"]
#         if "video" in Message:
#             self.video = Message["video"]
#         if "caption" in Message:
#             self.caption = Message["caption"]
#         if "contact" in Message:
#             self.contact = Message["contact"]
#         if "location" in Message:
#             self.location = Message["location"]
#         if "new_chat_participant" in Message:
#             self.new_chat_participant = Message["new_chat_participant"]
#         if "left_chat_participant" in Message:
#             self.left_chat_participant = Message["left_chat_participant"]
#         if "new_chat_title" in Message:
#             self.new_chat_title = Message["new_chat_title"]
#         if "new_chat_photo" in Message:
#             self.new_chat_photo = Message["new_chat_photo"]
#         if "delete_chat_photo" in Message:
#             self.delete_chat_photo = Message["delete_chat_photo"]
#         if "group_chat_created" in Message:
#             self.group_chat_created = Message["group_chat_created"]

    def UserExists(self,):
        
        temp = self.SqlObject.SelectEntry(self.SqlCursor, 
                                          FromTable="User_Table", 
                                          Columns = (
                                                     "External_User_Id",
                                                     "Creation_Date",
                                                     "User_Name",
                                                     "First_Name",
                                                     "Last_Name"
                                                     ),
                                          Where = ["External_User_Id", "=", "%s"],
                                          Data = (self.UserId),
                                          )
        #print(temp)
        if temp == None or temp == []:
            return False
        else:
            return True
        
        
    def AddUser(self,):
        #Insert into user
        TableName = "User_Table"
        Columns = {
                   "External_User_Id" : self.UserId,
                   "User_Name" : self.UserName,
                   "First_Name": self.UserFirstName,
                   "Last_Name": self.UserLastName
                   }
        
        self.SqlObject.InsertEntry(self.SqlCursor, TableName, Columns)
        self.SqlObject.Commit(self.SqlCursor)
    
    def GetUserSetting(self):
        #get user settings
        pass
        
    
if __name__ == "__main__":
    import Main
    Main.ObjectInitialiser()
    MessageObject = {
                     'update_id': 469262050, 
                     'message': {
                                 'chat': {
                                          'first_name': 'Robin', 
                                          'id': 105654068
                                          
                                          }, 
                                 'text': '/start', 
                                 'date': 1439417521,
                                 'from': {
                                          'first_name': 'Robin',
                                          'id': 105654068
                                          }, 
                                 'message_id': 89
                                 }}
    #a = MessageProcessor(MessageObject)
    
    import pprint
    foo = {'result': [{'update_id': 469262050, 'message': {'chat': {'first_name': 'Robin', 'id': 105654068}, 'text': '/start', 'date': 1439417521, 'from': {'first_name': 'Robin', 'id': 105654068}, 'message_id': 89}}], 'ok': True}
    #pprint.PrettyPrinter(indent=2).pprint(foo["result"])
    foo = { 
           'ok': True,
           'result': [
                      { 'message': { 
                                    'chat': { 
                                             'first_name': 'Jonas',
                                             'id': 10620786,
                                             'last_name': 'Löw',
                                             'username': 'kiritjom'
                                             },
                                    'date': 1439412135,
                                    'from': { 
                                             'first_name': 'Jonas',
                                             'id': 10620786,
                                             'last_name': 'Löw',
                                             'username': 'kiritjom'
                                             },
                                    'message_id': 55,
                                    'text': 'yep'
                                    },
                       'update_id': 469262035
                       }
                      ]
           }
    #a = MessageProcessor(foo["result"][0], ) 
    foo = {
           'ok': True, 
           'result': [
                      {
                       'message': {
                                   'date': 1439471738, 
                                   'text': '/newpoll',
                                   'from': {
                                            'id': 32301786, 
                                            'last_name': 'Hornung', 
                                            'first_name': 'Adrian', 
                                            'username': 'TheRedFireFox'
                                            }, 
                                   'message_id': 111, 
                                   'chat': {
                                            'id': -7903240, 
                                            'title': 'Drive'
                                            }
                                   },
                        'update_id': 469262057
                        }
                      ]
           }
    LanguageObject= LanguageClass.CreateTranslationObject()
    LoggingObject = LoggingClass.Logger(config_name='config.ini', log_to_file=False)
    
    import ConfigurationClass
    Config = ConfigurationClass.ConfigurationParser()
    Config.ReadConfigurationFile()

    SqlObject =  SqlClass.SqlApi("root", 
                                 "Password", 
                                 Config["MySQL Connection Parameter"]["DatabaseName"],
                                 LoggingObject = LoggingObject,
                                 
                                 LanguageObject = LanguageClass.CreateTranslationObject("de_DE")
                                                              )
    a = MessageProcessor(
                         MessageObject = foo["result"][0],
                         OptionalObjects = {
                         "LanguageObject": LanguageObject,
                         "LoggingObject" : LanguageObject, 
                         "SqlObject": SqlObject}
                         )