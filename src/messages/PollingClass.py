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
                 **OptionalObjects
                 ):
        """
        The init method of the class
        
        Variables:
            InternalUserId                None or integer
                stores the internal user id
                
            InternalPollId                None or integer
                stores the internal poll id
            
            OptionalObjects               dictionary
                holds all the additional objects like:
                    LoggingObject         object
                        holds the logging object
                    
                    SqlObject             object
                        holds the sql connection object
                        
        """
        
        self.InternalUserId = InternalUserId
        
        self.InternalPollId = InternalPollId

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
            Question                      string
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
        return True
    
    def GetPollName(self):
        """
        This methode will return the poll name if given.
        
        Variables:
            -
        """
        pass     
    
    def AddAnwser(self, Anwser):
        """
        This method adds an anwser to the poll.
        
        Variables:
            Anwser                        string
                the answer or option to be added
        """
        self.SqlObject.InserEntry(
                                  self.SqlCursor,
                                  TableName = "Options_Table",
                                  Columns = {
                                             "Option_Name": Anwser,
                                             "Id_Poll_Table": self.InternalPollId
                                             }
                                  )
        
        pass
    
#     def AddQuestion(self, Question):
#         pass
    

def GetPollByExternalId(ExternalId):
    """
    This method will return a poll object with the correct selected poll. 
    """
    # 
    # SELECT * FROM `poll_table` WHERE `External_Poll_Id`=CAST('c4ca4238a0b923820dcc509a6f75849b' AS BINARY)
    
    PollObject = Poll()
    
    return PollObject