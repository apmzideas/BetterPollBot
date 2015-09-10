#!/usr/bin/python
# -*- coding: utf-8 -*-

''' a logging tool'''

import logging

#read logging info
class Logger(logging.Logger):

    def __init__(self, 
                 #ConfigurationName='config.ini', 
                 LogToConsole=False,
                 FileName = "log.txt",
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
        super().__init__(name="Logger")
        self.setLevel(LoggingLevel)
        
        FileHandler = logging.FileHandler(filename=FileName)
        
        FileHandler.setFormatter(Formatter)
        
        self.addHandler(FileHandler)
        
        if LogToConsole == True:
            ConsoleHandler = logging.StreamHandler()
            ConsoleHandler.setFormatter(Formatter)
            self.addHandler(ConsoleHandler)

        
if __name__ == '__main__':
    log_to = False
    c = Logger()
    c.info("Hallo?")
    c.error("Test")

