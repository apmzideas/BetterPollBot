#!/usr/bin/python
# -*- coding: utf-8 -*-


''' The master file that will hold all the initiated classes and will be used as the thread deployer.
    
'''


import GlobalObjects
import LanguageClass
import TelegramClass
import SqlClass

import ErrorClasses

def ObjectInitialiser():
    
    GlobalObjects.ObjectHolder["LanguageClass"] = LanguageClass.Languages('gerDE')
    GlobalObjects.ObjectHolder["TelegramClass"] = TelegramClass.TelegramApi('')
    
    


if __name__ == "__main__":
    ObjectInitialiser()
    a = SqlClass.SqlApi("root", "Password", "test")
    a.Dummy()
    print(GlobalObjects.ObjectHolder)