#!/usr/bin/python
# -*- coding: utf-8 -*-

import GlobalObjects

import mysql.connector  # A additional interface needed for the connection to the MySql-Database
import LoggingClass

import LanguageClass

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
            Id_Option            Integer (auto_increment)             - contains the id of the qption
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
    def __init__(self, User, Password, DatabaseName=None, Host="127.0.0.1", Port="3306"):

        self.User = User
        self.Password = Password
        self.Host = Host
        self.DatabaseName = DatabaseName
        self.Port = Port
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
                print(GlobalObjects.ObjectHolder["LanguageClass"].GetString("DatabaseAutentificationError"))
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                print(GlobalObjects.ObjectHolder["LanguageClass"].GetString("NotExistingDatabase"))
                raise SystemExit
            else:
                print(err)
    
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
            print(GlobalObjects.ObjectHolder["LanguageClass"].GetString('DatabaseQuerryError') + " {0}".format(err))
            
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
            print(GlobalObjects.ObjectHolder["LanguageClass"].GetString('DatabaseDeleteError') + "{0}".format(err))
            
    def CreateTables(self, Cursor, TableName, TableData, IfNotExists=True):
        """
        A methode to dynamicaly create a table entry to the database
        
        HOW TO USE:
            import collections 
            TableData = (
                ('Id', 'INT UNSIGNED NOT NULL AUTO_INCREMENT'),
                ('PRIMARY KEY', 'ID')
            )
            
            #function call
            SqlApl.CreateTables('Test', TableDataifNotExists = True)
        """
            
        try:
            Querry = "CREATE TABLE "
            if IfNotExists:
                Querry += "IF NOT EXISTS "
                
            Querry += TableName + " ("
                
            PrimaryKeyId = None
            for i in range(len(TableData)):
                if (TableData[i][0].lower() != 'primary key'):
                    Querry += TableData[i][0] + " " + TableData[i][1] + ", "
                else: 
                    PrimaryKeyId = i
                
            Querry += TableData[PrimaryKeyId][0] + " (" + TableData[PrimaryKeyId][1] + "))"
                
            Cursor.execute(Querry)
            return True
        
        except mysql.connector.Error as err:    
            print(GlobalObjects.ObjectHolder["LanguageClass"].GetString('DatabaseTableCreationError') + "{0}".format(err))
            return False
    
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
        
        
if __name__ == "__main__":
    print("online")
    import Main
    import pprint
    Main.ObjectInitialiser()
    a = SqlApi("root", "Password", "BetterPollBotDatabase") 
    Cursor = a.CreateCursor(Buffered=False, Dictionary=True, )
    # a.CreateDatabase(Cursor, "TestDatabase")
    f = a.SelectEntry(Cursor, "Membership_Roles", 
                  Columns=["Id", "Title" ], 
                  OrderBy= [ ["Title"]] ,
                  Amount=1,
                  Where=[["Id", "=", 1], "and", ["Title", "=", "SuperUser"]],
                  Distinct=False)
    
    print(f)
#     Query = """
#     SELECT 
#     Membership_Roles.Title,
#     Membership_Rights.NameOfRight 
#     FROM Membership_Options
#     LEFT JOIN Membership_Roles ON Membership_Roles.ID = Membership_Options.IdOfRoles
#     LEFT JOIN Membership_Rights ON Membership_Rights.ID = Membership_Options.IdOfMembers;
#     """
#     temp = a.ExecuteTrueQuery(Cursor, Query)
#     pp = pprint.PrettyPrinter(indent=4)
# 
#     pp.pprint(temp)
    
#     for i in temp:
#         t = ""
#         for key in i.keys():
#             t += ("%s, " % (i[key]))
#         print(t)
        
    #a.DeleteDatabase(Cursor, "Test")
    a.DestroyCursor(Cursor)
    print("offline")
    
    
