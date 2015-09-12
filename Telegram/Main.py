#!/usr/bin/python
# -*- coding: utf-8 -*-


""" The master file that will hold all the initiated classes and will be used
     as the thread deployer.
"""

# supper import needed by other classes
import GlobalObjects

# standard modules import 
# import argparse
import getpass
import time
import msvcrt
import threading
import sys

# personal imports
import ParserClass
import ConfigurationClass
import LoggingClass
import LanguageClass
import TelegramClass
import Sql.SqlClass
import ErrorClasses
import MessageProcessorClass


def Main():
    # Create the configuration class and read the configuration class.
    Configuration = ConfigurationClass.ConfigurationParser()

    # Create the language proccesser
    LanguageMasterObject = LanguageClass.CreateTranslationObject(Configuration["Telegram"]["DefaultLanguage"].split(","))
    
    # This is the language objects only value
    _ = LanguageMasterObject.gettext
    
#     # init parser
   
    Parser = ParserClass.Parser(ConfigurationObject = Configuration, 
                                LanguageObject = LanguageMasterObject
                                )
    Parser.RunParser()
    ParserArguments = Parser.GetArguments()
    
    # Initialise the rest of the objects.
    MasterLogger = LoggingClass.Logger(
                                           LogToConsole=ParserArguments.PrintToConsole,
                                           FileName = Configuration["Logging"]["LoggingFileName"],
                                           MaxLogs = Configuration["Logging"]["MaxLogs"],
                                           LoggingFormat = Configuration["Logging"]["LoggingFormat"],
                                           Dateformat = Configuration["Logging"]["Dateformat"],
                                           LoggingLevel = "debug")
        
    MasterLogger.info(_("{AppName} has been startet.").format(AppName = GlobalObjects.__AppName__))
    
    if ParserArguments.ApiToken == "":
        MasterLogger.critical(_("No telegram token has been added to the system!"))
        raise SystemExit
    
    TelegramObject = TelegramClass.TelegramApi(
                                               ApiToken = ParserArguments.ApiToken,
                                               RequestTimer = ParserArguments.Time,
                                               LoggingObject = MasterLogger,
                                               LanguageObject = LanguageMasterObject,
                                               ExitOnError = False
                                               )
    BotName = TelegramObject.GetBotName()
    
    SqlObject = None
    
    NoConnection = True
    NrTry = 1
    
    while (NoConnection and NrTry <= 3):
        #If no database user or password have been sent, get them from the user. 
        #(This is safer than other options.)
        if ParserArguments.DatabaseUser == "":
            ParserArguments.DatabaseUser = input(_("User:") + " ")
        if ParserArguments.DatabasePassword == "":
            ParserArguments.DatabasePassword = getpass.getpass(_("Password:") + " ")
                 
        SqlObject = Sql.SqlClass.SqlApi(
                                    ParserArguments.DatabaseUser,
                                    ParserArguments.DatabasePassword,
                                    ParserArguments.DatabaseName,
                                    LoggingObject = MasterLogger
                                    )
        
        if SqlObject.DatabaseConnection == False:
            ParserArguments.DatabaseUser = ""
            ParserArguments.DatabasePassword = ""
            
            # If the password has been entered more than tree times
            # the system will shut down.
            TryAgain = ""
            if NrTry < 3: 
                TryAgain = _("try again")
            else:
               TryAgain = _("too bad")                                                               
            
            MasterLogger.warning( _("You have used {NrTry} of 3 times:").format(NrTry = str(NrTry))+ " "  + TryAgain,)
            NrTry += 1
        else:
            NoConnection = False 
    
    if NrTry == 3:
        MasterLogger.info( _("{AppName} has been stoped, because you didn't input the correct user name of password.").format(AppName = GlobalObjects.__AppName__))
        raise SystemExit
    
    # This will be used if the database will be installed.
    if ParserArguments.InstallDatabaseStructure == True:
        InstallDatabase = input( _("Are you sure you want to install the database structure?") +" Yes/No ")
        if InstallDatabase.lower() == "yes":
            MasterLogger.info( _("{AppName} will now start to install the database structure").format(AppName = GlobalObjects.__AppName__))
            SqlCursor = SqlObject.CreateCursor()
            SqlObject.CreateMainDatabase(SqlCursor)
            MasterLogger.info( _("The database has been installed, please restart system.") )
        elif InstallDatabase.lower() == "no":
            MasterLogger.info( _("Database will not be installed terminating process."))
        raise SystemExit
    
    # print(ParserArguments)
    
    ParserArguments.Time = ParserArguments.Time / 1000.0
    
    # Initialise the main loop (it's a endless loop, it breaks when a key is pressed.)
    MasterLogger.info(_("Exit loop by pressing <Esc>, <q> or <Space>"))
    MasterLogger.info( _("Getting updates from the telegram api."))
    # Add a comment number to the telegram request, so that the old messages will be sorted out.
    CommentNumber = None
    
    while True:
        # check if a key is pressed by user and stop if pressed.    
        if msvcrt.kbhit():
            PressedKey = ord(msvcrt.getch())
            if PressedKey == 27 or PressedKey == 113 or PressedKey == 32:
                MasterLogger.info( _("A user shutdown was requested will now shutdown."))
                break
        
        #Processrequest()
        
        # Get the updates from the telegram serves.
        Results = TelegramObject.GetUpdates(CommentNumber)
        
        # Do 
        if Results != None:
            for i in Results["result"]:
                MessageProcessor = MessageProcessorClass.MessageProcessor(i,
                                                                          LanguageObject = LanguageMasterObject,
                                                                          SqlObject = SqlObject,
                                                                          LoggingObject = MasterLogger,
                                                                          ConfigurationObject = Configuration,
                                                                          BotName = BotName
                                                                          )
                
                # This command sends the message to the user
                InterpretedMessage = MessageProcessor.InterpretMessage()
                if InterpretedMessage != None:
                    TelegramObject.SendMessage(InterpretedMessage)
                
                
                # Set the CommentNumber to a actual ChatId number, 
                # so that the incomming list is allways actuel.
                # This number has to be 1 bigger than the oldest unit
                CommentNumber = MessageProcessor.UpdateId + 1

        # Waites until the next loop should start. 
        # Sleep need a second to be parsed, so the given value is transformed
        # from miliseconds to seconds.
        if TelegramObject.RequestTimer == ParserArguments.Time:
            time.sleep((ParserArguments.Time))
        else:
            time.sleep((TelegramObject.RequestTimer / 1000))
    


if __name__ == "__main__":
    Main()
