#!/usr/bin/python
# -*- coding: utf-8 -*-

''' a logging tool'''

import logging
import logging.handlers
import multiprocessing
import os

#read logging info
class Logger(logging.Logger):
    # This class is a child class of the logging.Logger, it simplifies the 
    # customisation and throuth the overriding of the parent methodes listed below
    # it makes the Logger thread and multiprocess safe.
    def __init__(self, 
                 #ConfigurationName='config.ini', 
                 LogToConsole=False,
                 FileName = "log.txt",
                 MaxLogs = 20,
                 LoggingFormat = "[%(asctime)s] - [%(levelname)s] - %(message)s",
                 Dateformat = "%d.%m.%Y %H:%M:%S",
                 LoggingLevel = "debug"
                 ):
        
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
        # This method extends the debug method of the parent
        # and makes the function multiprocess safe.
        self.Lock.acquire()
        super().debug(msg, *args, **kwargs)
        self.Lock.release()
    
    def info(self, msg, *args, **kwargs):
        # This method extends the info method of the parent
        # and makes the function multiprocess safe.
        self.Lock.acquire()
        super().info(msg, *args, **kwargs)
        self.Lock.release()
    
    def warning(self, msg, *args, **kwargs):
        # This method extends the warning method of the parent
        # and makes the function multiprocess safe.
        self.Lock.acquire()
        super().warning(msg, *args, **kwargs)
        self.Lock.release() 
        
    def error(self, msg, *args, **kwargs):
        # This method extends the error method of the parent
        # and makes the function multiprocess safe.
        self.Lock.acquire()
        super().error(msg, *args, **kwargs)
        self.Lock.release()                
    
    def critical(self, msg, *args, **kwargs):
        # This method extends the critical method of the parent
        # and makes the function multiprocess safe.
        self.Lock.acquire()
        super().critical(msg, *args, **kwargs)
        self.Lock.release()  
        
if __name__ == '__main__':
    log_to = False
    c = Logger()
    c.info("Hallo?")
    c.error("Test")

