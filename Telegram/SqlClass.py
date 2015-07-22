#!/usr/bin/python
# -*- coding: utf-8 -*-

import mysql.connector #A additional interface needed for the connection to the MySql-Database
import LoggingClass


class SqlApi(object):
    
    """
    This API enables an easy connection to the mysql driver and to the server with the database 
    
    VARIABLES:
        User            String - contains the Databaseuser
        Password        String - contains the Databaseuserpassword
        DatabaseName    String - contains the Databasename
    
    DATABASE STRUCTURE:
        Polltable
            I_Poll_Id    Integer (auto_increment)             - conntains the polltable id
            E_Poll_Id    Binary(16) or Varchar(36)            - UUID for external use
            Question     Varchar(999)                         - contains the question that has to be asked to the groupe
            MasterUser   Interger                             - Contains the internal user Id
            
        Options
            Id_Option    Integer                              - Contains the id of the qption
            Id-Polltable Interger                             - Contains the id of the question (from the polltable)
            Option_Name  Varchar(128)                         - Contains the option to be displayed
            
        Usertable
            I_User_ID    Interger                             - Contains the internal user id
            E_User_ID    Interger Usigned                     - Contains the external interger
        SettingsOfPoll
        
        UserSettingOfPoll
        
    """
    def __init__(self, User, Password, DatabaseName, LanguageObject,  Host = "127.0.0.1", Port = "3306"):

        self.User = User
        self.Password = Password
        self.LanguageObject = LanguageObject
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
                      'database': self.DatabaseName,
                      'port': 3306,
                      'raise_on_warnings': True,
                      'use_pure': True,
                      }
    
            return  mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print(self.LanguageObject.GetString("DatabaseAutentificationError"))
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(self.LanguageObject.GetString("NotExistingDatabase"))
            else:
                print(err)
    
    def CreateCursor(self):
        #this methode will ceate the cursor needet for the connection to the server
        return self.connection.cursor()
    
    def DestroyCursor(self, cursor):
        #this methode closes the connection opend by the cursor
        return cursor.close()
    
    def CreateDatabase(self,):
        pass
    
    def CreateTables(self, **TableData):
        pass
    
    