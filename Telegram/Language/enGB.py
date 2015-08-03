#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    A class to get the correct language file and Data
"""

class language(object):
    def __init__(self):
        
        #Strings for Connection Errors with Telegram
        self.TokenError = "The token you are using has not been found in the system ."
        self.FailedTelegramConnection = "The Connection to the TelegramServer failed, please try again later."
        
        #String for DatabaseErrors
        self.DatabaseAutentificationError = "Something is wrong with your user name or password."
        self.NotExistingDatabase = "Database does not exist."
        self.DatabaseDeleteError = "Failed to delete database, please delete manually: "
        self.DatabaseTableCreationError = "Failed to create table: "
        self.DatabaseQuerryError = "The executet querry failed, please contact your administrator: "
        #Strings for LanguageErrors
        self.LanguageFileLoadingError = "The languagefiles could not be loaded or found, insted the english language will be used." 