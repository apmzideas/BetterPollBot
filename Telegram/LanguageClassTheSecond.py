#!/usr/bin/python
# -*- coding: utf-8 -*-

import GlobalObjects

import os, sys
import locale
import gettext
 
# Change this variable to your app name!
#  The translation files will be under
#  @LOCALE_DIR@/@LANGUAGE@/LC_MESSAGES/@APP_NAME@.mo
APP_NAME = GlobalObjects.__AppName__

def CreateTranslationObject(Domain="Telegram", localedir='Language', Languages = ["de", "en"]):
    temp = gettext.translation("Telegram", localedir=localedir, languages=Languages)
    #temp.install()
    return temp

