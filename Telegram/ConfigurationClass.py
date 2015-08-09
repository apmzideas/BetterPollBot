#!/usr/bin/python
# -*- coding: utf-8 -*-

import configparser
import os
import collections


class ConfigurationParser(configparser.ConfigParser):
    def __init__(self, FileName = "config.ini", **Configuration ):
        
        #Custom configurable filename
        self.FileName = FileName
        self.ResetConfigurationFile = False
        self.Encoding = "utf-8"
        
        #variables needed for the configparser 
        self.Default = None
        self.DictType = collections.OrderedDict
        self.AllowNoValue = False
        self.Delimiters = ("=", ":")
        self.CommentPrefixes = ("#", ";")
        self.InlineCommentPrefixes = None
        self.Strict = True
        self.EmtyLineInValues = True
        self.DefaultSelection = configparser.DEFAULTSECT
        self.Interpolation = configparser.BasicInterpolation()
        
        
        #the Configuration directory is to be filled with the parameters of the configparser
        if 0 < len(Configuration):
            #for the own class
            if "reset_configuration" in Configuration:
                self.ResetConfigurationFile = Configuration["reset_configuration"]
                
            #for the super class the configparser
            if "defaults" in Configuration:
                self.Default = Configuration["defaults"]
            if "dict_type" in Configuration:
                self.DictType = Configuration["dict_type"]
            if "allow_no_value" in Configuration:
                self.AllowNoValue = Configuration["allow_no_value"]
            if "delimiters" in Configuration:
                self.Delimiters = Configuration["delimiters"]
            if "comment_prefixes" in Configuration:
                self.CommentPrefixes = Configuration["comment_prefixes"]
            if "inline_comment_prefixes" in Configuration:
                self.InlineCommentPrefixes = Configuration["inline_comment_prefixes"]
            if "strict" in Configuration:
                self.Strict = Configuration["strict"]
            if "empty_lines_in_values" in Configuration:
                self.EmtyLineInValues = Configuration["empty_lines_in_values"]
            if "default_section" in Configuration:
                self.DefaultSelection = Configuration["default_section"]
            if "interpolation" in Configuration:
                self.Interpolation = Configuration["interpolation"]
            
        #This method initializes the superclass with all the possible parameters.
        super(ConfigurationParser, self).__init__(defaults=self.Default,
                                            dict_type=self.DictType,
                                            allow_no_value=self.AllowNoValue, 
                                            delimiters=self.Delimiters,
                                            comment_prefixes=self.CommentPrefixes, 
                                            inline_comment_prefixes=self.InlineCommentPrefixes, 
                                            strict=self.Strict, 
                                            empty_lines_in_values= self.EmtyLineInValues, 
                                            default_section= self.DefaultSelection, 
                                            interpolation=self.Interpolation
                                            )
        
        #This commands sets the parser sensitive to upper- and lowercase.
        self.optionxform = lambda option: option
        
        #check if configfile exists
        if os.path.isfile(self.FileName) is not True:
            self.WriteDefaultConfigurationFile()
            #raise SystemExit
        elif self.ResetConfigurationFile is True:
            self.WriteDefaultConfigurationFile()
        else:
            self.read(self.FileName)
            
            
    def WriteDefaultConfigurationFile(self):
        #a methode to write the default configuration to the .ini file
        
        #The Title of the file 
        self["Configuration"] = {}
        
        self["MySQL Connection Parameter"] = {"DatabaseName": "BetterPollBotDatabase",                                            
                                            "DatabaseHost": "127.0.0.1",
                                            "DatabasePort": 3306,
                                            }
        
        self["Language"] = {"Language": "enGB",
                            "Allow language change": True
                           }
        
        self["Logging"] = {"LogToFile": True,
                           "LoggingFileName":'log.txt',
                           }
       
       #Writes the default configuration in to the correct file 
        with open(self.FileName, "w") as configfile:
            self.write(configfile)
            
    def ReadConfigurationFile(self):
        #This methode will read the configuration from the self.file
        self.read(self.FileName,)
        
        return True
    
if __name__ == "__main__":
    print("Online")
    a = ConfigurationParser(reset_configuration = False)
    a.ReadConfigurationFile()
    print(type(a["MySQL Connection Parameter"]["DatabaseName"]))
    print("Offline")
    