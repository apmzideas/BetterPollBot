#!/usr/bin/python
# -*- coding: utf-8 -*-

# The custom modules
import GlobalObjects
import ErrorClasses
import LoggingClass
import language.LanguageClass  # imports the _() function! (the translation feature).
import parsers.ConfigurationClass
import TelegramClass
from . import PollingClass  # imports in the same folder (module)
from . import MessageClass
from . import EmojiClass


class MessageProcessor(object):
    """
    This class is used as the user message analyser.
    
    The MessageObject will only contains a single message object, 
    so that this class will be thread save and so that we can run
    multiple instances per unit.    
    
    The message object will contain all the following parts.\n
    .. code-block:: python\n
        {
                       'message': {
                                   'date': 1439471738, 
                                   'text': '/newpoll',
                                   'from': {
                                            'id': 3xxxxxx6,
                                            'last_name': 'Sample',
                                            'first_name': 'Max',
                                            'username': 'TheUserName'
                                            }, 
                                   'message_id': 111, 
                                   'chat': {
                                            'id': -xxxxxxx,
                                            'title': 'Drive'
                                            }
                                   },
                        'update_id': 469262057
                        }
        }
    
    """

    def __init__(self, MessageObject, **OptionalObjects):
        """
        Variables:
            MessageObject                 ``object``
                the message to be analysed message
                
            OptionalObjects                ``object``
                Just some optional objects for example the logging
                object, the configuration object, the sql object with 
                the connection commands and the master language object, 
                that is used for the logging in the correct language.
        """

        # Predefining attributes so that it later can be used for evil.
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
            self.ConfigurationObject = (
                parsers.ConfigurationClass.ConfigurationParser()
            )

        if "SqlObject" in OptionalObjects:
            self.SqlObject = OptionalObjects["SqlObject"]

            # The object get's it's own cursor so that there will be no 
            # problems in the future making the system multi threading safe.
            self.SqlCursor = self.SqlObject.CreateCursor()

        else:
            self.LoggingObject.error(self._("The sql object is missing, please"
                                            " contact your administrator.")
                                     )
            raise ValueError(self._("The sql object is missing, please contact"
                                    " your administrator.")
                             )

        # This variable is needed for the logger so that the log end up 
        # getting printed in the correct language.
        if "LanguageObject" in OptionalObjects:
            self.M_ = OptionalObjects["LanguageObject"].gettext
        else:
            self.M_ = language.LanguageClass.CreateTranslationObject()

        if "BotName" in OptionalObjects:
            # The name of the bot that is doing it's job.
            self.BotName = OptionalObjects["BotName"]["result"]["username"]
        else:
            self.BotName = GlobalObjects.__AppName__

        if "update_id" in MessageObject:
            # The update‘s unique identifier. Update identifiers start from a
            # certain positive number and increase sequentially. This ID
            # becomes especially handy if you’re using web hooks, since it
            # allows you to ignore repeated updates or to restore the correct
            # update sequence, should they get out of order.
            self.UpdateId = MessageObject["update_id"]

        if "message_id" in MessageObject["message"]:
            # Unique message identifier
            self.MessageID = MessageObject["message"]["message_id"]

        # get the user of the message
        # get user data from the message
        if "first_name" in MessageObject["message"]["from"]:
            # User‘s or bot’s first name
            self.UserFirstName = MessageObject["message"]["from"]["first_name"]
        else:
            self.UserFirstName = ""

        if "last_name" in MessageObject["message"]["from"]:
            # Optional. User‘s or bot’s last name
            self.UserLastName = MessageObject["message"]["from"]["last_name"]
        else:
            self.UserLastName = ""

        if "username" in MessageObject["message"]["from"]:
            # Optional. User‘s or bot’s username
            self.UserName = MessageObject["message"]["from"]["username"]
        else:
            self.UserName = ""

        if "id" in MessageObject["message"]["from"]:
            # Unique identifier for this user or bot
            self.UserId = MessageObject["message"]["from"]["id"]

        # Add user to the system if not exists
        if self.UserExists() is False:
            self.AddUser()

        # Get the Internal user id
        self.InternalUserId = self.GetInternalUserId()

        # Here we are initialising the function for the translations.
        # Get the user settings from the user that has send the message
        Query = ("SELECT User_Setting_Table.User_String FROM "
                 "User_Setting_Table INNER JOIN Setting_Table ON "
                 "User_Setting_Table.Master_Setting_Id="
                 "Setting_Table.Setting_Id WHERE Setting_Table.Setting_Name=%s"
                 " AND User_Setting_Table.Master_User_Id=%s;"
                 )

        Data = ("Language", self.InternalUserId)

        self.LanguageName = (
            self.SqlObject.ExecuteTrueQuery(
                self.SqlCursor,
                Query,
                Data
            )[0]["User_String"])

        self.LanguageObject = language.LanguageClass.CreateTranslationObject(
            Languages=[self.LanguageName]
        )

        # create the translator        
        self._ = self.LanguageObject.gettext

        # Get the text message with the command
        if "text" in MessageObject["message"]:
            self.Text = MessageObject["message"]["text"]
        else:
            self.Text = None

        # where was the message send from the user or the group
        # Get the chat id
        if "id" in MessageObject["message"]["chat"]:
            # Unique identifier for this group chat
            self.ChatId = MessageObject["message"]["chat"]["id"]

        # Check if message is from a group or not.
        if self.ChatId == self.UserId:
            self.InGroup = False
        else:
            self.InGroup = True
            self.GroupName = MessageObject["message"]["chat"]["title"]
            # Check if group exists
            if self.GroupExists() is False:
                self.AddGroup()
            self.InternalGroupId = self.GetInternalGroupId()

        if "date" in MessageObject["message"]:
            # Optional. For forwarded messages, sender of the original message
            self.MessageDate = MessageObject["message"]["date"]

        if "forward_from" in MessageObject["message"]:
            self.ForwardedFrom = MessageObject["message"]["forward_from"]

        if "forward_date" in MessageObject["message"]:
            # Optional. For forwarded messages, date the original
            # message was sent in Unix time
            self.forward_date = MessageObject["message"]["forward_from"]

        if "reply_to_message" in MessageObject["message"]:
            # Optional. For replies, the original message. Note that
            # the Message object in this field will not contain further
            # reply_to_message fields even if it itself is a reply.
            self.ReplyToMessage = MessageObject["message"]["reply_to_message"]

        if "audio" in MessageObject["message"]:
            # Optional. Message is an audio file, information about the file
            self.MessageAudio =  MessageObject["message"]["audio"]

        if "document" in MessageObject["message"]:
            # Optional. Message is a general file, information about the file
            self.MEssageDocument = MessageObject["message"]["document"]

        if "photo" in MessageObject["message"]:
            # Optional. Message is a photo, available sizes of the photo
            self.MessagePhoto = MessageObject["message"]["photo"]

        if "sticker" in MessageObject["message"]:
            # Optional. Message is a sticker, information about the sticker
            self.MessageSticker = MessageObject["message"]["sticker"]

        if "video" in MessageObject["message"]:
            # Optional. Message is a video, information about the video
            self.MessageVideo = MessageObject["message"]["video"]

        if "caption" in MessageObject["message"]:
            # Optional. Caption for the photo or video
            self.MessageCaption = MessageObject["message"]["caption"]

        if "contact" in MessageObject["message"]:
            # Optional. Message is a shared contact, information about
            # the contact
            self.MessageContact = MessageObject["message"]["contact"]

        if "location" in MessageObject["message"]:
            # Optional. Message is a shared location, information about
            # the location
            self.MessageLocation = MessageObject["message"]["location"]

        if "new_chat_participant" in MessageObject["message"]:
            # Optional. A new member was added to the group, information
            #  about them (this member may be bot itself)
            self.MessageNewChatParticipant = (
                MessageObject["message"]["new_chat_participant"]
            )

        if "left_chat_participant" in MessageObject["message"]:
            # Optional. A member was removed from the group, information
            # about them (this member may be bot itself)
            self.MessageLeftChatParticipant = (
                MessageObject["message"]["left_chat_participant"]
            )

        if "new_chat_title" in MessageObject["message"]:
            # Optional. A group title was changed to this value
            self.MessageNewChatTitle = (
                MessageObject["message"]["new_chat_title"]
            )

        if "new_chat_photo" in MessageObject["message"]:
            # Optional. A group photo was change to this value
            self.MessageNewChatPhoto = (
                MessageObject["message"]["new_chat_photo"]
            )

        if "delete_chat_photo" in MessageObject["message"]:
            # Optional. Informs that the group photo was deleted
            self.MessageDeleteChatPhoto = (
                MessageObject["message"]["delete_chat_photo"]
            )

        if "group_chat_created" in MessageObject["message"]:
            # Optional. Informs that the group has been created
            self.MessageGroupChatCreated = (
                MessageObject["message"]["group_chat_created"]
            )

    def UserExists(self, ):
        """
        This method will detect if the use already exists or not.
        
        The following query will return 1 if a user with the specified 
        username exists a 0 otherwise.
        
        .. code-block:: sql\n
            SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'username')
        
        It will return a True if the database returns a 1 and a False
        if the database a 0.
        Variables:
            \-
        """

        exists = self.SqlObject.ExecuteTrueQuery(
            self.SqlObject.CreateCursor(Dictionary=False),
            Query=("SELECT EXISTS(SELECT 1 FROM User_Table WHERE"
                   " External_User_Id = %s);"
                   ),
            Data=self.UserId
        )[0][0]

        if exists is False:
            return False
        else:
            return True

    def AddUser(self, ):
        """
        This method will add a new user to the database.
        
        Variables:
            \-
        """
        # Insert into user
        TableName = "User_Table"
        Columns = {
            "External_User_Id": self.UserId,
            "User_Name": self.UserName,
            "First_Name": self.UserFirstName,
            "Last_Name": self.UserLastName
        }

        self.SqlObject.InsertEntry(self.SqlCursor, TableName, Columns)
        self.SqlObject.Commit(self.SqlCursor)

        # insert default settings
        # get default values

        # get the default settings
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

    def GetInternalUserId(self):
        """
        This method will get the internal user id from the database.
        
        This method will return the internal user id directly.
        
        Variables:
            \-
        """
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
        """
        This method checks if the group exists or not.
        
        The following query will return a 1 if a user with the 
        specified username exists a 0 otherwise. From that on
        the system will return True if the group exists and if it
        doesn't False.\n
        .. code-block:: sql\n
            SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'username')
        
        Variables:
            \-
        """

        # This method checks in the database if the group (if it is one)
        # exists.


        Exists = self.SqlObject.ExecuteTrueQuery(
            self.SqlObject.CreateCursor(Dictionary=False),
            Query="SELECT EXISTS(SELECT 1 FROM Group_Table WHERE"
                  " External_Group_Id = %s);",
            Data=self.ChatId
        )[0][0]

        if Exists == True:
            return True
        else:
            return False

    def AddGroup(self):
        """
        This method will add an not existing group to the database.
        
        Variables:
            \-
        """
        # This method will add the group if it doen't exit.
        self.SqlObject.InsertEntry(
            self.SqlCursor,
            TableName="Group_Table",
            Columns={
                "External_Group_Id": self.ChatId,
                "Group_Name": self.GroupName
            },
        )
        self.SqlObject.Commit(self.SqlCursor)

    def GetInternalGroupId(self):
        """
        This method will get the user internal group id.
        
        This method will return the the internal group id directly from
        the database.
        Variables:
            \-
        """

        return self.SqlObject.SelectEntry(
            self.SqlCursor,
            FromTable="Group_Table",
            Columns=["Internal_Group_Id"],
            Where=[["External_Group_Id", "=", "%s"]],
            Data=self.ChatId
        )

    def SetLastSendCommand(self, Command, LastUsedId=None):
        """
        This method will save the last user command into the database.
        
        The commands used can be set manually from the programmer
        so that it can be user for flow control.
        
        Example:\n
        .. code-block:: guess\n
            /Command option
            
        Variables:
            Command                       ``string``
                this is the used command with the option
                
            LastUsedId                    ``integer``
                This is the last used id, it can be every id, depending 
                the situation.
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
        self.SqlObject.Commit()

    def GetLastSendCommand(self):
        """
        This method will get the last user command.
        
        This method will get the last user command from the database,
        so that the last command can be used for flow control.
        The command are mostly set by the system and not by the user,
        at least not direct.
        
        Example:\n
        .. code-block:: guess\n
            /command option
            
        Variables:
            \-
        """

        FromTable = "Session_Table"
        Columns = ["Command", "Last_Used_Id"]
        Where = [["Command_By_User", "=", "%s"]]
        Data = (self.InternalUserId,)
        LastSendCommand = self.SqlObject.SelectEntry(
            self.SqlCursor,
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
            \-
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
        if the new language could be initialised and False if there has
        been an error.
        
        Variables:
            Language                      string
                should be a string with the new language file
        """

        if Language == "English":
            Language = "en_US"
        elif Language == "Deutsch":
            Language = "de_DE"

        self.SqlObject.UpdateEntry(
            Cursor=self.SqlCursor,
            TableName="User_Setting_Table",
            Columns={"User_String": Language},
            Where=[["Master_User_Id", self.InternalUserId]],
            Autocommit=True
        )
        try:
            self.LanguageName = Language
            self.LanguageObject = (
                language.LanguageClass.CreateTranslationObject(
                    self.LanguageName
                )
            )

            self._ = self.LanguageObject.gettext
            if self.LanguageObject.info()["language"] != Language:
                raise ErrorClasses.LanguageImportError(
                    self.M_("Unknown Error")
                )
            return True
        except ErrorClasses.LanguageImportError as Error:
            self.LoggingObject.error(
                self.M_("There has been an error with the changing of the "
                        "language class, this error has been returned: {Error}"
                        ).format(Error=Error) +
                " " + self.M_("Please, contact your administrator.")
            )
            return False

    def AddPoll(self, ):
        """ 
        This method adds the new poll to the system.
        
        First check if that poll exists, a poll name can only be 
        used once per person so that will be no confusion between 
        multiple poll per person. It will return the new internal poll
        id, if the process has been a success and the poll name is 
        unique otherwise it returns a False.
        
        Variables:
            \-
        """
        IfExists = self.SqlObject.ExecuteTrueQuery(
            self.SqlObject.CreateCursor(Dictionary=False),
            Query=("SELECT EXISTS(SELECT 1 FROM Poll_Table WHERE `Poll_Name`"
                   " = %(PollName)s AND `Master_User_Id` = %(UserID)s);"
                   ),
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
                    "Poll_Name": self.Text,
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
        
        This method will get all the already created polls and
        will return them, if the user has no polls the system will
        return a None.
        
        Variables:
            \-
        """
        Polls = self.SqlObject.SelectEntry(
            self.SqlCursor,
            FromTable="Poll_Table",
            Columns=("Poll_Name",),
            Where=[["Master_User_Id", "=", "%s"]],
            Data=(self.InternalUserId),
        )
        temp = []
        for Index in Polls:
            for Key in Index.keys():
                temp.append(Index[Key])
        Polls = sorted(temp)

        if len(Polls) > 0:
            return Polls
        else:
            return None

    def InterpretMessage(self):
        """
        This method interprets the user text.

        This method is used as an pre interpreter of the user send text.
        It primarily chooses if the user send text is a command or not.
        It will choose the correct interpretation system, if the text has
        been send by a group or not.
        It returns the MessageObject after letting it get modified.

        Variables:
            \-
        """

        MessageObject = MessageClass.MessageToBeSend(ToChatId=self.ChatId)
        MessageObject.Text = self._("Sorry, but this command could not be"
                                    " interpreted.")
        # check if message is a command

        if self.Text is not None:
            # delete the annoying bot command from the text to analyse
            BotName = "@{BotName}".format(BotName=self.BotName)
            # Analyse the text and do your stuff.

            # If the name of the bot is used in the
            # command delete the @NameOfBot
            if BotName in self.Text:
                self.Text = self.Text.replace(BotName, "")

            if self.InGroup is False:
                if self.Text.startswith("/"):
                    MessageObject = self.InterpretUserCommand(MessageObject)
                else:
                    MessageObject = self.InterpretUserNonCommand(MessageObject)
            else:
                if self.Text.startswith("/"):
                    MessageObject = self.InterpretGroupCommand(MessageObject)
                else:
                    MessageObject = self.InterpretGroupNonCommand(
                        MessageObject
                    )
        else:
            MessageObject = None

        return MessageObject

    def InterpretUserCommand(self, MessageObject):
        """
        This method interprets the commands form the user text.

        This method is used as an interpreter of the user send
        commands. It returns the MessageObject
        after analysing and modifying the MessageObject to respond
        the user Text.

        Variables:
            MessageObject                 ``object``
                is the message object that has to be modified
        """
        # register the command in the database for later use
        if self.Text.startswith("/start"):
            Parts = self.Text.split(" ")
            if len(Parts) <= 1:
                MessageObject.Text = self._("Welcome.\nWhat can I do for you?"
                                            "\nPress /help for all my commands"
                                            )
            else:
                if Parts[1] == "addpoll":
                    self.Text = "/newpoll"
                    MessageObject = self.InterpretUserCommand(MessageObject)
                else:
                    pass
        elif self.Text == "/newpoll":

            # Check if user has already a poll
            temp = self.SqlObject.ExecuteTrueQuery(
                self.SqlObject.CreateCursor(Dictionary=False),
                Query="SELECT EXISTS(SELECT 1 FROM poll_table"
                      " WHERE Master_User_Id = %s)",
                Data=self.InternalUserId
            )[0][0]
            if temp is False:
                MessageObject.Text = self._(
                    "Welcome to the poll creation, please follow the following"
                    " steps.\n") + self._("Please enter the name of the new"
                                          " poll."
                                          )
            else:
                MessageObject.Text = self._("Please enter the name of the new "
                                            "poll."
                                            )
            self.SetLastSendCommand("/newpoll")

        elif self.Text == "/addanswer":
            # Get the polls
            Polls = self.GetUserPolls()
            if len(Polls)>0:
                MessageObject.Text = self._("Please choose the poll to add the"
                                            " answer to:"
                                            )
                MessageObject.ReplyKeyboardMarkup(
                    [Polls],
                    OneTimeKeyboard=True
                )
                self.SetLastSendCommand("/addanswer pollsearch")
            else:
                # there are no polls to add to a group
                MessageObject.Text = self._("Sorry but there are no poll in "
                                            "your database.\n Do you want to "
                                            "add some?"
                                            )
                MessageObject.ReplyKeyboardMarkup([
                    [self._("YES")],
                    [self._("NO")]
                ],
                    OneTimeKeyboard=True
                )
                self.SetLastSendCommand("/newpoll unclear", None)

        elif self.Text == "/delanswer":
            Polls = self.GetUserPolls()

            if len(Polls)>0:
                MessageObject.Text = self._(
                    "Please choose the poll to delete the answer from.\n"
                    "Attention if you delete the answer to the poll, the "
                    "results to from that poll will be false."
                )
                MessageObject.ReplyKeyboardMarkup(
                    [Polls],
                    OneTimeKeyboard=True
                )
                self.SetLastSendCommand("/delanswer poll")
            else:
                MessageObject.Text = self._(
                    "Sorry, you have no polls with answers to delete...\n"
                    "Please add a poll with answers so that you can delete "
                    "them again."
                )


        elif self.Text == "/listpoll":
            Polllist = "\n".join(["-" + i for i in self.GetUserPolls()])
            MessageObject.Text = self._("Here is the list with all your polls:"
                                        "\n{Polllist}").format(
                Polllist = Polllist
            )
        elif self.Text == "/delpoll":
            pass
        elif self.Text == "/polllink":
            # This command will give the system the chance to include itself
            # into a group.
            # First check if user has a poll to add to a group.
            Polls = self.GetUserPolls()

            if len(Polls)>1:
                # if some polls exist add them to the system
                MessageObject.Text = self._("Please choose the poll to add to "
                                            "the group:"
                                            )
                MessageObject.ReplyKeyboardMarkup(
                    [Polls],
                    OneTimeKeyboard=True
                )

                self.SetLastSendCommand("/polllink poll", None)

            elif len(Polls)<1:
                # there are no polls to add to a group
                MessageObject.Text = self._("Sorry but there are no poll in "
                                            "your database.\nDo you want to "
                                            "add some?"
                                            )
                MessageObject.ReplyKeyboardMarkup([
                    [self._("YES")],
                    [self._("NO")]
                ],
                    OneTimeKeyboard=True
                )
                self.SetLastSendCommand("/newpoll unclear", None)

        elif self.Text == "/done":
            LastSendCommand = self.GetLastSendCommand()
            LastUsedId = LastSendCommand["Last_Used_Id"]
            LastCommand = LastSendCommand["Command"]
            if LastCommand == "/addanswer answer":
                MessageObject.Text = self._(
                    "Thank you very much for adding the commands.\nDo you want"
                    " to add this poll to a group?"
                )
                MessageObject.ReplyKeyboardMarkup(
                    [
                        [self._("YES")],
                        [self._("NO")]
                    ],
                    OneTimeKeyboard=True
                )
                self.SetLastSendCommand("/polllink unclear", LastUsedId)
        elif self.Text == "/help":
            MessageObject.Text = self._(
                "Work in progress! @BetterPollBot is a bot similar to @PollBot"
                ", with more features and less spamming in groups.\n\ngeneral"
                " commands\n /help - display's this message\n /settings - "
                "display's you're own settings\n\npoll related commands\n "
                "/newpoll - creates a new poll\n /delpoll - deletes a selected"
                " poll\n /addanswer - adds a new answer to the selected poll"
                "\n /delanswer - deletes a selected answer\n /listpoll - see "
                "all your polls\n /polllink - get's the link to a selected "
                "poll\n /endpoll - ends a poll in a group\n /pollsettings - "
                "display's all the settings for a selected poll"
            )
        elif self.Text == "/settings":
            # This command will send the possible setting to the user
            self.SetLastSendCommand("/settings", None)
            MessageObject.Text = self._("Please, choose the setting to change:"
                                        )
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

            MessageObject.Text = self._(
                "Please choose your preferred language:"
            )
            MessageObject.ReplyKeyboardMarkup([
                ["English"],
                ["Deutsch"],
                ["Français"]
            ],
                OneTimeKeyboard=True
            )
        else:
            # send that the command is unknown
            pass

        return MessageObject

    def InterpretUserNonCommand(self, MessageObject):
        """
        This method interprets the non commands from user text.

        This method is used as an interpreter of the system set
        commands and the user send text. It returns the MessageObject
        after modifying it.

        Variables:
            MessageObject                 ``object``
                is the message object that has to be modified
        """

        # Get the last send command and the last used id
        LastSendCommand = self.GetLastSendCommand()
        LastUsedId = LastSendCommand["Last_Used_Id"]
        LastCommand = LastSendCommand["Command"]

        if LastCommand is None:
            # if there is nothing return de default.
            return MessageObject

        if LastCommand == "/language":
            self.ChangeUserLanguage(self.Text)
            MessageObject.Text = self._("Language changed successfully.")
            MessageObject.ReplyKeyboardHide()
            self.ClearLastCommand()

        elif LastCommand.startswith("/addanswer"):  # /addanswer NoPoll
            if LastCommand == "/addanswer answer":
                Poll = PollingClass.Poll(
                    InternalUserId=self.InternalUserId,
                    InternalPollId=LastUsedId,
                    LoggingObject=self.LanguageObject,
                    SqlObject=self.SqlObject
                )
                Poll.AddAnwser(self.Text)
                MessageObject.Text = self._(
                    "The answer has been added, please add a additional answer"
                    " to stop adding answers press /done or enter it."
                )

                self.SetLastSendCommand("/addanswer answer", Poll.InternalPollId)

            elif LastCommand == "/addanswer pollsearch":
                Poll = PollingClass.Poll(
                    InternalUserId=self.InternalUserId,
                    PollName=self.Text,
                    LoggingObject=self.LanguageObject,
                    SqlObject=self.SqlObject
                )
                Poll.GetPollByName()
                self.SetLastSendCommand("/addanswer answer",
                                        Poll.InternalPollId
                                        )
                MessageObject = self.InterpretMessage()

        elif LastCommand.startswith("/newpoll"):
            if LastCommand == "/newpoll":
                Id = self.AddPoll()
                if Id != False:
                    MessageObject.Text = self._("The poll \"{PollName}\" has"
                                                " been created, please enter "
                                                "the question to the poll."
                                                ).format(PollName=self.Text)

                    self.SetLastSendCommand("/newpoll question", Id)
                else:
                    MessageObject.Text = self._("The poll {PollName} already "
                                                "exists.\nPress /list and on "
                                                "the poll to modify it."
                                                )

            elif LastCommand == "/newpoll unclear":
                if self.Text == self._("YES"):
                    MessageObject.Text = self._("")
                elif self.Text == self._("NO"):
                    pass

            elif LastCommand.startswith("/newpoll question"):

                Poll = PollingClass.Poll(
                    InternalUserId=self.InternalUserId,
                    InternalPollId=LastUsedId,
                    LoggingObject=self.LanguageObject,
                    SqlObject=self.SqlObject
                )

                if Poll.UpdateQuestion(self.Text):
                    MessageObject.Text = self._("The question has been added."
                                                "\nDo you want to add some "
                                                "answers to the question?"
                                                )
                    MessageObject.ReplyKeyboardMarkup(
                        [
                            [self._("YES")],
                            [self._("NO")]
                        ],
                        OneTimeKeyboard=True
                    )
                    self.SetLastSendCommand("/newpoll answer", LastUsedId)
                else:
                    raise Exception
            elif LastCommand.startswith("/newpoll answer"):
                if self.Text == self._("YES"):
                    # add the first possible answer to the system and arrange
                    # the rest of the process.
                    MessageObject.Text = self._("Please enter your first "
                                                "possible answer to the "
                                                "question."
                                                )
                    MessageObject.ReplyKeyboardHide()

                    self.SetLastSendCommand("/addanswer answer", LastUsedId)

                elif self.Text == self._("NO"):
                    MessageObject.Text = self._("You can add an answer later "
                                                "via the /addanswer command."
                                                )
                    MessageObject.ReplyKeyboardHide()
                    self.ClearLastCommand()

        elif LastCommand.startswith("/polllink"):
            # Send the Url to add the poll to the group.
            URL = ""
            if LastCommand == "/polllink poll":
                Poll = PollingClass.Poll(
                    InternalUserId=self.InternalUserId,
                    PollName=self.Text,
                    LoggingObject=self.LanguageObject,
                    SqlObject=self.SqlObject
                )
                Poll.GetPollByName()
                URL = Poll.GenerateURL(self.BotName)

            elif LastCommand == "/polllink unclear":
                if self.Text == self._("YES"):
                    Poll = PollingClass.Poll(
                        InternalUserId=self.InternalUserId,
                        InternalPollId=LastUsedId,
                        LoggingObject=self.LanguageObject,
                        SqlObject=self.SqlObject
                    )
                    URL = Poll.GenerateURL(self.BotName)
                elif self.Text == self._("NO"):
                    MessageObject.Text = self._(
                        "You can add the poll later via the /polllink command."
                    )
                    MessageObject.ReplyKeyboardHide()
            else:
                Poll = PollingClass.Poll(
                    InternalUserId=self.InternalUserId,
                    InternalPollId=LastUsedId,
                    LoggingObject=self.LanguageObject,
                    SqlObject=self.SqlObject
                )
                URL = Poll.GenerateURL(self.BotName)

            MessageObject.Text = self._("Press the following link to add the"
                                        " poll to a group:\n{GroupURL}"
                                        ).format(GroupURL=URL)
            self.ClearLastCommand()

        return MessageObject

    def InterpretGroupCommand(self, MessageObject):
        """
        This command will interpret all the group send commands.

        Variables:
            MessageObject                 ``object``
                is the message object that has to be modified
        """
        if self.Text.startswith("/start"):
            # if the text starts with the /start command
            # first detect if the command is send with a
            # group id (external version)
            # else send a standard start hello what can
            # I do for you?
            Parts = self.Text.split(" ")
            if len(Parts) > 1:
                Poll = PollingClass.Poll(
                    InternalUserId=self.InternalUserId,
                    ExternalPollId=Parts[1],
                    LoggingObject=self.LanguageObject,
                    SqlObject=self.SqlObject
                )
                Poll.GetPollByExternalId()
                PollQuestion = Poll.GetPollQuestion()
                OptionsOrg = Poll.GetAllOptions()
                Options = (
                    "\n".join([str((i+1))+". " + " ".join(OptionsOrg[i])
                               for i in range(len(OptionsOrg))])
                )

                MessageObject.Text = self._(
                    "{Question}\n{Options}").format(
                    Question=PollQuestion,
                    Options=Options
                )
                MessageObject.ReplyKeyboardMarkup(
                    OptionsOrg,
                    OneTimeKeyboard=True
                )
                MessageObject.ForceReply()

            else:
                URL = "{BaseUrl}/{AppName}?start=addpoll".format(
                    BaseUrl = TelegramClass.TelegramAPI.BASE_URL,
                    AppName=self.BotName
                )
                MessageObject.Text = self._(
                    "Work in progress! @BetterPollBot is a bot similar to "
                    "@PollBot, with more features and less spamming in groups."
                    "\nPress here to add a new poll\n{BetterPollBotURL}"
                ).format(BetterPollBotURL=URL)

        elif self.Text == "/help":
            MessageObject.Text = self._(
                "Work in progress! @BetterPollBot is a bot similar to "
                "@PollBot, with more features and less spamming in groups.\n"
                "general commands\n /help - display's this message\n \n poll "
                "related commands\n /polls – displays all "
                "the available polls for this group\n /results – shows the"
                " temporary results\n /endpoll - close poll and show final "
                "results\n"
            )

        elif self.Text == "/results":
            pass
        elif self.Text == "/endpoll":
            pass

        return MessageObject

    def InterpretGroupNonCommand(self, MessageObject):
        """
        This command will interpret all the group send non commands.

        Variables:
            MessageObject                 ``object``
                is the message object that has to be modified
        """
        raise NotImplementedError
        return MessageObject
