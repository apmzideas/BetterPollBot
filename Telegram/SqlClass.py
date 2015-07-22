#!/usr/bin/python
# -*- coding: utf-8 -*-

import mysql.connector #A additional interface needed for the connection to the MySql-Database



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
    def __init__(self, User, Password, DatabaseName,  Host ):

        self.User = User
        self.Password = Password
        self.Host = Host
        self.DatabaseName = DatabaseName
        self.connection = self.CreateConnection()
        
    def CreateConnection(self):

        config = {
                  'user': self.User,
                  'password': self.Password,
                  'host': self.Host,
                  'database': self.DatabaseName,
                  'raise_on_warnings': True,
                  }

        return  mysql.connector.connect(**config)