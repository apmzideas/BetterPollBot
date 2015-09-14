#!/usr/bin/python
# -*- coding: utf-8 -*-

''' 
    some error classes
'''

class TokenError(Exception):
    #A Error Handling Class for an Wrong Token or Conection error
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)
    
class LanguageImportError(Exception):
    #A Error Handling Class for a not existing Language
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

class MissingArguments(Exception):
    #A Error Handling Class for an missing argument
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

if __name__ == "__main__":
    try:
        raise LanguageImportError("Foo")
    except LanguageImportError as Error:
        print("The Connection to the TelegramServer failed")

