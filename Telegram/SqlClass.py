#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3


class SqlApi(object):
    
    """
        DBName string - contains the Databasename
    """
    def __init__(self, DBName, Tables):
        self.DBName = DBName
        self.Tables = Tables
    
    