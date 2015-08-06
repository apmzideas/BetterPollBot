#!/usr/bin/python
# -*- coding: utf-8 -*-

import configparser
import collections


class Configuration(configparser.ConfigParser):
    def __init__(self, FileName = 'config.ini', **Configuration ):
        
        #Custom configurable filename
        self.FileName = FileName
        
        #variables needed for the configparser 
        self.Default = None
        self.DictType = collections.OrderedDict
        self.AllowNoValue = False
        self.Delimiters = ('=', ':')
        self.CommentPrefixes = ('#', ';')
        self.InlineCommentPrefixes = None
        self.Strict = True
        self.EmtyLineInValues = True
        self.DefaultSelection = configparser.DEFAULTSECT
        self.Interpolation = configparser.BasicInterpolation()
        
        
        #the Configuration directory is to be filled with the parameters of the configparser
        if 0 < len(Configuration):
            if 'defaults' in Configuration:
                self.Default = Configuration['defaults']
            if 'dict_type' in Configuration:
                self.DictType = Configuration['dict_type']
            if 'allow_no_value' in Configuration:
                self.AllowNoValue = Configuration['allow_no_value']
            if 'delimiters' in Configuration:
                self.Delimiters = Configuration['delimiters']
            if 'comment_prefixes' in Configuration:
                self.CommentPrefixes = Configuration['comment_prefixes']
            if 'inline_comment_prefixes' in Configuration:
                self.InlineCommentPrefixes = Configuration['inline_comment_prefixes']
            if 'strict' in Configuration:
                self.Strict = Configuration['strict']
            if 'empty_lines_in_values' in Configuration:
                self.EmtyLineInValues = Configuration['empty_lines_in_values']
            if 'default_section' in Configuration:
                self.DefaultSelection = Configuration['default_section']
            if 'interpolation' in Configuration:
                self.Interpolation = Configuration['interpolation']
            
        
        super(Configuration, self).__init__(defaults=self.Default,
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
        