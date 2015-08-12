#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    A class to get the correct language file and Data
"""

import ErrorClasses
import GlobalObjects

class Languages(object):
    def __init__(self, languageName):
        self.languageName = "Language." + languageName
        #the object that holds the languagedata 
        self.LanguageObject = self.LaodLanguageFile(self.languageName)
    
    #A Methode to load the correct language file if needed
    def LaodLanguageFile(self, languagesName):
        try:
            return __import__(languagesName, fromlist=['']).language()
        except ImportError:
            try:
                raise ErrorClasses.LanguageImportError("The languagefiles could not be loaded")
            except ErrorClasses.LanguageImportError as Error:
                self.LanguageObject = self.LaodLanguageFile("Language.enGB")
                print(self.GetString("LanguageFileLoadingError"))
                
                
    def GetString(self, StringToSearch):
        #The methode to get the correct string
        
        Temp = None
        #Try to get the string in the correct language
        try:
            Temp = getattr(self.LanguageObject, StringToSearch) 
        except AttributeError:
            try:
                Temp = getattr(self.LaodLanguageFile("Language.enGB"), StringToSearch)
            except ErrorClasses.LanguageImportError:
                self.LanguageObject = self.LaodLanguageFile("Language.enGB")
                print(self.GetString(self.LanguageObject, "LanguageFileLoadingError"))
        return Temp
            
if __name__ == "__main__":
    a = Languages("enGB")
    print(a.GetString("NotExistingDatabase"))
    
    a = Languages("gerDE")
    print(a.GetString("DatabaseTableCreationError"))
    print(a.GetString("TokenError"))