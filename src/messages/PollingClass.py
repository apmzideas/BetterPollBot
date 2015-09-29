#!/usr/bin/python
# -*- coding: utf-8 -*-

class Poll(object):
    """
    In this class all the methods needed for the poll will be stored.
    """


    BASE_URL = "https://telegram.me/"
    """
    The base of the telegram api url.
    """

    def __init__(self,
                 InternalUserId=None,
                 InternalPollId=None,
                 ExternalPollId=None,
                 PollName=None,
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
            raise ValueError("Missing LoggingObject cannot log")

        if "SqlObject" in OptionalObjects:
            self.SqlObject = OptionalObjects["SqlObject"]

            # The object get's it's own cursor so that there will be no 
            # problems in the future making the system multi threading
            # safe.
            self.SqlCursor = self.SqlObject.CreateCursor()
        else:
            raise ValueError("Missing SqlObject cannot create connection.")

    def UpdateQuestion(self, Question):
        """
        This method adds or modifies a question from the specific poll.
        
        Variables:
            Question                      ``string``
                holds the question given by the user
        """
        try:
            self.SqlObject.UpdateEntry(
                self.SqlCursor,
                TableName="Poll_Table",
                Columns={"Question": Question},
                Where=[
                    ["Internal_Poll_Id", self.InternalPollId],
                    "AND",
                    ["Master_User_Id", self.InternalUserId],
                ],
                Autocommit=True
            )
            return True
        except Exception:
            return False

    def GetPollByName(self):
        """
        This method will set the self.InternalPollId with the id.
        
        Variables:
            \-
        """
        self.InternalPollId = self.SqlObject.SelectEntry(
            self.SqlCursor,
            FromTable="Poll_Table",
            Columns=("Internal_Poll_Id",),
            Where=[
                ["Poll_Name", "=", "%s"],
                "AND",
                ["Master_User_Id", "=", "%s"]
            ],
            Data=(
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
        Query = ("SELECT CAST(`External_Poll_Id` AS CHARACTER) AS "
                 "`External_Poll_Id` FROM `poll_table` WHERE "
                 "`Internal_Poll_Id`=%s;"
                 )
        Data = (self.InternalPollId,)
        self.ExternalPollId = self.SqlObject.ExecuteTrueQuery(
            self.SqlCursor,
            Query,
            Data
        )[0]["External_Poll_Id"]

    def GetPollName(self):
        """
        This method will return the poll name if given.
        
        Variables:
            \-
        """
        raise NotImplementedError
        PollName = ""

        return PollName

    def AddAnwser(self, Answer):
        """
        This method adds an answer to the poll.
        
        Variables:
            Answer                        ``string``
                the answer or option to be added
        """
        self.SqlObject.InsertEntry(
            self.SqlCursor,
            TableName="Options_Table",
            Columns={
                "Option_Name": Answer,
                "Id_Poll_Table": self.InternalPollId,
                "Master_User_Id": self.InternalUserId,
            },
            AutoCommit=True
        )

    def GetPollByExternalId(self):
        """
        This method will set the internal poll id by using the external one.

        .. code-block:: sql\n
            SELECT * FROM `poll_table` WHERE `External_Poll_Id`=
            CAST('c4ca4238a0b923820dcc509a6f75849b' AS BINARY);

        Variables:
            \-
        """
        # 
        #

        self.InternalPollId = self.SqlObject.SelectEntry(
            Cursor=self.SqlCursor,
            FromTable="Poll_Table",
            Columns=("Internal_Poll_Id",),
            Where=[["External_Poll_Id", "=", "CAST(%s AS BINARY)"]],
            Data=(self.ExternalPollId,)
        )[0]["Internal_Poll_Id"]

    def GenerateURL(self, NameOfApp):
        """
        Generates and returns the url needed to add a poll to a group.
        
        The telegram link:
            ``https://telegram.me/<bot name>?startgroup=<external group id>``
        
        Variables:
            NameOfApp                     ``string``
                contains the name of the bot (the bot username) it
                is needed to tell the telegram client what bot with what 
                parameter to add to a user chosen group.
        """
        URL = [
            Poll.BASE_URL,
            NameOfApp,
        ]

        if self.ExternalPollId is None:
            self.GetExternalPollId()

        URL.append("?startgroup=")
        URL.append(self.ExternalPollId)

        return "".join(URL)

    def GetPollQuestion(self):
        """
        This method will query the database for the poll question.

        It will return in the end a list of possibles options for
        the given query.

        Variables:
            \-
        """
        return self.SqlObject.SelectEntry(
            self.SqlCursor,
            FromTable="Poll_Table",
            Columns=("Question",),
            Where=[
                ["Internal_Poll_Id", "=", "%s"],
                "AND",
                ["Master_User_Id", "=", "%s"]
            ],
            Data=(self.InternalPollId,
                  self.InternalUserId,
                  ),
        )[0]["Question"]

    def GetAllOptions(self):
        """
        This method will query the database for all the poll options.

        It will return in the end a list of possibles options of the
        poll.

        Variables:
            \-
        """

        Options = self.SqlObject.SelectEntry(
            self.SqlCursor,
            FromTable="Options_Table",
            Columns=("Option_Name",),
            OrderBy=[["Option_Name"]],
            Where=[
                ["Id_Poll_Table", "=", "%s"],
                "AND",
                ["Master_User_Id", "=", "%s"]
            ],
            Data=(self.InternalPollId,
                  self.InternalUserId,
                  ),
        )
        return [list(Parts.values()) for Parts in Options]

    def GetAllResults(self, GroupId):
        """
        This method will query the database for all the poll results.

        It will return in the end a list of all the results of the
        poll in the correct group.

        Variables:
            \-
        """
        raise NotImplementedError
        self.SqlObject.SelectEntry(
            self.SqlCursor,

        )
