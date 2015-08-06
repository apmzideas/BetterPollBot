#!/usr/bin/python
# -*- coding: utf-8 -*-


class Querry(object):
    """
    This class will enable to automatically create the correct querry  
    """
    __Select__ =  "SELECT"
    
    __InnerJoin = "INNER JOIN"
    __LeftJoin = "LEFT JOIN"
    __RightJoin = "RIGHT JOIN"
    __FullJoin = "FULL JOIN"
    
    
    def __init__ (self):
        self.Tables
    
    def SelectFromColumns(self, ColumnNames):
        # A methode to know of the to be selected columns
        pass
    
    def SelectColumn(self, ColumnName):
        self.SelectColumns(list(ColumnName))
        
    
    def AddTable(self, TableName):