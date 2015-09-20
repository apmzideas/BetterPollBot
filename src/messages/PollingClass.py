#!/usr/bin/python
# -*- coding: utf-8 -*-

import GlobalObjects
import hashlib
import sql.SqlClass
import LoggingClass

class Poll(object):
    """
    In this class all the methodes needed for the poll will be stored.
    """

    def __init__(self, 
                 InternalUserId = None, 
                 InternalPollId = None,
                 ExternalPollId = None,
                 PollName = None,
                 **OptionalObjects
                 ):
        """
        The init method of the class
        
        Variables:
            InternalUserId                ``None or integer``
                stores the internal user id
                
            InternalPollId                ``None or integer``
                stores the internal poll id
            
            OptionalObjects               ``dictionary``
                holds all the additional objects like:
                    LoggingObject         ``object``
                        holds the logging object
                    
                    SqlObject             ``object``
                        holds the sql connection object
                        
        """
        
        self.InternalUserId = InternalUserId
        
        self.InternalPollId = InternalPollId
        
        self.ExternalPollId = ExternalPollId
        
        self.PollName = PollName
        
        # Predefining attribute so that it later can be used for evil.
        self.LoggingObject = None
        
        # SqlObjects
        self.SqlObject = None
        self.SqlCursor = None
        
        if "LoggingObject" in OptionalObjects:
            self.LoggingObject = OptionalObjects["LoggingObject"]
        else:
            self.LoggingObject = LoggingClass.Logger()

        if "SqlObject" in OptionalObjects:
            self.SqlObject = OptionalObjects["SqlObject"]
            
            # The object get's it's own cursor so that there will be no 
            # problems in the future making the system multi threading
            # safe.
            self.SqlCursor = self.SqlObject.CreateCursor()
        
    def UpdateQuestion(self, Question):
        """
        This method adds or modifies a question from the specific poll.
        
        Variables:
            Question                      ``string``
                holds the question given by the user
        """

        self.SqlObject.UpdateEntry(
                                   self.SqlCursor,
                                   TableName = "Poll_Table",
                                   Columns = {"Question": Question},
                                   Where = [
                                            ["Internal_Poll_Id", self.InternalPollId],
                                            "AND",
                                            ["Master_User_Id", self.InternalUserId],
                                            ],
                                   Autocommit = True
                                   )
    
    def GetPollByName(self):
        """
        This methode will set the self.InternalPollId with the id.
        
        Variables:
            \-
        """
        
        self.InternalPollId = self.SqlObject.SelectEntry(
                                   self.SqlCursor,
                                   FromTable = "Poll_Table",
                                   Columns = ("Internal_Poll_Id",),
                                   Where = [
                                            ["Poll_Name","=","%s"],
                                            "AND",
                                            ["Master_User_Id", "=", "%s"]
                                            ],
                                    Data = (
                                            self.PollName, 
                                            self.InternalUserId
                                            )
                                   )[0]["Internal_Poll_Id"]
    
    def GetExternalPollId(self):
        """
        This method will get the external group id from the database.
        
        Variables:
            \-
        """
        if self.InternalPollId == None:
            self.GetPollByName()

#         self.ExternalPollId = self.SqlObject.SelectEntry(
#                                    self.SqlCursor,
#                                    "Poll_Table",
#                                    ("CAST('External_Poll_Id' AS CHARACTER) AS 'External_Poll_Id'",),
#                                    Where = [["Internal_Poll_Id","=", "%s"]],
#                                    Data = (self.InternalPollId)
#                                    )[0]["External_Poll_Id"]
        
        Query = "SELECT CAST(`External_Poll_Id` AS CHARACTER) AS `External_Poll_Id` FROM `poll_table` WHERE `Internal_Poll_Id`=%s;"
        Data = self.InternalPollId
        self.ExternalPollId = self.SqlObject.ExecuteTrueQuery(self.SqlCursor,
                                        Query,
                                        Data
                                        )[0]['External_Poll_Id']

    def GetPollName(self):
        """
        This methode will return the poll name if given.
        
        Variables:
            \-
        """
        PollName = ""
        
        return PollName   
         
    def AddAnwser(self, Anwser):
        """
        This method adds an anwser to the poll.
        
        Variables:
            Anwser                        ``string``
                the answer or option to be added
        """
        self.SqlObject.InserEntry(
                                  self.SqlCursor,
                                  TableName = "Options_Table",
                                  Columns = {
                                             "Option_Name": Anwser,
                                             "Id_Poll_Table": self.InternalPollId,
                                             "Master_User_Id": self.InternalUserId,
                                             },
                                  Autocommit = True
                                  )

    def GetPollByExternalId(self):
        """
        This method will return a poll object with the correct selected poll. 
        
        Variables:
            \-
        """
        # 
        # SELECT * FROM `poll_table` WHERE `External_Poll_Id`=CAST('c4ca4238a0b923820dcc509a6f75849b' AS BINARY)
        
        PollObject = Poll()
        
        return PollObject
    
    def GenerateURL(self, NameOfApp):
        """
        Generates and returns the url needed to add a poll to a group.
        
        The telegram 
        https://telegram.me/<bot name>?startgroup=<external group id>
        
        Variables:
            NameOfApp                     ``string``
                contains the name of the bot (the bot username) it
                is needed to tell the telegram client what bot with what 
                parameter to add to a user chosen group.
        """
        URL = [
               "https://telegram.me/", 
               NameOfApp,
               ]
                
        if self.ExternalPollId == None:
            self.GetExternalPollId()
            
        URL.append("?startgroup=")
        URL.append(self.ExternalPollId)
        
        return "".join(URL)
        