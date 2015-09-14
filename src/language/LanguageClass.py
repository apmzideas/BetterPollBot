#!/usr/bin/python
# -*- coding: utf-8 -*-

import gettext
 

def CreateTranslationObject( Languages = ["de", "en"], localedir='language',):
    """
    This function returns a gettext object.
    """
    if type(Languages) == type('str'):
        Languages = [Languages]
    
    temp = gettext.translation("Telegram", 
                               localedir=localedir,
                               languages=Languages
                               )
    print(temp.info())
    print(temp.output_charset())
    print(temp.charset())
    #temp.install()
    return temp

if __name__ == "__main__":
    i = CreateTranslationObject(localedir="../language")

