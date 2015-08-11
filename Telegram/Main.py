#!/usr/bin/python
# -*- coding: utf-8 -*-


''' The master file that will hold all the initiated classes and will be used as the thread deployer.
    
'''


import GlobalObjects
import ConfigurationClass
import LoggingClass
import LanguageClass
import TelegramClass
import SqlClass

import ErrorClasses

def ObjectInitialiser():
    GlobalObjects.ObjectHolder["ConfigurationClass"] = ConfigurationClass.ConfigurationParser()
    GlobalObjects.ObjectHolder["ConfigurationClass"].ReadConfigurationFile()
    GlobalObjects.ObjectHolder["LoggingClass"] = LoggingClass.Logger(config_name='config.ini', log_to_file=False)
    GlobalObjects.ObjectHolder["LanguageClass"] = LanguageClass.Languages('gerDE')
    GlobalObjects.ObjectHolder["SqlClass"] = SqlClass.SqlApi("root", "Password", 
                                                             GlobalObjects.ObjectHolder["ConfigurationClass"]["MySQL Connection Parameter"]["DatabaseName"]
                                                             )
    #GlobalObjects.ObjectHolder["TelegramClass"] = TelegramClass.TelegramApi('80578257:AAEt5tHodsbD6P3hqumKYFJAyHTGWEgcyEY')
    
    


if __name__ == "__main__":
    
    ObjectInitialiser()

    Cursor = GlobalObjects.ObjectHolder["SqlClass"].CreateCursor(Buffered=False, Dictionary=True, )
    GlobalObjects.ObjectHolder["LoggingClass"].create_log('this is a test', "Error")
