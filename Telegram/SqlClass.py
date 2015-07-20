#!/usr/bin/python
import sqlite3


class SqlApi(object):
    
    """
        DBName string - contains the Databasename
    """
    def __init__(self, DBName, Tables):
        self.DBName = DBName
        self.Tables = Tables
    
    