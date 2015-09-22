#!/usr/bin/python3.4
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
import platform
# if windows only windows is supported :(
try:
    import msvcrt
except ImportError:
    import curses

# for now these imports are not need
# import threading
# import queue

# personal imports
import parsers.ParserClass
import parsers.ConfigurationClass
import LoggingClass
import language.LanguageClass
import TelegramClass
import sql.SqlClass
import messages.MessageProcessorClass


def Main():
    """
    The main function that let's the application roll.

    This function will initialise all the needed objects
    and see that there will be always something to do.
    """
    # this module is needed for the curses module for all unix distributions
    CursesMasterObject = None
    CursesObject = None
    # if program is run not on a windows system:
    if platform.system() != "Windows":
        # init the curses screen
        CursesMasterObject = curses.initscr()
        # Use cbreak to not require a return key press
        # The system will not be waiting so but continue to work.
        curses.cbreak()
        curses.noecho()
        CursesMasterObject.nodelay(1)
        maxy, maxx = CursesMasterObject.getmaxyx()
        begin_x = 0
        begin_y = 0
        height = 10
        width = maxx - 4
        CursesObject = curses.newwin(height, width, begin_y, begin_x)
        CursesObject.nodelay(1)
        curses.setsyx(-1, -1)
        CursesMasterObject.refresh()
        CursesObject.refresh()
        CursesObject.scrollok(True)
        CursesObject.idlok(True)
        CursesObject.leaveok(True)

    try:

        # Create the configuration class and read the configuration class.
        Configuration = parsers.ConfigurationClass.ConfigurationParser()

        # Create the language processor
        LanguageMasterObject = language.LanguageClass.CreateTranslationObject(
            Configuration["Telegram"]["DefaultLanguage"].split(","))

        # This is the language objects only value
        _ = LanguageMasterObject.gettext

        # init parser

        Parser = parsers.ParserClass.Parser(ConfigurationObject=Configuration,
                                            LanguageObject=LanguageMasterObject
                                            )
        Parser.RunParser()
        ParserArguments = Parser.GetArguments()

        # Initialise the rest of the objects.
        MasterLogger = LoggingClass.Logger(
            LogToConsole=ParserArguments.PrintToConsole,
            FileName=Configuration["Logging"]["LoggingFileName"],
            MaxLogs=Configuration["Logging"]["MaxLogs"],
            LoggingFormat=Configuration["Logging"]["LoggingFormat"],
            Dateformat=Configuration["Logging"]["Dateformat"],
            LoggingLevel="debug",
            CursesObject=CursesObject)

        MasterLogger.info(_("{AppName} has been startet.").format(AppName=GlobalObjects.__AppName__))

        if ParserArguments.ApiToken == "":
            MasterLogger.critical(_("No telegram token has been added to the system!"))
            raise SystemExit

        TelegramObject = TelegramClass.TelegramApi(
            ApiToken=ParserArguments.ApiToken,
            RequestTimer=ParserArguments.Time,
            LoggingObject=MasterLogger,
            LanguageObject=LanguageMasterObject,
            ExitOnError=False
        )
        BotName = TelegramObject.GetBotName()

        SqlObject = None

        NoConnection = True
        NrTry = 1

        while NoConnection and NrTry <= 3:
            # If no database user or password have been sent, get them from the user.
            # (This is safer than other options.)
            if ParserArguments.DatabaseUser == "":
                ParserArguments.DatabaseUser = input(_("User:") + " ")
            if ParserArguments.DatabasePassword == "":
                ParserArguments.DatabasePassword = getpass.getpass(_("Password:") + " ")

            SqlObject = sql.SqlClass.SqlApi(
                ParserArguments.DatabaseUser,
                ParserArguments.DatabasePassword,
                ParserArguments.DatabaseName,
                LoggingObject=MasterLogger,
                LanguageObject=LanguageMasterObject
            )

            if SqlObject.DatabaseConnection is False:
                ParserArguments.DatabaseUser = ""
                ParserArguments.DatabasePassword = ""

                # If the password has been entered more than tree times
                # the system will shut down.
                TryAgain = ""
                if NrTry < 3:
                    TryAgain = _("try again")
                else:
                    TryAgain = _("too bad")

                MasterLogger.warning(_("You have used {NrTry} of 3 times:").format(NrTry=str(NrTry)) + " " + TryAgain, )
                NrTry += 1
            else:
                NoConnection = False

        if NrTry == 3:
            MasterLogger.info(
                _("{AppName} has been stopped, because you didn't input the correct user name of password.").format(
                    AppName=GlobalObjects.__AppName__))
            raise SystemExit

        # This will be used if the database will be installed.
        if ParserArguments.InstallDatabaseStructure is True:
            InstallDatabase = input(_("Are you sure you want to install the database structure?") + " Yes/No ")
            if InstallDatabase.lower() == "yes":
                MasterLogger.info(_("{AppName} will now start to install the database structure").format(
                    AppName=GlobalObjects.__AppName__))
                SqlCursor = SqlObject.CreateCursor()
                SqlObject.CreateMainDatabase(SqlCursor)
                MasterLogger.info(_("The database has been installed, please restart system."))
            elif InstallDatabase.lower() == "no":
                MasterLogger.info(_("Database will not be installed terminating process."))
            raise SystemExit

        ParserArguments.Time = ParserArguments.Time / 1000.0

        # Initialise the main loop (it's a endless loop, it breaks when a key is pressed.)
        MasterLogger.info(_("Exit loop by pressing <Esc>, <q> or <Space>"))
        MasterLogger.info(_("Getting updates from the telegram api."))
        # Add a comment number to the telegram request, so that the old messages will be sorted out.
        CommentNumber = None

        while True:
            # check if a key is pressed by user and stop if pressed.
            # if windows use msvcrt
            if platform.system() == "Windows":
                if msvcrt.kbhit():
                    PressedKey = ord(msvcrt.getch())
                    if PressedKey == 27 or PressedKey == 113 or PressedKey == 32:
                        MasterLogger.info(_("A user shutdown was requested will now shutdown."))
                        SqlObject.CloseConnection()
                        break

            # use curses
            else:
                PressedKey = CursesObject.getch()
                if PressedKey == 27 or PressedKey == 113 or PressedKey == 32:
                    MasterLogger.info(_("A user shutdown was requested will now shutdown."))
                    SqlObject.CloseConnection()
                    break
                else:
                    pass

            # Process the requests

            # Get the updates from the telegram serves.
            Results = TelegramObject.GetUpdates(CommentNumber)

            # Do
            if Results != None:
                for Message in Results["result"]:
                    MessageProcessor = messages.MessageProcessorClass.MessageProcessor(Message,
                                                                                       LanguageObject=LanguageMasterObject,
                                                                                       SqlObject=SqlObject,
                                                                                       LoggingObject=MasterLogger,
                                                                                       ConfigurationObject=Configuration,
                                                                                       BotName=BotName
                                                                                       )

                    # This command sends the message to the user
                    InterpretedMessage = MessageProcessor.InterpretMessage()
                    if InterpretedMessage != None:
                        TelegramObject.SendMessage(InterpretedMessage)

                    # Set the CommentNumber to a actual ChatId number,
                    # so that the incomming list is allways actuel.
                    # This number has to be 1 bigger than the oldest unit
                    CommentNumber = MessageProcessor.UpdateId + 1

            # Waits until the next loop should start.
            # Sleep need a second to be parsed, so the given value is transformed
            # from milliseconds to seconds.
            if TelegramObject.RequestTimer == ParserArguments.Time:
                time.sleep((ParserArguments.Time))
            else:
                time.sleep((TelegramObject.RequestTimer / 1000))

    finally:
        if platform.system() != "Windows":
            # clean after the curses module
            time.sleep(1)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            # Raise the terror of the curses module for a second time. (It's correctly formatted now)
            try:
                raise
            except RuntimeError:
                pass


if __name__ == "__main__":
    Main()
