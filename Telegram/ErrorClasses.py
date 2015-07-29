#!/usr/bin/python
# -*- coding: utf-8 -*-

''' 
    some error classes
'''

__author__ = "Adrian Hornung"
__copyright__ = "Copyright (C) Adrian Hornung 2013-2015"
__credits__ = ["Adrian Hornung"]
__license__ = "License GNU General Public License https://www.gnu.org/copyleft/gpl.html"
__version__ = "0.1"
__maintainer__ = "Adrian Hornung"
__email__ = "hornung.adrian@gmial.com"
__status__ = "Development"

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

if __name__ == "__main__":
    try:
        raise LanguageImportError("Foo")
    except LanguageImportError as Error:
        print("The Connection to the TelegramServer failed")
    
