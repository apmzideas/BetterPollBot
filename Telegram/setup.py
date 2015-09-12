#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe
import time
import os
import subprocess

# print nice messages

def LogPrint(Message, Type = "INFO"):

    print("[{DateOfMessage}] - [{TypeOfMessage}] - {Message}".format(
                                                                   DateOfMessage = time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime()),
                                                                   TypeOfMessage = Type.upper(),
                                                                   Message = Message
                                                                   ))

# Set the compiler time
DateOfCompiling = time.strftime("%Y%m%d%H%M%S", time.gmtime())

# Modification of the GlobalObjects
if os.path.isfile("GlobalObjects.py"):
    os.rename("GlobalObjects.py", "GlobalObjects_old.py")
with open("GlobalObjects_old.py") as FileInput:
    with open("GlobalObjects.py", "w") as FileOutPut:
        for Line in FileInput:
            if Line.startswith("__release__"):
                FileOutPut.write("__release__ = {Date}\n".format(Date=DateOfCompiling))
            else:
                FileOutPut.write(Line)

if os.path.isfile("GlobalObjects_old.py"):
    os.remove("GlobalObjects_old.py")

# This Module will be modified befor the import.
import GlobalObjects

LogPrint("release build: " + str(GlobalObjects.__release__))
#sets the current directory in to a variable
DirectoryOfSetup = os.path.abspath("./")
 
#creates the path to the Directory of the newest build 
DirectoryToBuild = os.path.abspath("..\\Build") + "\\{Date}".format(Date=DateOfCompiling)
if not os.path.exists(DirectoryToBuild):
    os.makedirs(DirectoryToBuild, exist_ok = True)
 
LogPrint("Building language files")

# Get the stupid __pycache__ folder
LanguageFilesArray = [i for i in os.listdir(".\\Language") if i != "__pycache__" and i != "LanguageClass.py" and i != "__init__.py"]
print(LanguageFilesArray)
#creating the directorys for the language files
LogPrint("creating the directorys for the language files")

if not os.path.exists(DirectoryToBuild+"\\Language"):
    os.mkdir(DirectoryToBuild+"\\Language")
 
for i in LanguageFilesArray:
    DirectoryOfLanguage = DirectoryToBuild+"\\Language\\{NameOfLanguage}".format(NameOfLanguage=i)
    
    if not os.path.exists(DirectoryOfLanguage):
        os.mkdir(DirectoryOfLanguage)
    DirectoryOfLanguageSub = DirectoryOfLanguage+"\\LC_MESSAGES"
    
    if not os.path.exists(DirectoryOfLanguageSub):
        os.mkdir(DirectoryOfLanguageSub)
        
    LogPrint("Compiling language file {Name}".format(Name = i))
    
    #compiling
    subprocess.call(["py", "C:\\Python34\\Tools\\i18n\\msgfmt.py", 
                     "-o", "{OutputFile}".format(OutputFile=DirectoryOfLanguageSub+"\\Telegram.mo"),
                     "{InputFile}".format(
                                          InputFile="{DirectoryOfSetup}\\Language\\"
                                          "{Language}\\LC_MESSAGES\\Telegram.po".format(
                                                                                        DirectoryOfSetup=DirectoryOfSetup,
                                                                                        Language=i)
                                          )
                     ])
#start compiling the source code
setup(
      console=[{
               # Main Python script
               "script": "Main.py",                      
               # Icon to embed into the PE file.  
               "icon_resources": [(0, "icons\\photo_2015-09-03_20-15-23.ico")],
               # The application name
               "dest_base" : GlobalObjects.__AppName__
               }],
      zipfile = "library.zip",
      options = {
                 "py2exe":{
                           "dist_dir":DirectoryToBuild,
                           "optimize":0,
                           #"includes": ["Sql.SqlClass"],
                           "compressed":False,
                           "xref":True,
                           "bundle_files":3,
                           "skip_archive": False
                           }
                 }
      )

