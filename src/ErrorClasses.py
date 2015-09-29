#!/usr/bin/python
# -*- coding: utf-8 -*-

''' 
    Some error classes needed for error and exception handling.
'''

class TokenError(Exception):
    """
    An error handling class for an wrong API token or connection error.
    """
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)
    
class LanguageImportError(Exception):
    """
    An error handling class for a not existing language file.
    """
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

class MissingArguments(Exception):
    """
    An error handling class for a missing argument.
    """
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

