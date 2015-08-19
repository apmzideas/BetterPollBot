#!/usr/bin/python
# -*- coding: utf-8 -*-


""" The master file that will hold all the initiated classes and will be used
     as the thread deployer.
"""


import GlobalObjects

import argparse
import getpass

import ConfigurationClass
import LoggingClass
import LanguageClass
import TelegramClass
import SqlClass
import ErrorClasses


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
    
    Parser.add_argument(
                        "-f",
                        #"--FileToLog",
                        help=_("Sets the file to log into temporary to the set destination."),
                        action="store",
                        #metavar="\b",
                        dest="File",
                        default=Configuration["Logging"]["LoggingFileName"]
                        )
    
    Parser.add_argument(
                        "-at",
                        #"--ApiToken",
                        help=_("Sets the telegram api token temporary."),
                        action="store",
                        #metavar="\b",
                        dest="ApiToken",
                        default=Configuration["Telegram"]["ApiToken"],
                        )
    
    Parser.add_argument(
                        "-dn", 
                        #"--DatabaseName",
                        help=_("Changes the database name to connect to."),
                        action="store",
                        #metavar="\b",
                        dest="DatabaseName",
                        default=Configuration["MySQLConnectionParameter"]["DatabaseName"],
                        )
    
    Parser.add_argument(
                        "-du",
                        #"--DatabaseUser",
                        help=_("Set's the database user, needed to connect to the database.") +" " + _("Attention use this option insted of the config.ini!"),
                        action="store",
                        dest="DatabaseUser",
                        default=Configuration["MySQLConnectionParameter"]["DatabaseUser"],
                        )
    
    Parser.add_argument(
                        "-dp",
                        #"--DatabasePassword",
                        help=_("Set's the databse password, needed to connect to the database.") + " " + _("Attention use this option insted of the config.ini!"),
                        action="store",
                        dest="DatabasePassword",
                        default=Configuration["MySQLConnectionParameter"]["DatabasePassword"],
                        )
    
    Parser.add_argument(
                        "-l",
                        #"--Language",
                        help=_("Change the language settings temporary"),
                        action="store",
                        nargs="1",
                        #metavar="\b",
                        dest="Language",
                        default=Configuration["Telegram"]["DefaultLanguage"],
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
    
    #Parser.print_help()
    args = Parser.parse_args()
    
    
    print(args)
    
    #Initialise the main loop
    
    
def ObjectInitialiser():
    GlobalObjects.ObjectHolder["ConfigurationClass"] = ConfigurationClass.ConfigurationParser()
    GlobalObjects.ObjectHolder["ConfigurationClass"].ReadConfigurationFile()
    GlobalObjects.ObjectHolder["LoggingClass"] = LoggingClass.Logger(config_name="config.ini", log_to_file=False)
    GlobalObjects.ObjectHolder["SqlClass"] = SqlClass.SqlApi("root", "Password", 
                                                             GlobalObjects.ObjectHolder["ConfigurationClass"]["MySQL Connection Parameter"]["DatabaseName"],
                                                             LoggingObject = GlobalObjects.ObjectHolder["LoggingClass"],
                                                             LanguageObject = LanguageClass.CreateTranslationObject("de_DE")
                                                             )
    #GlobalObjects.ObjectHolder["TelegramClass"] = TelegramClass.TelegramApi("80578257:AAEt5tHodsbD6P3hqumKYFJAyHTGWEgcyEY")
    
    


if __name__ == "__main__":
    Main()
