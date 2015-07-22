#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    A class to get the correct language file and Data
"""

import ErrorClasses
import importlib

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
                print("The languagefiles could not be loaded")
                exit()
                
                
    def GetString(self, StringToSearch):
        try:
            return  getattr(self.LanguageObject, StringToSearch) 
        except ErrorClasses.LanguageImportError:
            pass
        try:
            return getattr(LaodLanguageFile("enGB"), StringToSearch)
        except ErrorClasses.LanguageImportError:
            print(self.GetString(LaodLanguageFile("enGB"), ))
            
            
if __name__ == "__main__":
    a = Languages("enGB")
    print(a.GetString("NotExistingDatabase"))
    a = Languages("gerDE")
    print(a.GetString("NotExistingDatabase"))