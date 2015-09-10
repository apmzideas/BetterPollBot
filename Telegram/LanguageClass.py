#!/usr/bin/python
# -*- coding: utf-8 -*-

import GlobalObjects

import gettext
 

def CreateTranslationObject( Languages = ["de", "en"], localedir='Language',):
    
    if type(Languages) == type('str'):
        Languages = [Languages]
    
    temp = gettext.translation("Telegram", 
                               localedir=localedir,
                               languages=Languages
                               )
    #temp.install()
    return temp

