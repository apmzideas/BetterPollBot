#!/usr/bin/python
# -*- coding: utf-8 -*-
import GlobalObjects

import json

import language.LanguageClass  # imports the _() function! (the translation feature).
import LoggingClass
import sql.SqlClass
import ErrorClasses
import parsers.ConfigurationClass

import messages.PollingClass
import messages.MessageClass
import messages.EmojiClass

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
            self.ConfigurationObject = parsers.ConfigurationClass.ConfigurationParser()
            
        if "SqlObject" in OptionalObjects:
            self.SqlObject = OptionalObjects["SqlObject"]
            
            # The object get's it's own cursor so that there will be no 
            # problems in the future making the system multi threading safe.
            self.SqlCursor = self.SqlObject.CreateCursor()

        else:
            self.LoggingObject.error(self._("The sql obejct is missing, please contact your administrator."))
            raise ErrorClasses.MissingArguments(self._("The sql obejct is missing, please contact your administrator."))
        
        # This variable is needed for the logger so that the log end up 
        # getting printed in the correct language.
        if "LanguageObeject"  in OptionalObjects:
            self.M_ = OptionalObjects["LanguageObject"].gettext
        else:
            self.M_ = language.LanguageClass.CreateTranslationObject()
            
        if "BotName" in OptionalObjects:
            self.BotName = OptionalObjects["BotName"]["result"]["username"]
            #print(self.BotName, type(self.BotName))
        else:
            self.BotName = GlobalObjects.__AppName__
        
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
#         print(self.InternalUserId)
        
        # Hier we are initialising the function for the translations
        # Get the user settings
        Query = "SELECT user_setting_table.User_String FROM user_setting_table "\
                "INNER JOIN setting_table "\
                "ON user_setting_table.Master_Setting_Id=setting_table.Setting_Id "\
                "WHERE setting_table.Setting_Name=%s "\
                "AND user_setting_table.Master_User_Id=%s;"
        
        Data = ("Language", self.InternalUserId)
        
        self.LanguageName = self.SqlObject.ExecuteTrueQuery(self.SqlCursor, Query, Data)[0]["User_String"]
        
        self.LanguageObject = language.LanguageClass.CreateTranslationObject(Languages=[self.LanguageName])
        # create the translator        
        self._ = self.LanguageObject.gettext
        
        # Get the textmessage with the command
        if "text" in MessageObject["message"]:
            self.Text = MessageObject["message"]["text"]
        else:
            self.Text = None
        # where was the message send from the user or the group
        # Get the chat id
        if "id" in MessageObject["message"]["chat"]:
            self.ChatId = MessageObject["message"]["chat"]["id"]
        
        if self.ChatId == self.UserId:
            self.InGroup = False
        else:

            self.InGroup = True
            self.GroupName = MessageObject["message"]["chat"]["title"]
            # Check if group exists
            if self.GroupExists() == False:
                self.AddGroup()
            self.InternalGroupId = self.GetInternalGroupId()
        

#        if "from_user" in MessageObject:
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
        #  The following query will return 1 if a user with the specified username exists, 0 otherwise.
        # 
        # SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'username')

        Exists = self.SqlObject.ExecuteTrueQuery(
                                          self.SqlObject.CreateCursor(Dictionary=False),
                                          Query="SELECT EXISTS(SELECT 1 FROM User_Table WHERE External_User_Id = %s);",
                                          Data=self.UserId
                                          )[0][0]    

        if Exists == False:
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
                   "Master_User_Id": self.GetInternalUserId(),
                   "User_String": MasterSetting["Default_String"]
                   } 
        
        self.SqlObject.InsertEntry(
                                   self.SqlCursor, 
                                   TableName, 
                                   Columns
                                   )   
        
        self.SqlObject.Commit(self.SqlCursor)

        return True
    
    def GetInternalUserId(self):
        # This methode will get the internal user id from the database.
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
    
    def GroupExists(self):
        # This method checks in the database if the group (if it is one) exists.
        #  The following query will return 1 if a user with the specified username exists, 0 otherwise.
        # 
        # SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'username')

        Exists = self.SqlObject.ExecuteTrueQuery(
                                          self.SqlObject.CreateCursor(Dictionary=False),
                                          Query="SELECT EXISTS(SELECT 1 FROM Group_Table WHERE External_Group_Id = %s);",
                                          Data=self.ChatId
                                          )[0][0]
                                          
        if Exists == True:
            return True
        else:
            return False
            
    def AddGroup(self):
        # This method will add the group if it doen't exit.
        self.SqlObject.InsertEntry(
                                   self.SqlCursor,
                                   TableName = "Group_Table",
                                   Columns = {
                                              "External_Group_Id": self.ChatId,
                                              "Group_Name": self.GroupName
                                              },
                                   )
        self.SqlObject.Commit(self.SqlCursor)
    
    def GetInternalGroupId(self):
        # This method will get the internal group id from the database so that
        # it can be used for evil.
        
        return self.SqlObject.SelectEntry(
                                          self.SqlCursor,
                                          FromTable = "Group_Table",
                                          Columns = ["Internal_Group_Id"],
                                          Where = [["External_Group_Id", "=", "%s"]],
                                          Data = self.ChatId
                                          )
    
    def InterpretMessage(self, ):
        # This methode will interpret and the message and do what ever is needed.
        # This variable is to be used later on

        MessageObject = messages.MessageClass.MessageToBeSend(ToChatId=self.ChatId)
        MessageObject.Text = self._("Sorry, but this command could not be interpreted.")
        # check if message is a command
        if self.Text != None:
            # delete the annoying bot command from the text to analyse
            BotName = "@{BotName}".format(BotName = self.BotName)
            # Analyse the text and do your stuf.
            
            # If the name of the bot is used in the 
            # command delete the @NameOfBot
            if BotName in self.Text:
                self.Text = self.Text.replace(BotName, "")
            if self.Text.startswith("/"):
               MessageObject = self.InterpretCommand(MessageObject)
            else:
                MessageObject = self.InterpresNonCommand(MessageObject)
        else:
            MessageObject = None
        return MessageObject

    def InterpretCommand(self, MessageObject):
         # register the command in the database for later use
        if self.Text == "/start":
            MessageObject.Text = self._("Welcome.\nWhat can I do for you?\nPress /help for all my commands")
        elif self.Text == "/newpoll":
            self.SetLastSendCommand("/newpoll")
            # Check if user has already a poll
            temp = self.SqlObject.ExecuteTrueQuery(
                                                   self.SqlObject.CreateCursor(Dictionary=False),
                                                   Query="SELECT EXISTS(SELECT 1 FROM poll_table WHERE Master_User_Id = %s)",
                                                   Data=self.InternalUserId
                                                   )[0][0] 
            if temp == False:
                MessageObject.Text = self._("Welcome to the poll creation, please follow the following steps.\n") + self._("Please enter the name of the new poll.")
            else:
                MessageObject.Text = self._("Please enter the name of the new poll.")

        elif self.Text == "/addanwser":
             # Get the polls
            Polls = self.GetUserPolls()
            MessageObject.Text = self._("Please choose the poll to add the poll to:")
            MessageObject.ReplyKeyboardMarkup(
                                              [Polls],
                                              OneTimeKeyboard=True
                                              )
            self.SetLastSendCommand("/addanwser NoPoll", None)
            
        elif self.Text == "/delanswer":
            pass
        elif self.Text == "/listpoll":
            pass
        elif self.Text == "/delpoll":
            pass
        elif self.Text == "/polllink":
            pass
        elif self.Text == "/done":
            LastSendCommand = self.GetLastSendCommand()
            LastUsedId = LastSendCommand["Last_Used_Id"]
            LastCommand = LastSendCommand["Command"]
            if LastCommmand == "/addanwser awnser":
                MessageObject.Text = self._("Thank you very much for adding the commands.\nDo you wnat to add this poll to a group?")
                MessageObject.ReplyKeyboardMarkup(
                                                  [
                                                   ["1. YES"],
                                                   ["2. NO"]
                                                   ],
                                                  OneTimeKeyboard=True
                                                  )
                self.SetLastSendCommand("/addtogroup", LastUsedId)
        elif self.Text == "/help":                
            MessageObject.Text = self._("Work in progress! @BetterPollBot is a bot similar to @PollBot, with more features and less spamming in groups.\n\ngeneral commands\n /help - display's this message\n /settings - display's you're own settings\n\npoll related commands\n /newpoll - creates a new poll\n /delpoll - deletes a selected poll\n /addanswer - adds a new answer to the selected poll\n /delanswer - deletes a selected answer\n /listpoll - see all your polls\n /polllink - get's the link to a selected poll\n /endpoll - ends a poll in a group\n /pollsettings - display's all the settings for a selected poll")
        elif self.Text == "/settings":
            # This command will sennd the possible setting to the user
            self.SetLastSendCommand("/settings", None)
            MessageObject.Text = self._("Please, choose the setting to change:")
            MessageObject.ReplyKeyboardMarkup(
                                              [
                                               ["/language"], 
                                               ["/comming soon"]
                                               ],
                                              OneTimeKeyboard=True
                                              )
        elif self.Text == "/language":
            # This option will change the user language
            # Set the last send command
                
            self.SetLastSendCommand("/language")
            
            MessageObject.Text = self._("Please choose your preferred language:")
            MessageObject.ReplyKeyboardMarkup([["English"],
                                               ["Deutsch"],
                                               ["Français"]
                                               ],
                                              OneTimeKeyboard=True
                                              )
        else:
               # send that the command is unnown
            pass
        
        return MessageObject
              
    def InterpresNonCommand(self, MessageObject):
        """
        This method interprets the non commands user text.
        
        This method is used as an interpreter of the system set 
        commands and the user send text. It returns the MessageObject
        after modifying it.
        
        Variables:
            MessageObejct - is the message obejct that has to be 
                modified
        """
        
        # Get the last send command and the last used id
        LastSendCommand = self.GetLastSendCommand()
        LastUsedId = LastSendCommand["Last_Used_Id"]
        LastCommand = LastSendCommand["Command"]
        
        if LastCommand != None:
            if LastCommand == "/language":
                self.ChangeUserLanguage(self.Text)
                MessageObject.Text = self._("Language changed successfully.")
                MessageObject.ReplyKeyboardHide()
                self.ClearLastCommand()
            elif LastCommand.startswith("/addanwser"):
                if LastCommand == "addawnser awnser":
                    Poll = messages.PollingClass.Poll(
                                             InternalUserId=self.InternalUserId,
                                             InternalPollId=PollId,
                                             LoggingObject=self.LanguageObject,
                                             SqlObject=self.SqlObject
                                            )
                    Poll.AddAnwser(self.Text)
                #elif LastCommand.startswith()
            elif LastCommand.startswith("/newpoll"):
                if LastCommand == "/newpoll":
                    Id = self.AddPoll()
                    if Id != False:
                        MessageObject.Text = self._("The poll \"{PollName}\" has been created, please enter the question to the poll.").format(PollName=self.Text)
                        self.SetLastSendCommand("/newpoll question", Id)
                    else:
                        MessageObject.Text = self._("The poll {PollName} allready exists.\nPress /list and on the poll to modify it.")
                elif LastCommand.startswith("/newpoll question"):

                    Poll = messages.PollingClass.Poll(
                                             InternalUserId=self.InternalUserId,
                                             InternalPollId=LastUsedId,
                                             LoggingObject=self.LanguageObject,
                                             SqlObject=self.SqlObject
                                             )

                    if Poll.UpdateQuestion(self.Text):
                        MessageObject.Text = self._("The question has been added.\nDo you want to add some anwsers to the question?")
                        MessageObject.ReplyKeyboardMarkup(
                                                          [
                                                           ["1. " + self._("YES")], 
                                                           ["2. " + self._("NO")]
                                                           ],
                                                          OneTimeKeyboard=True
                                                          )
                        self.SetLastSendCommand("/newpoll anwser", LastUsedId)
                elif LastCommand.startswith("/newpoll anwser"):
                    if self.Text.startswith("1."):
                        MessageObject.Text = self._("Please enter your first possible awnser to the question.")
                        MessageObject.ReplyKeyboardHide()
                        self.SetLastSendCommand("/addawnser awnser", LastUsedId)
                    elif self.Text.startswith("2. "):
                        MessageObject.Text = self._("You can add an awnser later via the /addawnser command.")
                        MessageObject.ReplyKeyboardHide()
                        self.ClearLastCommand()
                    
        return MessageObject
               
    def SetLastSendCommand(self, Command, LastUsedId = None):
        """
        This method will save the last user command into the database.
        
        The commands used can be set manuely from the programmer 
        so that it can be user for flow controll.
        
        Example:
            /Command option
        Variables:
            Command - this is the used command with the option
            LastUsedId - This is the last used id, it can be
                every id, depending the situation.
        """
        
        TableName = "Session_Table"
        Columns = {
                   "Command_By_User": self.InternalUserId,
                   "Command": Command,

                   }

            
        Duplicate = {
                     "Command": Command,

                     }
        if LastUsedId != None:
            Columns["Last_Used_Id"] = LastUsedId
            Duplicate["Last_Used_Id"] = LastUsedId
            
        SetLastSendCommand = self.SqlObject.InsertEntry(
                                                        self.SqlCursor,
                                                        TableName=TableName,
                                                        Columns=Columns,
                                                        Duplicate=Duplicate)
        self.SqlObject.Commit(self.SqlCursor)
    
    def GetLastSendCommand(self):
        """
        This method will get the last user command.
        
        This method will get the last user command from the database,
        so that the last command can be used for flow controll. 
        The command are mostly set by the system and not by the user,
        at least not direct.
        
        Example:
            /command option
            
        Variables:
            -
        """

        
        FromTable = "Session_Table"
        Columns = ["Command", "Last_Used_Id"]
        Where = [["Command_By_User", "=", "%s"]]
        Data = (self.InternalUserId)
        LastSendCommand = self.SqlObject.SelectEntry(self.SqlCursor,
                                                     FromTable=FromTable,
                                                     Columns=Columns,
                                                     Where=Where,
                                                     Data=Data
                                                     )
        if len(LastSendCommand) > 0:
            return LastSendCommand[0]
        
        return None
    
    def ClearLastCommand(self):
        """
        This method clears the last set command if the process finished.
        
        Variables:
            -
        """

        self.SqlObject.UpdateEntry(
                                   Cursor=self.SqlCursor,
                                   TableName="Session_Table",
                                   Columns={
                                            "Command": "0",
                                            "Last_Used_Id": 0
                                            },
                                   Where=[["Command_By_User", self.InternalUserId]],
                                   Autocommit=True
                                   )

    def ChangeUserLanguage(self, Language):
        """
        This method changes the user language.
        
        This method is responsible for initialising the language change, 
        as well as activating the new language. It will return True
        if the new language could be initialied and False if there has 
        been an error.
        
        Variables:
            Language - should be a string with the new language file
        """
        
        if Language == "English":
            Language = "en_US"
        elif Language == "Deutsch":
            Language = "de_De"

        self.SqlObject.UpdateEntry(
                                   Cursor=self.SqlCursor,
                                   TableName="User_Setting_Table",
                                   Columns={"User_String": Language},
                                   Where=[["Master_User_Id", self.InternalUserId]],
                                   Autocommit=True
                                   )
        try:
            self.LanguageName = Language
            self.LanguageObject = language.LanguageClass.CreateTranslationObject(Language)
            self._ = self.LanguageObject.gettext
            if self.LanguageObject.info()["language"]!= Language:
                raise ErrorClasses.LanguageImportError("")
            return True
        except ErrorClasses.LanguageImportError as Error:
            self.LoggingObject.error(self.M_("There has been an error with the changing of the language class, this error has been returned: {Error}").format(Error = Error)
                                     + " " + self.M_("Please, contact your administrator."))
            return False
    
    def AddPoll(self,):
        """ 
        This method adds the new poll to the system.
        
        First check if that poll exists, a poll name can only be 
        used once per person so that will be no confusion between 
        multiple poll per person. It will return the new internal poll
        id, if the process has been a success and the poll name is 
        unique otherwise it returns a False.
        
        Variables:
            -
        """
        IfExists = self.SqlObject.ExecuteTrueQuery(
                                                   self.SqlObject.CreateCursor(Dictionary=False),
                                                   Query="SELECT EXISTS(SELECT 1 FROM Poll_Table WHERE `Poll_Name` = %(PollName)s AND `Master_User_Id` = %(UserID)s);",
                                                   Data={
                                                         "PollName": self.Text,
                                                         "UserID": self.InternalUserId
                                                         }
                                                   )[0][0]
        if IfExists == False:
            import hashlib
            self.SqlObject.InsertEntry(
                                       self.SqlCursor,
                                       TableName="Poll_Table",
                                       Columns={
                                                "Poll_Name":self.Text,
                                                "Master_User_Id": self.InternalUserId
                                                },
                                       AutoCommit=False)
            # self.SqlObject.Commit(self.SqlCursor)
            Id = self.SqlObject.GetLastRowId(self.SqlCursor)

            # get last Id for the md5-hash needed for the talk
            Hash = hashlib.md5()
            Hash.update(str(Id).encode(encoding='utf_8', errors='strict'))
            Hash = Hash.hexdigest().encode("utf-8")
    
            self.SqlObject.UpdateEntry(
                                  self.SqlCursor,
                                  TableName="Poll_Table",
                                  Columns={
                                             "External_Poll_Id": Hash,
                                             },
                                  Where=[["Internal_Poll_Id", Id]],
                                  Autocommit=False
                                  )
            
            self.SqlObject.Commit(self.SqlCursor)
            return Id
        else:
            return False
        
    def GetUserPolls(self):
        """ 
        Get all user polls and return them in a list.
        
        This method will get all the allready created polls and 
        will return them, if the user has no polls the system will
        return a False.
        
        Variables:
            -
        """
        Polls = self.SqlObject.SelectEntry(
                                   self.SqlCursor,
                                   FromTable = "Poll_Table",
                                   Columns = ("Poll_Name",), 
                                   Where = [["Master_User_Id", "=", "%s"]], 
                                   Data = (self.InternalUserId),
                                   )
        temp = []
        for Index in Polls: 
            for Key in Index.keys():
                temp.append(Index[Key])
        Polls = sorted(temp)
        
        if len(Polls)>0:
            return Polls
        else: 
            return False