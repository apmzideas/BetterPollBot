#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import gobjects


class CustomParser(argparse.ArgumentParser):
    """
    This module it a preconfigured extended version of the argparser.
    
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
        This method is an init, never seen one before?
        
        Variables:
            OptionalObjects               ``directory``
                contains the optional objects 
                like:
                    ConfigurationObject   ``object``
                        contains the configuration
                    
                    LanguageObject        ``object``
                        contains the language object needed for 
                        automatic string translation
        """

        if "ConfigurationObject" in OptionalObjects:
            self.Configuration = OptionalObjects["ConfigurationObject"]
        else:
            raise ValueError("Missing ConfigurationObject")

        if "LanguageObject" in OptionalObjects:
            self.LanguageObject = OptionalObjects["LanguageObject"]
            self._ = self.LanguageObject.gettext
        else:
            raise ValueError("Missing LanguageObject")

        Description = self._(
            "An in python written telegram bot, called BetterPollBot."
        )

        Epilog = (
            self._(
                "Author:\t\t\t{Author}\nCredits:\t\t{Credits}\nVersion:\t\t"
                "{Version}\nRelease:\t\t{Release}\nLicense:\t\t{License}\n"
                "Copyright:\t\t{Copyright}"
            ).format(
                Author=gobjects.__author__,
                Credits=", ".join(gobjects.__credits__),
                Version=gobjects.__version__,
                Release=gobjects.__release__,
                License=gobjects.__license__,
                Copyright=gobjects.__copyright__)
        )

        super().__init__(
            prog=gobjects.__AppName__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=Description,
            epilog=Epilog
        )

    def RunParser(self):
        """
        This method add the parser arguments to the system.
        
        With the here defined parser arguments can the system 
        understand the ``sys.args`` values better.
        This method will set the command line arguments like this:\n


            usage: BetterPollBot [-h] [-v] [-c] [-f FILE] [-l LANGUAGE] 
                                 [-t TIME] [-at APITOKEN] 
                                 [-dn DATABASENAME] [-du DATABASEUSER]
                                 [-dp DATABASEPASSWORD] 
                                 [-dh DATABASEHOST]
                                 [-dhp DATABASEHOSTPORT]
            
            An in python written telegram bot, called BetterPollBot.
            
            optional arguments:\n
            +---------------------+------------------------------------+
            |  -h, --help         |show this help message and exit     |
            +---------------------+------------------------------------+ 
            |  -v, --version      |show program's version number and   |
            |                     |exit                                |
            +---------------------+------------------------------------+
            |  -c, --console      | Toggles the type of logging from   |
            |                     |the set settings in the config.ini. | 
            +---------------------+------------------------------------+
            |  -f FILE            |Set the file to log into temporary  |
            |                     |to the set destination.             |
            +---------------------+------------------------------------+
            |  -l LANGUAGE        |Changes the set language temporary. |
            +---------------------+------------------------------------+
            |  -t TIME            |Set's the time for the main loop to | 
            |                     |wait until the next request.        | 
            +---------------------+------------------------------------+
            |  -at APITOKEN       |Sets the telegram api token         |
            |                     |temporary.                          |
            +---------------------+------------------------------------+
            |  -dn DATABASENAME   |Changes the database name to connect|
            |                     |to.                                 |
            +---------------------+------------------------------------+
            |  -du DATABASEUSER   |Set the database user, needed to    |
            |                     |connect to the database. Attention  |
            |                     |use this option instead of the      |
            |                     |config.ini!                         |
            +---------------------+------------------------------------+  
            |-dp DATABASEPASSWORD |Set the database password, needed to|
            |                     |connect to the database.            |
            |                     |Attention use this option instead of|
            |                     |the config.ini!                     |
            +---------------------+------------------------------------+
            |-dh DATABASEHOST     |Set the database host, needed to    |
            |                     |connect to the database.            |
            +---------------------+------------------------------------+ 
            |-dhp DATABASEHOSTPORT|Set the database port, needed to    |
            |                     |connect to the database.            |
            +---------------------+------------------------------------+            
        
        Variables:
            \-
        """
        # adding parser arguments to the system
        self.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " + str(gobjects.__version__)
        )

        self.add_argument(
            "-c",
            "--console",
            help=self._(
                "Toggles the type of logging from the set settings in the "
                "config.ini."
            ),
            action=(
                "store_false"
                if self.Configuration.getboolean("Logging", "LogToConsole")
                else "store_true"
            ),
            dest="PrintToConsole"
        )

        # All the telegram related commands are here.
        self.add_argument(
            "-f",
            # "--FileToLog",
            help=self._(
                "Set the file to log into temporary to the set destination."
            ),
            action="store",
            # metavar="\b",
            dest="File",
            default=self.Configuration["Logging"]["LoggingFileName"]
        )

        self.add_argument(
            "-l",
            # "--Language",
            help=self._("Changes the set language temporary."),
            action="store",
            # nargs="+",
            # metavar="\b",
            dest="Language",
            default=self.Configuration["Telegram"]["DefaultLanguage"]
        )

        self.add_argument(
            "-t",
            # "--time",
            help=self._("Set's the time for the main loop to wait until the"
                        " next request."
                        ),
            action="store",
            type=int,
            # metavar="\b",
            dest="Time",
            default=self.Configuration["Telegram"]["RequestTimer"],
        )

        self.add_argument(
            "-at",
            # "--ApiToken",
            help=self._("Sets the telegram api token temporary."),
            action="store",
            # metavar="\b",
            dest="ApiToken",
            default=self.Configuration["Telegram"]["ApiToken"]
        )

        # All database related commands are listed here.
        self.add_argument(
            "-dn",
            # "--DatabaseName",
            help=self._("Changes the database name to connect to."),
            action="store",
            # metavar="\b",
            dest="DatabaseName",
            default=(self.Configuration["MySQLConnectionParameter"]
                     ["DatabaseName"])
        )

        self.add_argument(
            "-du",
            # "--DatabaseUser",
            help=(
                self._(
                    "Set the database user, needed to connect to the "
                    "database."
                ) + " " +
                self._(
                    "Attention use this option instead of the config.ini!"
                )
            ),
            action="store",
            # metavar="\b",
            dest="DatabaseUser",
            default=(
                self.Configuration["MySQLConnectionParameter"]["DatabaseUser"]
            )
        )

        self.add_argument(
            "-dp",
            # "--DatabasePassword",
            help=(
                self._(
                    "Set the database password, needed to connect to the "
                    "database."
                ) + " " +
                self._(
                    "Attention use this option instead of the config.ini!"
                )
            ),
            action="store",
            dest="DatabasePassword",
            default=(
                self.Configuration["MySQLConnectionParameter"]
                ["DatabasePassword"]
            )
        )

        self.add_argument(
            "-dh",
            # "--DatabaseHost",
            help=self._(
                "Set the database host, needed to connect to the database."
            ),
            action="store",
            dest="DatabaseHost",
            default=(
                self.Configuration["MySQLConnectionParameter"]["DatabaseHost"]
            )
        )

        self.add_argument(
            "-dhp",
            # "--DatabaseHostPort",
            help=self._(
                "Set the database port, needed to connect to the database."
            ),
            dest="DatabaseHostPort",
            default=(
                self.Configuration["MySQLConnectionParameter"]["DatabasePort"]
            )
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
        
        This method is an alias of ``Parser.parse_args()``.
        
        Variables:
            \-
        """
        return self.parse_args()
