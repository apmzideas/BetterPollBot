#!/usr/bin/python
# -*- coding: utf-8 -*-

import GlobalObjects
import hashlib


class Poll(object):
    #In this class all the methodes needed for the poll will be stored.
    def __init__(self, ExternalUserId, PollId = None,):
        
        self.ExternalUserId = ExternalUserId
        self.PollId = PollId
    
    def GetPollName(self):
        pass
        
    def CreateNewPoll(self, Question):
        #This method will create a new poll
        
        #create the poll
        
        #get last Id for the md5-hash needed for the talk
        Hash = hashlib.md5()
        Hash.update(str(Id).encode(encoding='utf_8', errors='strict'))
        Hash = Hash.hexdigest()