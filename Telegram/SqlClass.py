#!/usr/bin/python
# -*- coding: utf-8 -*-

import GlobalObjects

import mysql.connector  # A additional interface needed for the connection to the MySql-Database
import LoggingClass

# import the _() function!
import LanguageClass

class SqlApi(object):
    
    """
    This API enables an easy connection to the mysql driver and to the server with the database 
    
    VARIABLES:
        User                     String                               - contains the Databaseuser
        Password                 String                               - contains the Databaseuserpassword
        DatabaseName             String                               - contains the Databasename
    
    DATABASE STRUCTURE:
        PollTable
            Internal_Poll_Id      Integer (auto_increment)             - conntains the internal polltable id
            External_Poll_Id      Binary(16)                           - contains the MD5 for external use is the Id
            CreationDat           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            Question              Varchar(999)                         - contains the question that has to be asked to the groupe
            Master_User           Integer                              - contains the internal user Id
            
            UNIQUE (External_Poll_Id)
            PRIMARY KEY (Internal_Poll_Id)
            
        Options
            Id_Option            Integer (auto_increment)             - contains the id of the qption
            Id-PollTable         Integer                              - contains the id of the question (from the polltable)
            Option_Name          Varchar(128)                         - contains the option to be displayed
            
            PRIMARY KEY (Id_Option)
            
        Usertable
            Internal_User_ID      Integer (auto_increment)             - contains the internal user id
            External_User_ID      Integer Usigned                      - contains the external Integer
            User_Name             Varchar(256)                         - contains the user name if exists
            First_Name            Varchar(256)                         - contains the first name if exists
            Last_Name             Varchar(256)                         - contains the last name id exists
            
            PRIMARY KEY (Internal_User_ID)
            
        SettingsOfPoll
            Setting_Id           Integer (auto_increment)             - contains the internal settings id
            Setting_Name         Varchar(128)                         - contains the name of the setting
            Default_String       Varchar(256)                         - contains the default value for the setting if string
            Default_Integer      Integer                              - contains the default value for the setting if integer
            Default_Boolean      Boolean                              - contains the default value for the setting if boolean
            
            PRIMARY KEY (Setting_Id)
            
        UserSettingOfPoll
            User_Setting_Id
            Setting_Id          Integer (auto_increment)               - contains the settings id
            User_Id             Integer                                - contains the internal user id
            String              Varchar(256)                           - contanis the set string value for the setting
            Integer             Integer                                - contains the set integer value for the setting
            Boolean             Boolean                                - contains the set boolean value for the setting
            
            PRIMARY KEY (User_Setting_Id)
        
        UserAnswersToPoll
            Answer_Id         Integer (auto_increment)
            By_User            Integer
            Poll_Id            Integer
            Option_ID          Integer
            
            PRIMARY KEY (Answer_Id)
            
            
    """
    def __init__(self,
                  User, 
                  Password, 
                  DatabaseName=None, 
                  Host="127.0.0.1", 
                  Port="3306", 
                  **OptionalObjects):

        self.User = User
        self.Password = Password
        self.Host = Host
        self.DatabaseName = DatabaseName
        self.Port = Port
        
        #Predefining attribute so that it later can be used for evil.
        self.LanguageObject = None
        self.LogggingObject = None
        
        if "LanguageObject" in OptionalObjects:
            self.LanguageObject = OptionalObjects["LanguageObject"]
        else:
            self.LanguageObject = LanguageClass.CreateTranslationObject()
        if "LoggingObject" in OptionalObjects:
            self.LogggingObject = OptionalObjects["LoggingObject"]
        else:
            self.LogggingObject = LoggingClass.Logger()
            
        #This is the language objects only value
        self._ = self.LanguageObject.gettext
        
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
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                self.LogggingObject.create_log(self._("The database connector returned following error: {Error}").format(Error = err) + " " + self._("Something is wrong with your user name or password."), "Error")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.LoggignObject.create_log( self._("The database connector returned following error: {Error}").format(Error = err) +" " + self._("The database does not exist, please contact your administrator."), "Error")
                raise SystemExit
            else:
                self.LoggignObject.create_log(err)
    
    def CreateCursor(self, Buffered=False, Dictionary=True):
        # this methode will ceate the cursor needet for the connection to the server
        return self.connection.cursor( buffered=Buffered, dictionary=Dictionary)
    
    def DestroyCursor(self, Cursor):
        # this methode closes the connection opend by the cursor
        return Cursor.close()
    
    def ExecuteTrueQuery(self, Cursor, Query, Data=None):
        """
        A methode to execute the query statements.
        
        cursor = cnx.cursor(prepared=True)
        stmt = "SELECT fullname FROM employees WHERE id = %s" # (1)
        cursor.execute(stmt, (5,))                            # (2)
        # ... fetch data ...
        cursor.execute(stmt, (10,))                           # (3)
        # ... fetch data ...
        
        Query = "SELECT fullname FROM employees WHERE id = %s or id = %s"
        Data = (10, 15)
        """
        try:
            if Data:
                Cursor.execute(Query, Data)
            else:
                Cursor.execute(Query)

            Temp = []
            for i in Cursor:
                Temp.append(i)
            return Temp
        
        except mysql.connector.Error as err:
            self.LoggingObject.create_log(_("The database returned following error: {Error}").format(Error=err) +" "+ _("The executet querry failed, please contact your administrator."))
            
    def CreateDatabase(self, Cursor, DatabaseName):
        try:
            Cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {0} DEFAULT CHARACTER SET 'utf8'".format(DatabaseName))
        except mysql.connector.Error as err:
            self.LogggingObject.create_log( self._("The database connector returned following error: {Error}").format(Error = err) + " " + self._("The creation of the following database {DatabaseName} has not succeded, please contact your administrator.").format(DatabaseName=DatabaseName) )
    
    def DeleteDatabase(self, Cursor, DatabaseName):
        try:
            Cursor.execute(
            "DROP DATABASE {0};".format(DatabaseName))
        except mysql.connector.Error as err:
            self.LogggingObject.create_log(_("The database returned following error: {Error}").format(Error=err) +" " + _("Failed to delete the \"{DatabaseName}\" database, please delete manually.").format(DatabaseName = DatabaseName))
            
    def CreateTable(self, Cursor, TableName, TableData, IfNotExists=True):
        """
        A methode to dynamicaly create a table entry to the database
        
        HOW TO USE:
 
            TableData = (
                ('Id', 'INT UNSIGNED NOT NULL AUTO_INCREMENT'),
                ('Unique', 'ID'),
                ('PRIMARY KEY', 'ID'),
                ('Foreigh Key', 'ID', 'Persons(P_Id)')
            )
            
            #function call
            SqlApl.CreateTable('Test', TableDataIfNotExists = True)
        """
            
        try:
            Query = "CREATE TABLE "
            if IfNotExists:
                Query += "IF NOT EXISTS "
                
            Query += TableName + " ("
                
            PrimaryKeyId = None
            UniqueKeyId = None
            ForeignKeyId = None
            
            for i in range(len(TableData)):
                if (TableData[i][0].lower() != 'primary key' and TableData[i][0].lower() != 'unique' and TableData[i][0].lower() != 'foreign key' ):
                    if i == 0:
                        Query += TableData[i][0] + " " + TableData[i][1]
                    else:
                        Query += ", " +TableData[i][0] + " " + TableData[i][1]
                
                else:
                    if (TableData[i][0].lower() == 'primary key'):
                        PrimaryKeyId = i
                    elif TableData[i][0].lower() == 'unique':
                        UniqueKeyId = i
                    elif TableData[i][0].lower() == 'foreign key':
                        ForeignKeyId = i
            
            #If a unique key has been added.
            if UniqueKeyId:
                if Query[-1] != ",":
                    Query += ","
                Query += " " + TableData[UniqueKeyId][0] + " (" + TableData[UniqueKeyId][1] + ")"
            
            #If a PrimatyKey has been added.
            if PrimaryKeyId:
                if Query[-1] != ",":
                    Query += ","
                Query += " " + TableData[PrimaryKeyId][0] + " (" + TableData[PrimaryKeyId][1] + ")"
           
            #If a Foreign Key has been added.
            if ForeignKeyId:
                if Query[-1] != ",":
                    Query += ","
                Query += " " + TableData[ForeignKeyId][0] + " (" + TableData[ForeignKeyId][1] + ") REFERENCES " + TableData[ForeignKeyId][2]              
            
            Query += ");"
            
            Cursor.execute(Query)
            return True
        
        except mysql.connector.Error as err:    
            self.LogggingObject.create_log( self._("The database connector returned following error: {Error}").format(Error = err) + " " + self._("The following database table \"{TableName}\" could not be created, please contact your administrator."), "error")
            return False
    
    def CreateMainDatabase(self, Cursor):
        #This methode will create all the default tables and data for the database
        
        #First all the tables 
        #UserTable
        TableData = (
                     ("Internal_User_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("External_User_Id", "Integer Unsigned"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("User_Name", "Varchar(256) DEFAULT NULL"),
                     ("First_Name", "Varchar(256) DEFAULT NULL"),
                     ("Last_Name", "Varchar(256) DEFAULT NULL"),
                     ("PRIMARY KEY", "Internal_User_ID")
                     )
        
        self.CreateTable(Cursor, "User_Table", TableData,) 
                 
        #The PollTable
        TableData = (
                     ("Internal_Poll_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("External_Poll_Id", "BINARY(16) DEFAULT NULL"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("Question", "Varchar(999)"),
                     ("Master_User_Id", "Integer"),
                     ("UNIQUE", "External_Poll_Id"),
                     ("PRIMARY KEY", "Internal_Poll_Id"),
                     ("FOREIGN KEY", "Master_User_Id", "User_Table(Internal_User_Id)")
                    )
         
        self.CreateTable(Cursor, "Poll_Table", TableData,)
         
        #Options for the Poll themself
        TableData = (
                     ("Id_Option", "Integer NOT NULL AUTO_INCREMENT"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("Id_Poll_Table", "Integer"),
                     ("Option_Name", "Varchar(128)"),
                     ("PRIMARY KEY", "Id_Option"),
                     ("FOREIGN KEY", "Id_Poll_Table", "Poll_Table(Internal_Poll_Id)")
                    )
         
        self.CreateTable(Cursor, "Options_Table", TableData,)
         
        #all settings of the poll
        TableData = (
                     ("Setting_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("Setting_Name", "Varchar(128)"),
                     ("Default_String", "Varchar(256)"),
                     ("Default_Boolean", "Boolean"),
                     ("PRIMARY KEY", "Setting_Id")               
                     )
         
        self.CreateTable(Cursor, "Settings_Of_Poll", TableData,)
         
        # User set settings for the poll, like custom language
         
        TableData = (
                     ("User_Setting_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("Id_Poll_Table", "Integer"),
                     ("User_Id", "Integer"),
                     ("User_String", "VARCHAR(256)"),
                     ("User_Integer", "Integer"),
                     ("User_Boolean", "Boolean"),
                     ("Primary key", "User_Setting_Id"),
                     ("FOREIGN KEY", "Id_Poll_Table", "PollTable(Internal_Poll_Id)"),
                     ("FOREIGN KEY", "User_Id", "User_Table(Internal_User_Id)")
                     )
        self.CreateTable(Cursor, "User_Setting_Of_Poll", TableData,)
        
        TableData = (
                     ("Answer_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("By_User", "Integer"),
                     ("Poll_Id", "Integer"),
                     ("Option_Id", "Integer"),
                     ("PRIMARY KEY", "Answer_Id"),
                     ("FOREIGN KEY", "User_Id", "User_Table(Internal_User_Id)"),
                     ("FOREIGN KEY", "Poll_Id", "PollTable(Internal_Poll_Id)"),
                     ("FOREIGN KEY", "Option_Id", "Options_Table(Id_Option)")
                     )
        self.CreateTable(Cursor, "User_Answers_To_Poll", TableData,)
        
        #Second all the inserts
        
        #The Settings
        
        Columns = {
                   
                   }
        
        self.InsertEntry(Cursor, "Settings_Of_Poll", Columns)
            
        return True
         
    def SelectEntry(self, Cursor, FromTable, Columns, OrderBy = [None] , Amount = None, Where = [], Data = (), Distinct = False, ):
        # a simple SQL SELECT builder, this will be replaces by the Querry Class generator
        # 
        # OrderBy example [[column_name, "ASC"],[column_name, ],[column_name, "DESC"]] if emtpy ASC - has to be list
        # Where example [{'column_name': ''}, operator, value], operator, [column_name, operator, value]]
        
        Query = ["SELECT"]
        
        if Distinct:
            Query.append("DISTINCT")
        
        #columns
        for i in range(len(Columns)):
            if i+1 < len(Columns):
                Query.append(Columns[i] + ",")
            else:
                Query.append(Columns[i])
        
        #from Table
        Query.append("FROM " + FromTable)
        
        #Where
        if Where != []:
            Query.append("WHERE")
            for i in range(len(Where)):
                if type(Where[i]) == type([]):
                    Query.append( Where[i][0] )
                    Query.append( Where[i][1] )
                    Query.append("'{0}'".format( Where[i][2]) )
                elif type(Where[i]) == type(""):
                    Query.append(Where[i])   
                
#                 if i+1 != len(Where):
#                     Query.append(",")
                
                print(Where[i])
                
                #Query.append(Where[i])
                             
        #Order By
        if OrderBy[0] is not None:
            Query.append("ORDER BY")
            
            for i in range(len(OrderBy)):
                for x in range(len(OrderBy[i])):
                    if not OrderBy[i] in ("and", "or"): 
                        Query.append(OrderBy[i][x])
                    else:
                        Query.append(OrderBy[i])
                
                if i+1 < len(OrderBy):
                    Query.append(",")
        
        
        
        #Limit
        if (Amount is not None) and (isinstance( Amount, int )):
            Query.append("LIMIT " + str(Amount))
        
        Query.append(";")
        
        Query = ' '.join([str(i) for i in Query])
        
        print(Query)
        
        if Data == ():
            return (self.ExecuteTrueQuery(Cursor, Query, ))
        else:
            return (self.ExecuteTrueQuery(Cursor, Query, Data))

    def UpdateEntry(self, Cursor, TableName, SetColumnTo=(), Data = (), Where=[]):
        #
        #
        # SetColumnTo = (('id',), ('Name', 'Max')) # if alone ?
        
        Query = ["UPDATE"]
        
        Query.append(TableName)
        
        Query.append("SET")
        
        for i in range(len(SetColumnTo)):
            Query.append(SetColumnTo[i][0])
            Query.append("=")
            if len(SetColumnTo) == 1:
                Query.append(SetColumnTo[1])
            else:
                Query.append("?") 
        
    def InsertEntry(self, Cursor, TableName, Columns={}):
        #This method will insert any type of entry into the system
        
        try:   
            Query = "INSERT INTO "
             
            Query += TableName + " ("
             
            Query += ', '.join( Columns.keys())     
            Query += ") VALUES (" 
            Query += ", ".join(["%("+str(i) + ")s" for i in  Columns.keys() ])
            
            Query += ");"
            
            Cursor.execute(Query, Columns)
            
            # Make sure data is committed to the database
            self.connection.commit()
            return True
        except mysql.connector.Error as err:    
            self.LogggingObject.create_log(self._("The database connector returned following error: {Error}").format(Error = err) + " " + self._("The exetuted insertion query failed, please contact your administrator") ,"error")
            return False
        
if __name__ == "__main__":
    print("online")
    import Main
    #import pprint
    Main.ObjectInitialiser()
    Cursor = GlobalObjects.ObjectHolder["SqlClass"].CreateCursor(Buffered=False, Dictionary=True,)
   
    GlobalObjects.ObjectHolder["SqlClass"].CreateMainDatabase(Cursor)
    
    
    GlobalObjects.ObjectHolder["SqlClass"].InsertEntry(Cursor, "user_table", {
                                                                              "External_User_Id" : 32301786,
                                                                              "First_Name" : "Adrian",
                                                                              "Last_Name" : "Hornung",
                                                                              "User_Name" : "TheRedFireFox"
                                                                            }
                                                       )
    GlobalObjects.ObjectHolder["SqlClass"].DestroyCursor(Cursor)
    print("offline")
    
    
