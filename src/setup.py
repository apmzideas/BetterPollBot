#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe
import time
import os
import subprocess

# print nice messages

def LogPrint(Message, Type = "INFO"):

    print("[{DateOfMessage}] - [{TypeOfMessage}] - "
          "{Message}".format(
        DateOfMessage = time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime()),
        TypeOfMessage = Type.upper(),
        Message = Message
    )
    )

# Set the compiler time
DateOfCompiling = time.strftime("%Y%m%d%H%M%S", time.gmtime())


# Modification of the gobjects.py
if os.path.isfile("gobjects.py"):
    os.rename("gobjects.py", "GlobalObjects_old.py")

    with open("GlobalObjects_old.py") as FileInput:
        with open("gobjects.py", "w") as FileOutPut:
            for Line in FileInput:
                if Line.startswith("__release__"):
                    FileOutPut.write("__release__ = {Date}\n".format(Date = DateOfCompiling))
                else:
                    FileOutPut.write(Line)

    if os.path.isfile("GlobalObjects_old.py"):
        os.remove("GlobalObjects_old.py")

# Modification of the docs/conf.py
File = "../docs/conf.py"
FileOld = "../docs/conf_old.py"
if os.path.isfile(File):
    os.rename(File, FileOld)
    
    with open(FileOld) as FileInput:
        with open(File, "w") as FileOutPut:
            for Line in FileInput:
                if Line.startswith("release"):
                    FileOutPut.write("release = '{Date}'\n".format(Date = DateOfCompiling))
                else:
                    FileOutPut.write(Line)
    
    if os.path.isfile(FileOld):
        os.remove(FileOld)        

# This Module will be modified befor the import.
import gobjects

LogPrint("release build: " + str(gobjects.__release__))
#sets the current directory in to a variable
DirectoryOfSetup = os.path.abspath("./")
 
#creates the path to the Directory of the newest build 
DirectoryToBuild = os.path.abspath("..\\Build") + "\\{Date}".format(Date=DateOfCompiling)
if not os.path.exists(DirectoryToBuild):
    os.makedirs(DirectoryToBuild, exist_ok = True)
 
LogPrint("Building language files")

# Get the stupid __pycache__ folder
LanguageFilesArray = [i for i in os.listdir(".\\language") if i != "__pycache__" and i != "language.py" and i != "__init__.py"]

#creating the directorys for the language files
LogPrint("creating the directorys for the language files")

if not os.path.exists(DirectoryToBuild+"\\language"):
    os.mkdir(DirectoryToBuild+"\\language")
 
for i in LanguageFilesArray:
    DirectoryOfLanguage = DirectoryToBuild+"\\language\\{NameOfLanguage}".format(NameOfLanguage=i)
    
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
               "script": "main.py",
               # Icon to embed into the PE file.  
               "icon_resources": [(0, "icons\\photo_2015-09-03_20-15-23.ico")],
               # The application name
               "dest_base" : gobjects.__AppName__
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

