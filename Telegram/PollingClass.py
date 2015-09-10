#!/usr/bin/python
# -*- coding: utf-8 -*-

import GlobalObjects
import hashlib
import Sql.SqlClass
import LoggingClass

class Poll(object):
    #In this class all the methodes needed for the poll will be stored.
    def __init__(self, InternalUserId = None, InternalPollId = None, **OptionalObjects):
        
        
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
            # problems in the future making the system multi threading safe.
            self.SqlCursor = self.SqlObject.CreateCursor()

        
    def UpdateQuestion(self, Question):
        self.SqlObject.UpdateEntry(
                                   self.SqlCursor,
                                   TableName = "poll_table",
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
        pass     

    
    def AddQuestion(self, Question):
        pass
    

def GetPollByExternalId(ExternalId):
    # This method will return a poll object with the correct poll selected.
    # SELECT * FROM `poll_table` WHERE `External_Poll_Id`=CAST('c4ca4238a0b923820dcc509a6f75849b' AS BINARY)
    
    PollObject = Poll()
    
    return PollObject