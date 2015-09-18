#!/usr/bin/python
# -*- coding: utf-8 -*-
import GlobalObjects
import argparse
import language.LanguageClass



class Parser(argparse.ArgumentParser):
    """
    This module it a preconfigured extended version of the Argparser.
    
    From the documentation.
    The argparse module makes it easy to write user-friendly 
    command-line interfaces. The program defines what arguments it 
    requires, and argparse will figure out how to parse those out of 
    sys.argv. The argparse module also automatically generates help and 
    usage messages and issues errors when users give the program 
    invalid arguments.
    
    link to the documentation:
        https://docs.python.org/3.4/library/argparse.html
    """


    def __init__(self, 
                 **OptionalObjects):
        """
        This method is an init, never seen one bevor?
        
        Variables:
            OptionalObjects               directory
                contains the optional objects 
                like:
                    ConfigurationObject   object
                        contains the configuration
                    
                    LanguageObject        object
                        contains the language object needed for 
                        automatic string translation
        """
        
        Description = ("An in python written telegram bot,"
                    " called BetterPollBot.")
        Epilog = ("Author:\t\t\t{Author}\nCredits:\t\t{Credits}"
                    "\nVersion:\t\t{Version}\nRelease:\t\t"
                    "{Release}\nLicense:\t\t{License}\n"
                    "Copyright:\t\t{Copyright}".format(
                                    Author = GlobalObjects.__author__,
                                    Credits = ", ".join(GlobalObjects.__credits__),
                                    Version = GlobalObjects.__version__,
                                    Release = GlobalObjects.__release__,
                                    License = GlobalObjects.__license__,
                                    Copyright = GlobalObjects.__copyright__)
                  )
        
        super().__init__(
                         prog=GlobalObjects.__AppName__,
                         formatter_class=argparse.RawDescriptionHelpFormatter,
                         description=Description,
                         epilog=Epilog
                                    )
        
        if "ConfigurationObject" in OptionalObjects:
            self.Configuration = OptionalObjects["ConfigurationObject"]
        if "LanguageObject" in OptionalObjects:
            self.LanguageObject = OptionalObjects["LanguageObject"]
            self._ = self.LanguageObject.gettext
        
    def RunParser(self):
        """
        This method add the parser arguments to the system.
        
        With the here defined parser arguments can the system 
        understand the sys.args values better.
        
        Variables:
            \-
        """
        # adding parser arguments to the system
        self.add_argument(
                            "-v", 
                            "--version",
                            action="version", 
                            version="%(prog)s " + str(GlobalObjects.__version__)
                            )
        
        self.add_argument(
                            "-c",
                            "--console", 
                            help=self._("Toggles the type of logging from the set settings in the config.ini."),                
                            action=("store_false" if self.Configuration.getboolean("Logging","LogToConsole" ) 
                                    else "store_true"),
                            dest="PrintToConsole"
                            )
        
        # All the telegram related commands are here.
        self.add_argument(
                            "-f",
                            #"--FileToLog",
                            help=self._("Set the file to log into temporary to the set destination."),
                            action="store",
                            #metavar="\b",
                            dest="File",
                            default=self.Configuration["Logging"]["LoggingFileName"]
                            )
        
        self.add_argument(
                            "-l",
                            #"--Language",
                            help=self._("Change the language settings temporary"),
                            action="store",
                            #nargs="+",
                            #metavar="\b",
                            dest="Language",
                            default=self.Configuration["Telegram"]["DefaultLanguage"]
                            )
        
        self.add_argument(
                            "-t",
                            #"--time",
                            help=self._("Set's the time for the main loop to wait until the next request."),
                            action="store",
                            type=int,
                            #metavar="\b",
                            dest="Time",
                            default=self.Configuration["Telegram"]["RequestTimer"],
                            )
        
        self.add_argument(
                            "-at",
                            #"--ApiToken",
                            help=self._("Sets the telegram api token temporary."),
                            action="store",
                            #metavar="\b",
                            dest="ApiToken",
                            default=self.Configuration["Telegram"]["ApiToken"]
                            )
        
        # All database related commands are listed here.
        self.add_argument(
                            "-dn", 
                            #"--DatabaseName",
                            help=self._("Changes the database name to connect to."),
                            action="store",
                            #metavar="\b",
                            dest="DatabaseName",
                            default=self.Configuration["MySQLConnectionParameter"]["DatabaseName"]
                            )
        
        self.add_argument(
                            "-du",
                            #"--DatabaseUser",
                            help=self._("Set the database user, needed to connect to the database.") +" " 
                                + self._("Attention use this option insted of the config.ini!"),
                            action="store",
                            #metavar="\b",
                            dest="DatabaseUser",
                            default=self.Configuration["MySQLConnectionParameter"]["DatabaseUser"]
                            )
        
        self.add_argument(
                            "-dp",
                            #"--DatabasePassword",
                            help=self._("Set the databse password, needed to connect to the database.") + " " 
                                + self._("Attention use this option insted of the config.ini!"),
                            action="store",
                            dest="DatabasePassword",
                            default=self.Configuration["MySQLConnectionParameter"]["DatabasePassword"]
                            )
        
        self.add_argument(
                            "-dh",
                            #"--DatabaseHost",
                            help=self._("Set the database host, needed to connect to the database."),
                            action="store",
                            dest="DatabaseHost",
                            default=self.Configuration["MySQLConnectionParameter"]["DatabaseHost"]
                            )
        
        self.add_argument(
                            "-dhp",
                            #"--DatabaseHostPort",
                            help=self._("Set the database port, needed to connect to the database."),
                            dest="DatabaseHostPort",
                            default=self.Configuration["MySQLConnectionParameter"]["DatabasePort"]
                            )
        
        # A hidden option to install the Database
        self.add_argument(
                            '--InstallDatabaseStructure', 
                            help=argparse.SUPPRESS,
                            dest="InstallDatabaseStructure",
                            action="store_true"                       
                            )
        
        
    def GetArguments(self):
        """
        This method will return the parser arguments as a directory.
        
        Variables:
            \-
        """
        return self.parse_args()
        