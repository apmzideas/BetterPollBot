#!/usr/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
import gobjects
import custom_logging
import language
import telegram
import sql.sql_api
import messages.msg_processor


class Server(multiprocessing.Process):
    """
    This class will let the bot server run on a different process than the
    console interface.
    """

    def __init__(self,
                 TelegramObject,
                 SqlObject,
                 MasterQueue,
                 **OptionalObjects):
        """

        Variables:
            TelegramObject                ``object``
                This holds the telegram object needed
            SqlObject                     ``object``
                This holds the sql connector object
            MasterQueue                   ``object``
                  This holds the queue used to get the termination command.
                  (True or False)
            OptionalObjects               ``directory``
                In here are all the normally not really needed variables stored
                like the logging object or else
                Possible objects are:
                    - LoggingObject
                    - LanguageObject
                    - BotName

        """

        # init the subprocess
        super().__init__(name="Background", )

        # init the programs
        self.TelegramObject = TelegramObject
        self.SqlObject = SqlObject
        self.MasterQueue = MasterQueue

        if "LoggingObject" in OptionalObjects:
            self.LoggingObject = OptionalObjects["LoggingObject"]
        else:
            self.LoggingObject = custom_logging.Logger()

        if "LanguageObject" in OptionalObjects:
            self.LanguageObject = OptionalObjects["LanguageObject"]
        else:
            self.LanguageObject = language.CreateTranslationObject()

        self._ = self.LanguageObject.gettext

        if "BotName" in OptionalObjects:
            self.BotName = OptionalObjects["BotName"]
        else:
            self.BotName = gobjects.__AppName__


    def run(self):
        """
        This method will override the parents run method.

        Variables:
            \-
        """
        #raise NotImplementedError

        InternalQueue = multiprocessing.Queue()
        InternalQueue.put(None)

        run = True
        while run:
            if self.MasterQueue.empty():
                run = False
            # Get the updates from the telegram serves.
            if self.SqlObject.DetectConnection() is True:
                # check if queue has something for us in it
                CommentNumber = []
                while True:
                    if self.MasterQueue.empty() is False:
                        CommentNumber.append((self.MasterQueue.get()))
                    else:
                        break
                if len(CommentNumber) == 1:
                    CommentNumber = CommentNumber[0]
                elif len(CommentNumber) > 1:
                    CommentNumber = max(CommentNumber)
                else:
                    CommentNumber = None

                Results = self.TelegramObject.GetUpdates(CommentNumber)

                # Do
                if Results is not None:
                    for Message in Results["result"]:
                        MessageProcessor = (
                            messages.msg_processor.MessageProcessor(
                                Message,
                                LanguageObject=self.LanguageMasterObject,
                                SqlObject=self.SqlObject,
                                LoggingObject=self.MasterLogger,
                                ConfigurationObject=self.Configuration,
                                BotName=self.BotName
                            )
                        )

                         # This command sends the message to the user
                        InterpretedMessage = (
                            MessageProcessor.InterpretMessage()
                        )
                        if InterpretedMessage != None:
                            #print(TelegramObject.SendMessage(
                            # InterpretedMessage))
                            self.TelegramObject.SendMessage(InterpretedMessage)
                        # Set the CommentNumber to a actual ChatId number,
                        # so that the incoming list is always actual.
                        # This number has to be 1 bigger than the oldest unit
                        self.MasterQueue.put(MessageProcessor.UpdateId + 1)


class TelegramConnection(multiprocessing.Process):
    """
    This class is the connection process to the telegram api.

    This class will receive all the important function results and return them
    into the correct queue, so that the original code can be self consistent.
    """

    def __init__(self):
        super().__init__()

    def run(self):
        """
        This method will override the parents run method.

        Variables:
            \-
        """

        raise NotImplementedError