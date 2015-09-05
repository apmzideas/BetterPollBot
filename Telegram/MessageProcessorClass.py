#!/usr/bin/python
# -*- coding: utf-8 -*-
import GlobalObjects
import json
import LanguageClass  # imports the _() function! (the translation feature).
import LoggingClass
import SqlClass
import PollingClass
import ErrorClasses
import ConfigurationClass

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
        
        # Predefining attribute so that it later can be used for evil.
        self.LoggingObject = None
        self.ConfigurationObject = None
        
        # SqlObjects
        self.SqlObject = None
        self.SqlCursor = None
        
        if "LoggingObject" in OptionalObjects:
            self.LoggingObject = OptionalObjects["LoggingObject"]
        else:
            self.LoggingObject = LoggingClass.Logger()
        if "ConfigurationObject" in OptionalObjects:
            self.ConfigurationObject = OptionalObjects["ConfigurationObject"]
        else:
            self.ConfigurationObject = ConfigurationClass.ConfigurationParser()
        if "SqlObject" in OptionalObjects:
            self.SqlObject = OptionalObjects["SqlObject"]
            
            self.SqlCursor = self.SqlObject.CreateCursor()
        else:
            self.LoggingObject.create_log(self._("The sql obejct is missing, please contact your administrator."), "Error")
            raise ErrorClasses.MissingArguments(self._("The sql obejct is missing, please contact your administrator."))
        
        if "update_id" in MessageObject:
            self.UpdateId = MessageObject["update_id"]
        
        if "message_id" in MessageObject["message"]:
            self.MessageID = MessageObject["message"]["message_id"]

        # get the user of the message
        # get user data from the message
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
        
        
        # Add user to the system if not exists
        if self.UserExists() == False:
            self.AddUser()
            
        # Get the Internal user id
        self.InternalUserId = self.GetInternalUserId()
        # Hier we are initialising the function for the translations
        # Get the user settings
        Query = "SELECT user_setting_table.User_String FROM user_setting_table "\
                "INNER JOIN setting_table "\
                "ON user_setting_table.Master_Setting_Id=setting_table.Setting_Id "\
                "WHERE setting_table.Setting_Name=%s "\
                "AND user_setting_table.Master_User_Id=%s;"
        
        Data = ("Language", self.InternalUserId)
        
        self.LanguageName = self.SqlObject.ExecuteTrueQuery(self.SqlCursor, Query, Data)[0]["User_String"]
        
        self.LanguageObject = LanguageClass.CreateTranslationObject(Languages=[self.LanguageName])
        # create the translator        
        self._ = self.LanguageObject.gettext
        
        
        # Get the textmessage with the commands
        if "text" in MessageObject["message"]:
            self.Text = MessageObject["message"]["text"]
        
        # where was the message send from the user or the group
        # Get the chat id
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
       # This methode will detect if the use already exists or not. 
#         temp = self.SqlObject.SelectEntry(self.SqlCursor, 
#                                           FromTable="User_Table", 
#                                           Columns = (
#                                                      "External_User_Id",
#                                                      "Creation_Date",
#                                                      "User_Name",
#                                                      "First_Name",
#                                                      "Last_Name"
#                                                      ),
#                                           Where = ["External_User_Id", "=", "%s"],
#                                           Data = (self.UserId),
#                                           )


#  The following query will return 1 if a user with the specified username exists, 0 otherwise.
# 
# SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'username')

        temp = self.SqlObject.ExecuteTrueQuery(
                                          self.SqlObject.CreateCursor(Dictionary=False),
                                          Query="SELECT EXISTS(SELECT 1 FROM User_Table WHERE External_User_Id = %s);",
                                          Data=self.UserId
                                          )          

        temp = temp[0][0]
        if temp == False:
            return False
        else:
            return True
        
    def AddUser(self,):
        # Insert into user
        TableName = "User_Table"
        Columns = {
                   "External_User_Id" : self.UserId,
                   "User_Name" : self.UserName,
                   "First_Name": self.UserFirstName,
                   "Last_Name": self.UserLastName
                   }
        
        self.SqlObject.InsertEntry(self.SqlCursor, TableName, Columns)
        self.SqlObject.Commit(self.SqlCursor)

        # insert default settings
        # get default values

        
        # get the default settigns
        # get the default language
        FromTable = "Setting_Table"
        Columns = ["Setting_Id", "Default_String"]
        Where = [["Setting_Name", "=", "%s"]]
        Data = ("Language")
        MasterSetting = self.SqlObject.SelectEntry(
                                                   self.SqlCursor,
                                                   FromTable=FromTable,
                                                   Columns=Columns,
                                                   Where=Where,
                                                   Data=Data
                                                   )[0]
        
        TableName = "User_Setting_Table"
                 
        Columns = {
                   "Master_Setting_Id": MasterSetting["Setting_Id"],
                   "Master_User_Id": self.InternalUserId[0]["Internal_User_Id"],
                   "User_String": MasterSetting["Default_String"]
                   } 
        self.SqlObject.InsertEntry(self.SqlCursor, TableName, Columns)   
        
        self.SqlObject.Commit(self.SqlCursor)
        
        return True
    
    def GetInternalUserId(self):
        # first the internal user id
        FromTable = "User_Table"
        Columns = ["Internal_User_Id"]
        Where = [["External_User_Id", "=", "%s"]]
        Data = (self.UserId,)
        
        return self.SqlObject.SelectEntry(
                                                         self.SqlCursor,
                                                         FromTable=FromTable,
                                                         Columns=Columns,
                                                         Where=Where,
                                                         Data=Data
                                                         )[0]["Internal_User_Id"]
        
        
    def GetUserSetting(self):
        # get user settings
        pass
    
    def InterpretMessage(self):
        # This methode will interpret and the message and do what ever is needed.
        if self.Text == "/newpoll":
            
            Poll = PollingClass.Poll(ExternalUserId=self.UserId, PollId=None,)
            Poll.GetPollName()
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
    # a = MessageProcessor(MessageObject)
    
    import pprint
    foo = {'result': [{'update_id': 469262050, 'message': {'chat': {'first_name': 'Robin', 'id': 105654068}, 'text': '/start', 'date': 1439417521, 'from': {'first_name': 'Robin', 'id': 105654068}, 'message_id': 89}}], 'ok': True}
    # pprint.PrettyPrinter(indent=2).pprint(foo["result"])
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
    # a = MessageProcessor(foo["result"][0], ) 
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
                                            'id':-7903240,
                                            'title': 'Drive'
                                            }
                                   },
                        'update_id': 469262057
                        }
                      ]
           }
    LanguageObject = LanguageClass.CreateTranslationObject()
    LoggingObject = LoggingClass.Logger(config_name='config.ini', log_to_file=False)

    Config = ConfigurationClass.ConfigurationParser()
    Config.ReadConfigurationFile()

    SqlObject = SqlClass.SqlApi("root",
                                 "Password",
                                 Config["MySQL Connection Parameter"]["DatabaseName"],
                                 LoggingObject=LoggingObject,
                                 
                                 LanguageObject=LanguageClass.CreateTranslationObject("de_DE")
                                                              )
    a = MessageProcessor(
                         MessageObject=foo["result"][0],
                         OptionalObjects={
                         "LanguageObject": LanguageObject,
                         "LoggingObject" : LanguageObject,
                         "SqlObject": SqlObject,
                         "ConfigurationObject": Config}
                         )
