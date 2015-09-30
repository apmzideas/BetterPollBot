#!/usr/bin/python3.4
# -*- coding: utf-8 -*-


"""
The master file that will hold all the initiated classes and will be used
as the thread or multiprocess initiator.
"""

# standard modules import 
import os
import getpass
import time
import platform
import multiprocessing
# if only windows is supported else use the curses module on linux (-.-)
try:
    import msvcrt
except ImportError:
    import curses

# personal imports
import gobjects
import parsers.comandline
import parsers.configuration
import custom_logging
import language.language
import telegram
import sql.sql_api
import messages.msg_processor


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
        height = maxy
        width = maxx
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
        Configuration = parsers.configuration.ConfigurationParser()

        # Create the language processor
        LanguageMasterObject = language.language.CreateTranslationObject(
            Configuration["Telegram"]["DefaultLanguage"].split(","))

        # This is the language objects only value
        _ = LanguageMasterObject.gettext

        # init parser

        Parser = parsers.comandline.CustomParser(ConfigurationObject=Configuration,
                                            LanguageObject=LanguageMasterObject
                                            )
        Parser.RunParser()
        ParserArguments = Parser.GetArguments()

        # Initialise the rest of the objects.
        MasterLogger = custom_logging.Logger(
            LogToConsole=ParserArguments.PrintToConsole,
            FileName=Configuration["Logging"]["LoggingFileName"],
            MaxLogs=Configuration["Logging"]["MaxLogs"],
            LoggingFormat=Configuration["Logging"]["LoggingFormat"],
            Dateformat=Configuration["Logging"]["Dateformat"],
            LoggingLevel="debug",
            CursesObject=CursesObject)

        MasterLogger.info(_("{AppName} has been started.").format(
            AppName=gobjects.__AppName__
        ))

        if ParserArguments.ApiToken == "":
            MasterLogger.critical(_("No telegram token has been added to the"
                                    " system!")
                                  )
            raise SystemExit

        TelegramObject = telegram.TelegramApi(
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
            # If no database user or password have been sent, get them
            #  from the user.
            # (This is safer than other options.)
            if ParserArguments.DatabaseUser == "":
                ParserArguments.DatabaseUser = input(_("User:") + " ")
            if ParserArguments.DatabasePassword == "":
                ParserArguments.DatabasePassword = getpass.getpass(
                    _("Password:") + " "
                )

            SqlObject = sql.sql_api.Api(
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

                MasterLogger.warning(_("You have used {NrTry} of 3 times:"
                                       ).format(NrTry=str(NrTry)) +
                                     " " + TryAgain, )
                NrTry += 1
            else:
                NoConnection = False

        if NrTry == 3:
            MasterLogger.info(
                _("{AppName} has been stopped, because you didn't input the"
                  " correct user name"
                  " of password.").format(
                    AppName=gobjects.__AppName__))
            raise SystemExit

        # This will be used if the database will be installed.
        if ParserArguments.InstallDatabaseStructure is True:
            InstallDatabaseDefault = _("YES")
            InstallDatabase = input(_("Are you sure you want to install the"
                                      " database structure?") +
                                    _("YES/NO [{Default}]").format(
                                        Default=InstallDatabaseDefault)
                                    )

            if InstallDatabase == "":
                InstallDatabase = InstallDatabaseDefault

            if InstallDatabase.lower() == _("YES").lower():
                MasterLogger.info(_("{AppName} will now start to install "
                                    "the database structure").format(
                    AppName=gobjects.__AppName__)
                )
                SqlCursor = SqlObject.CreateCursor()
                SqlObject.CreateMainDatabase(SqlCursor)
                MasterLogger.info(_("The database has been installed, "
                                    "please restart system."))
            elif InstallDatabase.lower() == _("NO").lower():
                MasterLogger.info(_("Database will not be installed "
                                    "terminating process."))
            raise SystemExit

        ParserArguments.Time = ParserArguments.Time / 1000.0

        # Initialise the main loop (it's a endless loop, it breaks when a
        # key is pressed.)
        MasterLogger.info(_("Exit loop by pressing <Esc>, <q> or <Space>"))
        MasterLogger.info(_("Getting updates from the telegram api."))
        # Add a comment number to the telegram request, so that the old
        # messages will be sorted out.
        Queue = multiprocessing.Queue()
        Queue.put(None)

        while True:
            # check if a key is pressed by user and stop if pressed.
            # if windows use msvcrt
            if platform.system() == "Windows":
                if msvcrt.kbhit():
                    PressedKey = ord(msvcrt.getch())
                    if PressedKey == 27 or PressedKey == 113 or \
                                    PressedKey == 32:
                        MasterLogger.info(_("A user shutdown was requested "
                                            "will now shutdown."))
                        SqlObject.CloseConnection()
                        break

            # use curses
            else:
                PressedKey = CursesObject.getch()
                if PressedKey == 27 or PressedKey == 113 or PressedKey == 32:
                    MasterLogger.info(_("A user shutdown was requested will "
                                        "now shutdown.")
                                      )
                    SqlObject.CloseConnection()
                    break
                else:
                    pass

            # Process the requests

            # Get the updates from the telegram serves.
            if SqlObject.DetectConnection() is True:
                # check if queue has something for us in it
                CommentNumber = []
                while True:
                    if Queue.empty() is False:
                        CommentNumber.append((Queue.get()))
                    else:
                        break

                if len(CommentNumber)==1:
                    CommentNumber = CommentNumber[0]
                elif len(CommentNumber) > 1:
                    CommentNumber = max(CommentNumber)
                else:
                    CommentNumber = None

                Results = TelegramObject.GetUpdates(CommentNumber)

                # Do
                if Results is not None:
                    for Message in Results["result"]:
                        MessageProcessor = (
                            messages.msg_processor.MessageProcessor(
                                Message,
                                LanguageObject=LanguageMasterObject,
                                SqlObject=SqlObject,
                                LoggingObject=MasterLogger,
                                ConfigurationObject=Configuration,
                                BotName=BotName
                            )
                        )

                         # This command sends the message to the user
                        InterpretedMessage = (
                            MessageProcessor.InterpretMessage()
                        )
                        if InterpretedMessage != None:
                            #print(TelegramObject.SendMessage(
                            # InterpretedMessage))
                            TelegramObject.SendMessage(InterpretedMessage)
                        # Set the CommentNumber to a actual ChatId number,
                        # so that the incoming list is always actual.
                        # This number has to be 1 bigger than the oldest unit
                        Queue.put(MessageProcessor.UpdateId + 1)

            # Waits until the next loop should start.
            # Sleep need a second to be parsed, so the given value is
            # transformed
            # from milliseconds to seconds.
            if TelegramObject.RequestTimer == ParserArguments.Time:
                time.sleep((ParserArguments.Time))
            else:
                time.sleep((TelegramObject.RequestTimer / 1000))

    finally:
        Queue.close()
        if platform.system() != "Windows":
            # clean after the curses module
            time.sleep(1)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            # Raise the terror of the curses module for a second time.
            # (It's correctly formatted now)
            try:
                raise
            except RuntimeError:
                pass


if __name__ == "__main__":
    multiprocessing.freeze_support()
    Main()
