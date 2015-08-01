#!/usr/bin/python
# -*- coding: utf-8 -*-

import GlobalObjects

import mysql.connector #A additional interface needed for the connection to the MySql-Database
import LoggingClass

import LanguageClass


__author__ = "Adrian Hornung"
__copyright__ = "Copyright (C) Adrian Hornung 2013-2015"
__credits__ = ["Adrian Hornung"]
__license__ = "License GNU General Public License https://www.gnu.org/copyleft/gpl.html"
__version__ = "0.1"
__maintainer__ = "Adrian Hornung"
__email__ = "hornung.adrian@gmial.com"
__status__ = "Development"


class SqlApi(object):
    
    """
    This API enables an easy connection to the mysql driver and to the server with the database 
    
    VARIABLES:
        User                     String                               - contains the Databaseuser
        Password                 String                               - contains the Databaseuserpassword
        DatabaseName             String                               - contains the Databasename
    
    DATABASE STRUCTURE:
        Polltable
            Internal_Poll_Id     Integer (auto_increment)             - conntains the internal polltable id
            External_Poll_Id     Binary(16) or Varchar(36)            - contains the UUID for external use
            Question             Varchar(999)                         - contains the question that has to be asked to the groupe
            MasterUser           Integer                              - contains the internal user Id
            
            PRIMARY KEY (Internal_Poll_Id)
            
        Options
            Id_Option            Integer                              - contains the id of the qption
            Id-Polltable         Integer                              - contains the id of the question (from the polltable)
            Option_Name          Varchar(128)                         - contains the option to be displayed
            
            PRIMARY KEY (Id_Option)
            
        Usertable
            Internal_User_ID     Integer                              - contains the internal user id
            External_User_ID     Integer Usigned                      - contains the external interger
            
            PRIMARY KEY (Internal_User_ID)
            
        SettingsOfPoll
            Setting_Id           Integer                              - contains the internal settings id
            Setting_Name         Varchar(128)                         - contains the name of the setting
            Default_String       Varchar(256)                         - contains the default value for the setting if string
            Default_Integer      Integer                              - contains the default value for the setting if integer
            Default_Boolean      Boolean                              - contains the default value for the setting if boolean
            
            PRIMARY KEY (Setting_Id)
            
        UserSettingOfPoll
            User_Setting_Id
            Setting_Id          Integer                                - contains the settings id
            User_Id             Integer                                - contains the internal user id
            String              Varchar(256)                           - contanis the set string value for the setting
            Interger            Integer                                - contains the set integer value for the setting
            Boolean             Boolean                                - contains the set boolean value for the setting
            
            PRIMARY KEY (User_Setting_Id)
    """
    def __init__(self, User, Password, DatabaseName=None,  Host = "127.0.0.1", Port = "3306"):

        self.User = User
        self.Password = Password
        self.Host = Host
        self.DatabaseName = DatabaseName
        self.Port =  Port
        self.connection = self.CreateConnection()
        
    def CreateConnection(self):
        try:
            config = {
                      'user': self.User,
                      'password': self.Password,
                      'host': self.Host,
                      'port': 3306,
                      'raise_on_warnings': True,
                      }
            if self.DatabaseName:
                config['database'] = self.DatabaseName
    
            return  mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print(GlobalObjects.ObjectHolder.LanguageObject.GetString("DatabaseAutentificationError"))
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(GlobalObjects.ObjectHolder.LanguageObject.GetString("NotExistingDatabase"))
            else:
                print(err)
    
    def CreateCursor(self):
        #this methode will ceate the cursor needet for the connection to the server
        return self.connection.cursor()
    
    def DestroyCursor(self, Cursor):
        #this methode closes the connection opend by the cursor
        return Cursor.close()
    
    def CreateDatabase(self, Cursor, DatabaseName):
        try:
            Cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {0} DEFAULT CHARACTER SET 'utf8'".format(DatabaseName))
        except mysql.connector.Error as err:
            print(GlobalObjects.ObjectHolder["LanguageClass"].GetString('DatabaseDeleteError') + " {0}".format(err))
    
    def DeleteDatabase(self, Cursor, DatabaseName):
        try:
            Cursor.execute(
            "DROP DATABASE {0}".format(DatabaseName))
        except mysql.connector.Error as err:
            print(GlobalObjects.ObjectHolder["LanguageClass"].GetString('DatabaseDeleteError') +"{0}".format(err))
            exit(1)
            
    def CreateTables(self, Cursor, TableName, TableData, IfNotExists = True):
        """A methode to dynamicaly create a table entry to the database
        
        HOW TO USE:
            import collections 
            TableData = (
                ('Id', 'INT UNSIGNED NOT NULL AUTO_INCREMENT'),
                ('PRIMARY KEY', 'ID')
            )
            
            #function call
            SqlApl.CreateTables('Test', TableDataifNotExists = True,)"""
        try:
            Querry = "CREATE TABLE "
            if IfNotExists:
                Querry += "IF NOT EXISTS "
                
                Querry += TableName + " ("
                for i in range(len(TableData)):
                    if ( TableData[i][0].lower() != 'primary key'):
                        Querry += TableData[i][0] +" " + TableData[i][1] + ", "
                        #print(TableData[i][0], TableData[i][1])
                    else: 
                        Querry += TableData[i][0] +" (" + TableData[i][1] + ")"
                
                Querry += ")"
                
                Cursor.execute(Querry)
                print(Querry)
        except mysql.connector.Error as err:    
            print(GlobalObjects.ObjectHolder["LanguageClass"].GetString('DatabaseTableCreationError') +"{0}".format(err))
            
    def Dummy(self):
        print(GlobalObjects.ObjectHolder["LanguageClass"].GetString('NotExistingDatabase'))

if __name__ == "__main__":
    print("online")
    import Main
    Main.ObjectInitialiser()
    a = SqlApi("root", "Password")
    Cursor = a.CreateCursor()
    a.CreateDatabase(Cursor, "Test")
    a.CreateTables(Cursor,"Test.TestTable", [['Id', 'INT UNSIGNED NOT NULL AUTO_INCREMENT'], ['PRIMARY KEY', 'ID']], IfNotExists = True)
    a.DeleteDatabase(Cursor, "Test")
    a.DestroyCursor(Cursor)
    print("offline")
    
    