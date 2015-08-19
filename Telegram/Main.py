#!/usr/bin/python
# -*- coding: utf-8 -*-


""" The master file that will hold all the initiated classes and will be used
     as the thread deployer.
"""


import GlobalObjects

import argparse
import getpass
import time
import msvcrt

import ConfigurationClass
import LoggingClass
import LanguageClass
import TelegramClass
import SqlClass
import ErrorClasses
import MessageProcessorClass


def Main():
    #Create the configuration class and read the configuration class.
    Configuration = ConfigurationClass.ConfigurationParser()
    Configuration.ReadConfigurationFile()
    
    #Create the language proccesser
    LanguageMasterObject = LanguageClass.CreateTranslationObject(Configuration["Telegram"]["DefaultLanguage"].split(","))
    
    #This is the language objects only value
    _ = LanguageMasterObject.gettext
    
    #init parser
    Parser = argparse.ArgumentParser(prog=GlobalObjects.__AppName__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="An in python written telegram bot, called BetterPollBot.", epilog="\
Author:\t\t\t{Author}\n\
Credits:\t\t{Credits}\n\
Version:\t\t{Version}\n\
Release:\t\t{Release}\n\
License:\t\t{License}\n\
Copyright:\t\t{Copyright}".format(
                                  Author = GlobalObjects.__author__,
                                  Credits = ", ".join(GlobalObjects.__credits__),
                                  Version = GlobalObjects.__version__,
                                  Release = GlobalObjects.__release__,
                                  License = GlobalObjects.__license__,
                                  Copyright = GlobalObjects.__copyright__)
                                )
    
    #adding parser arguments to the system
    Parser.add_argument(
                        "-v", 
                        "--version",
                        action="version", version="%(prog)s " + str(GlobalObjects.__version__)
                        )
    
    Parser.add_argument(
                        "-c",
                        "--console", 
                        help=_("Toggles the type of logging from the set settings in the config.ini."),                
                        action=("store_false" if Configuration.getboolean("Logging","LogToFile" ) else "store_true"),
                        dest="PrintToConsole"
                        )
    
    #All the telegram related commands are here.
    Parser.add_argument(
                        "-f",
                        #"--FileToLog",
                        help=_("Set the file to log into temporary to the set destination."),
                        action="store",
                        #metavar="\b",
                        dest="File",
                        default=Configuration["Logging"]["LoggingFileName"]
                        )
    
    Parser.add_argument(
                        "-l",
                        #"--Language",
                        help=_("Change the language settings temporary"),
                        action="store",
                        #nargs="+",
                        #metavar="\b",
                        dest="Language",
                        default=Configuration["Telegram"]["DefaultLanguage"]
                        )
    
    Parser.add_argument(
                        "-t",
                        #"--time",
                        help=_("Set's the time for the main loop to wait until the next request."),
                        action="store",
                        type=int,
                        #metavar="\b",
                        dest="Time",
                        default=Configuration["Telegram"]["RequestTimer"],
                        )
    
    Parser.add_argument(
                        "-at",
                        #"--ApiToken",
                        help=_("Sets the telegram api token temporary."),
                        action="store",
                        #metavar="\b",
                        dest="ApiToken",
                        default=Configuration["Telegram"]["ApiToken"]
                        )
    
    #All database related commands are listed here.
    Parser.add_argument(
                        "-dn", 
                        #"--DatabaseName",
                        help=_("Changes the database name to connect to."),
                        action="store",
                        #metavar="\b",
                        dest="DatabaseName",
                        default=Configuration["MySQLConnectionParameter"]["DatabaseName"]
                        )
    
    Parser.add_argument(
                        "-du",
                        #"--DatabaseUser",
                        help=_("Set the database user, needed to connect to the database.") +" " + _("Attention use this option insted of the config.ini!"),
                        action="store",
                        #metavar="\b",
                        dest="DatabaseUser",
                        default=Configuration["MySQLConnectionParameter"]["DatabaseUser"]
                        )
    
    Parser.add_argument(
                        "-dp",
                        #"--DatabasePassword",
                        help=_("Set the databse password, needed to connect to the database.") + " " + _("Attention use this option insted of the config.ini!"),
                        action="store",
                        dest="DatabasePassword",
                        default=Configuration["MySQLConnectionParameter"]["DatabasePassword"]
                        )
    
    Parser.add_argument(
                        "-dh",
                        #"--DatabaseHost",
                        help=_("Set the database host, needed to connect to the database."),
                        action="store",
                        dest="DatabaseHost",
                        default=Configuration["MySQLConnectionParameter"]["DatabaseHost"]
                        )
    
    Parser.add_argument(
                        "-dhp",
                        #"--DatabaseHostPort",
                        help=_("Set the database port, needed to connect to the database."),
                        dest="DatabaseHostPort",
                        default=Configuration["MySQLConnectionParameter"]["DatabasePort"]
                        )
    
    #A hidden option to install the Database
    Parser.add_argument(
                        '--InstallDataseStructure', 
                        help=argparse.SUPPRESS,
                        dest="InstallDataseStructure",
                        action="store_true"                       
                        )
    
    ParserArguments = Parser.parse_args()
    
    #Initialise the rest of the objects.
    MasterLogger = LoggingClass.Logger(log_to_file=ParserArguments.PrintToConsole)
        
    MasterLogger.create_log(_("{AppName} has been startet.").format(AppName = GlobalObjects.__AppName__))
    
    if ParserArguments.ApiToken == "":
        MasterLogger.create_log(_("No telegram token has been added to the system!"), "warning")
        raise SystemExit
    
    TelegramObject = TelegramClass.TelegramApi(
                                               ApiToken = ParserArguments.ApiToken,
                                               LoggingObject = MasterLogger,
                                               LanguageObject = LanguageMasterObject,
                                               )
    

    
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
                 
        SqlObject = SqlClass.SqlApi(
                                    ParserArguments.DatabaseUser,
                                    ParserArguments.DatabasePassword,
                                    ParserArguments.DatabaseName,
                                    LanguageObject = LanguageMasterObject,
                                    LoggingObject = MasterLogger
                                    )
        
        if SqlObject.DatabaseConnection == False:
            ParserArguments.DatabaseUser = ""
            ParserArguments.DatabasePassword = ""
            
            TryAgain = ""
            if NrTry < 3: 
                TryAgain = _("try again")
            else:
               TryAgain = _("too bad")                                                               
            
            MasterLogger.create_log( _("You have used {NrTry} of 3 times:").format(NrTry = str(NrTry))+ " "  + TryAgain, "WARNING")
            NrTry += 1
        else:
            NoConnection = False 
    
    if NrTry == 3:
        MasterLogger.create_log( _("{AppName} has been stoped, because you didn't input the correct user name of password."))
        raise SystemExit
    
    
    #print(ParserArguments)
    
    #Initialise the main loop (it's a endless loop, it breaks when a key is pressed.)
    MasterLogger.create_log(_("Exit loop by pressing <Esc>, <q> or <Space>"))
    MasterLogger.create_log( _("Getting updates from the telegram api."))
    #Add a comment number to the telegram request, so that the old messages will be sorted out.
    CommentNumber = None
    
    while True:
        #check if a key is pressed by user and stop if pressed.    
        if msvcrt.kbhit():
            PressedKey = ord(msvcrt.getch())
            if PressedKey == 27 or PressedKey == 113 or PressedKey == 32:
                MasterLogger.create_log( _("A user shutdown was requested will now shutdown."))
                break
            
        #Get the updates from the telegram serves.
        Results = TelegramObject.GetUpdates(CommentNumber)
        
        #Do 
        if Results != None:
            for i in Results["result"]:
                MessageProcessor = MessageProcessorClass.MessageProcessor(i,
                                                                          LanguageObject = LanguageMasterObject,
                                                                          SqlObject = SqlObject,
                                                                          LoggingObject = MasterLogger
                                                                          )
                
                #Set the CommentNumber to a actual ChatId number, so that the incomming list is allways actuel.
                #This number has to be 1 bigger than the oldest unit
                CommentNumber = MessageProcessor.UpdateId + 1

        #Waites until the next loop should start. 
        #Sleep need a second to be parsed, so the given value is transformed from miliseconds to seconds.
        time.sleep((ParserArguments.Time / 1000.0))
    


if __name__ == "__main__":
    Main()
