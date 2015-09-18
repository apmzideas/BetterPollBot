#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This module defines functions and classes which implement a flexible 
event logging system for applications and libraries.
'''

import logging
import logging.handlers
import multiprocessing
import os

#read logging info
class Logger(logging.Logger):
    """
    This class is a child class of the logging.Logger.
    
    It simplifies the customisation and throuth the extending of some 
    parent methodes listed below, it makes the Logger thread and
    multiprocess safe.
    """

    def __init__(self, 
                 LogToConsole=False,
                 FileName = "log.txt",
                 MaxLogs = 20,
                 LoggingFormat = "[%(asctime)s] - [%(levelname)s] - %(message)s",
                 Dateformat = "%d.%m.%Y %H:%M:%S",
                 LoggingLevel = "debug"
                 ):
        """
        An init function in which the configuration is written.
        
        Variables:
            LogToConsole                  boolean
                if the logger shall log to console and to file or
                just to the file
                
            FileName                      string
                the file to log to
                
            MaxLogs                       integer
                the maximal amout of old logs are written.
                Example:
                
                .. code-block:: python
                
                    log.txt\n
                    log.txt.1\n
                    log.txt.2\n
                    ...
                    
            LoggingFormat                 string
                the format of the string that has to be logged
                
                Example:
                
                    ``%(asctime)s`` 
                        Human-readable time when the LogRecord was 
                        created. By default this is of the form 
                        ‘2003-07-08 16:49:45,896’ (the numbers after 
                        the comma are millisecond portion of the time).
                    ``%(levelname)s``
                        Text logging level for the message ('DEBUG', 
                        'INFO', 'WARNING', 'ERROR', 'CRITICAL').
                    
                For the full list of possible attributes:
                    https://docs.python.org/3/library/logging.html#logrecord-attributes
            
            Dateformat                  string
                configures the date string format
                
                Example:
                
                    ``%Y-%m-%d %H:%M:%S``
                
                For the full lsit of possibles attributes:
                    https://docs.python.org/3.4/library/time.html#time.strftime
                
            LoggingLevel                string
                set's the minium logging value
                Explanation:
                    
                    ========  =============
                    Level     Numeric value
                    ========  =============
                    CRITICAL      50
                    ERROR         40
                    WARNING       30
                    INFO          20
                    DEBUG         10
                    NOTSET        0
                    ========  ============= 
                    
        """
        PossibleLoggingLevel = {"NOTSET": logging.NOTSET,
                                "DEBUG": logging.DEBUG,
                                "INFO": logging.INFO,
                                "WARNING": logging.WARNING,
                                "ERROR": logging.ERROR,
                                "CRITICAL": logging.CRITICAL
                                }
        if LoggingLevel.upper() in PossibleLoggingLevel.keys():
            LoggingLevel = PossibleLoggingLevel[LoggingLevel.upper()]
        else:
            LoggingLevel = PossibleLoggingLevel["DEBUG"]
            
        Formatter = logging.Formatter(fmt=LoggingFormat,
                                      datefmt=Dateformat,)
        
        # Initialise the superclass 
        super().__init__(name="DefaultLogger")
        self.setLevel(LoggingLevel)
        
        LoggingDictionary = os.path.abspath("logs")
        
        if not os.path.isdir(LoggingDictionary):
            os.mkdir(LoggingDictionary)
        
        FilePath = LoggingDictionary + "/" + FileName
        
        # This filehandler will see that there will be no problems with the 
        # file size of the logs.
        # The file being written to is always app.log. 
        # When this file is filled, it is closed and renamed to app.log.1,
        # and if files app.log.1, app.log.2, etc. exist, then they are renamed 
        # to app.log.2, app.log.3 etc. respectively.
        
        FileHandler = logging.handlers.RotatingFileHandler(
                                                  filename=FilePath,
                                                  mode='a',
                                                  # exacly 20 kilobites
                                                  maxBytes=20480,
                                                  backupCount=MaxLogs
                                                  )
        
        FileHandler.setFormatter(Formatter)
        
        self.addHandler(FileHandler)
        
        self.Lock = multiprocessing.Lock()
        
        if LogToConsole == True:
            ConsoleHandler = logging.StreamHandler()
            ConsoleHandler.setFormatter(Formatter)
            self.addHandler(ConsoleHandler)
    
    def debug(self, msg, *args, **kwargs):
        """
        This method extends the debug method of the parent.
        
        It makes the parent function multiprocess safe.
        Logs a message with level DEBUG on the root logger.
        
        Variables:
            from the python documentation:
                Logs a message with level DEBUG on the root logger. 
                The msg is the message format string, and the args are 
                the arguments which are merged into msg using the 
                string formatting operator. (Note that this means that 
                you can use keywords in the format string, together 
                with a single dictionary argument.)

                There are three keyword arguments in kwargs which are 
                inspected: ``exc_info`` which, if it does not evaluate as 
                false, causes exception information to be added to the 
                logging message. If an exception tuple (in the format 
                returned by ``sys.exc_info())`` is provided, it is used; 
                otherwise, ``sys.exc_info()`` is called to get the 
                exception information.

                The second optional keyword argument is ``stack_info``, 
                which defaults to ``False``. If true, stack information 
                is added to the logging message, including the actual 
                logging call. Note that this is not the same stack 
                information as that displayed through specifying 
                ``exc_info``: The former is stack frames from the bottom 
                of the stack up to the logging call in the current 
                thread, whereas the latter is information about stack 
                frames which have been unwound, following an exception, 
                while searching for exception handlers.

                You can specify ``stack_info`` independently of ``exc_info``, 
                e.g. to just show how you got to a certain point in 
                your code, even when no exceptions were raised. The 
                stack frames are printed following a header line which 
                says:

                Stack (most recent call last):

                This mimics the Traceback (most recent call last): 
                which is used when displaying exception frames.

                The third optional keyword argument is extra which 
                can be used to pass a dictionary which is used to 
                populate the ``__dict__`` of the LogRecord created for the 
                logging event with user-defined attributes. These 
                custom attributes can then be used as you like. 
                For example, they could be incorporated into logged
                messages. For example:
                
                .. code-block:: python\n
                    FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s '\\
                        '%(message)s'
                    logging.basicConfig(format=FORMAT)
                    d = {'clientip': '192.168.0.1', 'user': 'fbloggs'}
                    logging.warning('Protocol problem: %s', 
                        'connection reset', 
                        extra=d
                    )

                would print something like:\n
                .. code-block:: python\n
                    2006-02-08 22:20:02,165 192.168.0.1 fbloggs  
                    Protocol problem: connection reset
            
                The keys in the dictionary passed in extra should not 
                clash with the keys used by the logging system. (See 
                the Formatter documentation for more information on
                which keys are used by the logging system.)  
        """

        self.Lock.acquire()
        super().debug(msg, *args, **kwargs)
        self.Lock.release()
    
    def info(self, msg, *args, **kwargs):
        """
        This method extends the info method of the parent.
        
        Logs a message with level INFO on the root logger.
        It makes the parent function multiprocess safe.
        See debug for more informations about the variables.
        """
        
        self.Lock.acquire()
        super().info(msg, *args, **kwargs)
        self.Lock.release()
    
    def warning(self, msg, *args, **kwargs):
        """
        This method extends the warning method of the parent.
        
        Logs a message with level WARNING on the root logger.
        It makes the parent function multiprocess safe.
        See debug for more informations about the variables.
        """

        self.Lock.acquire()
        super().warning(msg, *args, **kwargs)
        self.Lock.release() 
        
    def error(self, msg, *args, **kwargs):
        """
        This method extends the warning method of the parent.
        
        Logs a message with level ERROR on the root logger. 
        It makes the parent function multiprocess safe.
        See debug for more informations about the variables.
        """
        
        self.Lock.acquire()
        super().error(msg, *args, **kwargs)
        self.Lock.release()                
    
    def critical(self, msg, *args, **kwargs):
        """
        This method extends the warning method of the parent.

        Logs a message with level CRITICAL on the root logger.
        It makes the parent function multiprocess safe.
        See debug for more informations about the variables.
        """
        
        self.Lock.acquire()
        super().critical(msg, *args, **kwargs)
        self.Lock.release()  
    
    def exception(self, msg, *args, **kwargs):
        """
        This method extends the exception method of the parent.
        
        Logs a message with level ERROR on the root logger.
        It makes the parent function multiprocess safe.        
        This function should only be called from an exception handler.
        See debug for more informations about the variables.
        """
        
        self.Lock.acquire()
        super().exception( msg, *args, **kwargs)
        self.Lock.release() 

    def log(self, level, msg, *args, **kwargs):
        """
        This method extends the warning method of the parent.
        
        Logs a message with level level on the root logger.         
        It makes the parent function multiprocess safe.        
        See debug for more informations about the variables.
        """
        
        self.Lock.acquire()
        super().log(level, msg, *args, **kwargs)
        self.Lock.release() 
        
        
if __name__ == '__main__':
    log_to = False
    c = Logger(True)
    c.info("Hallo?")
    c.error("Test")

