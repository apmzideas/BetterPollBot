#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe
import time
import os
import subprocess
import GlobalObjects

#sets the current directory in to a variable
DirectoryOfSetup = os.path.abspath("./")

#creates the path to the Directory of the newest build 
DirectoryToBuild = os.path.abspath("..\\Build") + "\\{Date}".format(Date=time.strftime("%Y%m%d%H%M%S", time.gmtime()))
if not os.path.exists(DirectoryToBuild):
    os.makedirs(DirectoryToBuild, exist_ok = True)


print("Building language files")

LanguageFilesArray = [i for i in os.listdir(".\\Language") if not i == "__pycache__"]

#creating the directorys for the language files
print("creating the directorys for the language files")
if not os.path.exists(DirectoryToBuild+"\\Language"):
    os.mkdir(DirectoryToBuild+"\\Language")

for i in LanguageFilesArray:
    DirectoryOfLanguage = DirectoryToBuild+"\\Language\\{NameOfLanguage}".format(NameOfLanguage=i)
    if not os.path.exists(DirectoryOfLanguage):
        os.mkdir(DirectoryOfLanguage)
    DirectoryOfLanguageSub = DirectoryOfLanguage+"\\LC_MESSAGES"
    if not os.path.exists(DirectoryOfLanguageSub):
        os.mkdir(DirectoryOfLanguageSub)
    
    subprocess.call(["py", "C:\\Python34\\Tools\\i18n\\msgfmt.py", 
                     "-o", "{OutputFile}".format(OutputFile=DirectoryOfLanguageSub+"\\Telegram.mo"),
                     "{InputFile}".format(InputFile="{DirectoryOfSetup}\\Language\\{Language}\\LC_MESSAGES\\Telegram.po".format(DirectoryOfSetup=DirectoryOfSetup,
                                                                                                                                Language=i))
                     ])

setup(
      console=[{
               "script": "Main.py",                    ### Main Python script    
               "icon_resources": [(0, "icons\\photo_2015-09-03_20-15-23.ico")], ### Icon to embed into the PE file.
               "dest_base" : GlobalObjects.__AppName__
               }],
      zipfile = "library.zip",
      options = {
                 "py2exe":{
                           "dist_dir":DirectoryToBuild,
                           "optimize":0,
                           "compressed":False,
                           "xref":True,
                           "bundle_files":3,
                           "skip_archive": False
                           }
                 }
      )

# cd ./Language
# echo compiling language files
# for /d %%s in (*) do (
#         IF /I NOT %%s==__pycache__ (
#             msgfmt nl.po --output-file nl.mo
#         )
#     )
# cd ../../
