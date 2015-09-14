#!/usr/bin/python
# -*- coding: utf-8 -*-
import GlobalObjects

import sql.mysql.connector  # A additional interface needed for the DatabaseConnection to the MySql-Database
import LoggingClass

# import the _() function!
import language.LanguageClass


class SqlApi(object):
    
    """
    This API enables an easy DatabaseConnection to the mysql driver and to the server with the database 
    
    VARIABLES:
        User                     String                               - contains the Databaseuser
        Password                 String                               - contains the Databaseuserpassword
        DatabaseName             String                               - contains the Databasename
    
    DATABASE STRUCTURE:
        PollTable
            Internal_Poll_Id      Integer (auto_increment)             - conntains the internal polltable id
            External_Poll_Id      Binary(16)                           - contains the MD5 for external use is the Id
            CreationDat           TIMESTAMP CURRENT_TIMESTAMP
            PollName              Varchar(255)                         - contains the pollname like poll 1
            Question              Varchar(999)                         - contains the question that has to be asked to the groupe
            Master_User           Integer                              - contains the internal user Id
            
            UNIQUE (External_Poll_Id)
            PRIMARY KEY (Internal_Poll_Id)
            
        Options
            Id_Option            Integer (auto_increment)             - contains the id of the qption
            Id-PollTable         Integer                              - contains the id of the question (from the polltable)
            Option_Name          Varchar(128)                         - contains the option to be displayed
            
            PRIMARY KEY (Id_Option)
            
        UserTable
            Internal_User_ID      Integer (auto_increment)             - contains the internal user id
            External_User_ID      Integer                              - contains the external Integer
            User_Name             Varchar(max)                         - contains the user name if exists
            First_Name            Varchar(max)                         - contains the first name if exists
            Last_Name             Varchar(max)                         - contains the last name id exists
            PRIMARY KEY (Internal_User_ID)
            
        GroupTable
            Internal_Id          Integer (auto_increment)             - contains the internal group id
            External_Id          Integer                              - contains the external group id
            Group                Varchar(255)                         - contains the group name
            UNIQUE (External_Poll_Id)            
            PRIMARY KEY (Internal_Id)
            
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
            Answer_Id           Integer (auto_increment)
            By_User             Integer
            By_Group            Integer 
            Poll_Id             Integer
            Option_ID           Integer
            
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
        self.LoggingObject = None
        
        if "LanguageObject" in OptionalObjects:
            self.LanguageObject = OptionalObjects["LanguageObject"]
        else:
            self.LanguageObject = language.LanguageClass.CreateTranslationObject()
            
        # This is the language objects only value. 
        # It enables the translation of the texts. 
        self._ = self.LanguageObject.gettext
        
        if "LoggingObject" in OptionalObjects:
            self.LoggingObject = OptionalObjects["LoggingObject"]
        else:
            self.LoggingObject = LoggingClass.Logger()
            
        # Create the connection to the database. 
        self.DatabaseConnection = self.CreateConnection()
        
    def CreateConnection(self):
        # This methode will create the connetion object for the mysql database. 
        # If if failes it will raise a 
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
    
            return  sql.mysql.connector.connect(**config)
        except sql.mysql.connector.Error as err:
            if err.errno == sql.mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                self.LoggingObject.warning(self._("The database connector returned following error: {Error}").format(Error = err) + " " + self._("Something is wrong with your user name or password."),)
                raise SystemError
            elif err.errno == sql.mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.LoggingObject.error( self._("The database connector returned following error: {Error}").format(Error = err) +" " + self._("The database does not exist, please contact your administrator."))
                raise SystemExit
            else:
                self.LoggingObject.error(err, "Error")
                raise SystemExit
        except:
            self.LoggingObject.critical( self._("The database connector returned following error: {Error}").format(Error = "[WinError 10061] No connection could be made because the target machine actively refused it") + " " + self._("The database server seems to be offline, please contact your administrator.")) 
    
    def CreateCursor(self, Buffered=False, Dictionary=True):
        # this methode will ceate the cursor needet for the DatabaseConnection to the server
        return self.DatabaseConnection.cursor( buffered=Buffered, dictionary=Dictionary)
    
    def GetLastRowId(self, Cursor):
        return Cursor.lastrowid
    
    def DestroyCursor(self, Cursor):
        # this methode closes the DatabaseConnection opend by the cursor
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

            if Data != None:
                if not isinstance(Data, dict):
                    if not isinstance(Data, list):
                        if isinstance(Data, int):
                            Data = (Data,)
                        elif isinstance(Data, str):
                            Data = (Data,)
                        Data = list(Data)
                    Cursor.execute(Query, [str(i) for i in Data])
                else:
                    Cursor.execute(Query, Data)
            else:
                Cursor.execute(Query)

            Temp = []
            for i in Cursor:
                Temp.append(i)
            return Temp
        
        except sql.mysql.connector.Error as err:
            self.LoggingObject.error(self._("The database returned following error: {Error}").format(Error=err) +" "+ self._("The executet query failed, please contact your administrator."))
            if isinstance(Data, list):
                Data = ', '.join(Data)
            elif isinstance(Data, dict):
                Data = ', '.join("{Key}={Value}".format(Key = Key, Value = Value) for (Key, Value) in Data.items())
            self.LoggingObject.error(self._("The failed query is:\n{Query}\n{Data}").format(Query = Query,
                                                                                            Data = Data))
            
    def CreateDatabase(self, Cursor, DatabaseName):
        try:
            Cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {0} DEFAULT CHARACTER SET 'utf8'".format(DatabaseName))
        except sql.mysql.connector.Error as err:
            self.LoggingObject.error( self._("The database connector returned following error: {Error}").format(Error = err) + " " + self._("The creation of the following database {DatabaseName} has not succeded, please contact your administrator.").format(DatabaseName=DatabaseName) )
    
    def DeleteDatabase(self, Cursor, DatabaseName):
        try:
            Cursor.execute(
            "DROP DATABASE {0};".format(DatabaseName))
        except sql.mysql.connector.Error as err:
            self.LoggingObject.error(_("The database returned following error: {Error}").format(Error=err) + " " + _("Failed to delete the \"{DatabaseName}\" database, please delete manually.").format(DatabaseName = DatabaseName))
            
    def CreateTable(self, Cursor, TableName, TableData, IfNotExists=True, Engine="InnoDB"):
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
            
            Query += ")" 
            if Engine != None:
                Query += "ENGINE="+Engine
            
            Query += ";"
            Cursor.execute(Query)
            return True
        
        except sql.mysql.connector.Error as err:    
            self.LoggingObject.error( self._("The database connector returned following error: {Error}").format(Error = err) + " " + self._("The following database table \"{TableName}\" could not be created, please contact your administrator.").format(TableName=TableName),)
            self.DatabaseConnection.rollback()
            return False
    
    def CreateMainDatabase(self, Cursor):
        #This methode will create all the default tables and data for the database
        
        #First all the tables 
        #UserTable
        TableData = (
                     ("Internal_User_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("External_User_Id", "Integer"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("User_Name", "TEXT DEFAULT NULL"),
                     ("First_Name", "TEXT DEFAULT NULL"),
                     ("Last_Name", "TEXT DEFAULT NULL"),
                     ("PRIMARY KEY", "Internal_User_ID")
                     )
        
        self.CreateTable(Cursor, "User_Table", TableData,) 
            
        #SessionHandling saves the last send command 
        TableData = (
                     ("Session_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("Command_By_User", "Integer"), #is the internal id of the user
                     ("Command", "Varchar(256)"),
                     ("Last_Used_Id", "Integer DEFAULT NULL"),
                     ("PRIMARY KEY", "Session_Id"),
                     ("UNIQUE", "Command_By_User"),
                     )
        
        self.CreateTable(Cursor, "Session_Table", TableData,)         
        
        #Settings 
        TableData = (
                     ("Setting_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("Setting_Name", "Varchar(128)"),
                     ("Default_String", "Varchar(256)"),
                     ("Default_Integer", "Integer"),
                     ("Default_Boolean", "Boolean"),
                     ("PRIMARY KEY", "Setting_Id")  
                     )
        
        self.CreateTable(Cursor, "Setting_Table", TableData,)
                
        #UserSetSetting
        TableData = (
                     ("Setting_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("Master_Setting_Id", "Integer"), #This settings master entry in 
                     ("Master_User_Id", "Integer"), #This setting has been set by
                     ("User_Integer", "Integer"),
                     ("User_String", "Varchar(256)"),
                     ("User_Boolean", "Boolean"),
                     ("PRIMARY KEY", "Setting_Id"),
                     ("FOREIGN KEY", "Master_Setting_Id", "Setting_Table(Setting_Id)"),
                     ("FOREIGN KEY", "Master_User_Id", "User_Table(Internal_User_Id)"),
                     )
        
        self.CreateTable(Cursor, "User_Setting_Table", TableData,)
        
        #GroupTable
        TableData = (
                     ("Internal_Group_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("External_Group_Id", "Integer"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("Group_Name", "Varchar(255)"),
                     ("UNIQUE", "External_Group_Id"),
                     ("PRIMARY KEY", "Internal_Group_Id")
                     )
        
        self.CreateTable(Cursor, "Group_Table", TableData,)
                          
        #The PollTable
        TableData = (
                     ("Internal_Poll_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("External_Poll_Id", "BINARY(32) DEFAULT NULL"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("Poll_Name", "Varchar(255) DEFAULT NULL"),
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
                     ("Master_User_Id", "Integer"),
                     ("PRIMARY KEY", "Id_Option"),
                     ("FOREIGN KEY", "Id_Poll_Table", "Poll_Table(Internal_Poll_Id)"),
                     ("FOREIGN KEY", "Master_User_Id", "User_Table(Internal_User_Id)")
                    )
         
        self.CreateTable(Cursor, "Options_Table", TableData,)
         
        #all settings of the poll
        TableData = (
                     ("Setting_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("Setting_Name", "Varchar(128)"),
                     ("Default_Integer", "Integer"),
                     ("Default_String", "Varchar(256)"),
                     ("Default_Boolean", "Boolean"),
                     ("PRIMARY KEY", "Setting_Id")               
                     )
         
        self.CreateTable(Cursor, "Settings_Of_Poll_Table", TableData,)
         
        # User set settings for the poll, like custom language
         
        TableData = (
                     ("User_Setting_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("Setting_Id", "Integer"), 
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("Id_Poll_Table", "Integer"),
                     ("User_Id", "Integer"),
                     ("User_String", "VARCHAR(256)"),
                     ("User_Integer", "Integer"),
                     ("User_Boolean", "Boolean"),
                     ("Primary key", "User_Setting_Id"),
                     ("FOREIGN KEY", "Id_Poll_Table", "Poll_Table(Internal_Poll_Id)"),
                     ("FOREIGN KEY", "User_Id", "User_Table(Internal_User_Id)"),
                     ("FOREIGN KEY", "Setting_Id", "Settings_Of_Poll_Table(Setting_Id)")
                     )
        
        self.CreateTable(Cursor, "User_Setting_Of_Poll_Table", TableData,)
        
        # User anwser to the poll
        TableData = (
                     ("Answer_Id", "Integer NOT NULL AUTO_INCREMENT"),
                     ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                     ("By_User", "Integer"),
                     ("By_Group", "Integer"),
                     ("Poll_Id", "Integer"),
                     ("Option_Id", "Integer"),
                     ("PRIMARY KEY", "Answer_Id"),
                     ("FOREIGN KEY", "By_User", "User_Table(Internal_User_Id)"),
                     ("FOREIGN KEY", "By_Group", "Group_Table(Internal_Group_Id)"),
                     ("FOREIGN KEY", "Poll_Id", "Poll_Table(Internal_Poll_Id)"),
                     ("FOREIGN KEY", "Option_Id", "Options_Table(Id_Option)")
                     )
        
        self.CreateTable(Cursor, "User_Answers_To_Poll_Table", TableData,)
        
        # Second all the inserts
        # The Settings for the default polls
        
        Columns = {
                   "Setting_Name": "Language",
                   "Default_String": "en_US"
                   }
        
        self.InsertEntry(Cursor, "Settings_Of_Poll_Table", Columns)
        
        # the inserts for the settings 
        Columns = {
                   "Setting_Name": "Language",
                   "Default_String": "en_US"
                   }
        self.InsertEntry(Cursor, "Setting_Table", Columns)
        
        # commit all the changes
        self.Commit(Cursor)
        
        return True
         
    def SelectEntry(self, Cursor, FromTable, Columns, OrderBy = [None] , Amount = None, Where = [], Data = (), Distinct = False, ):
        # a simple SQL SELECT builder, this will be replaces by the query Class generator
        # 
        # OrderBy example [[column_name, "ASC"],[column_name, ],[column_name, "DESC"]] if emtpy ASC - has to be list
        # Where example [['column_name', operator, value], operator, [column_name, operator, "%s"]]
        
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
                    Query.append("{0}".format( Where[i][2]) )
                elif type(Where[i]) == type(""):
                    Query.append(Where[i])   
                
#                 if i+1 != len(Where):
#                     Query.append(",")
                
                #print(Where[i])
                
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
        
        #print(Query)
        
        if Data == ():
            return (self.ExecuteTrueQuery(Cursor, Query, ))
        else:
            return (self.ExecuteTrueQuery(Cursor, Query, Data))

    def UpdateEntry(self, Cursor, TableName, Columns, Where=[], Autocommit = False):
        # This Methode will update a record in the database
        # This methode will return something like this:
        # UPDATE table_name
        # SET column1=value1,column2=value2,...
        # WHERE some_column=some_value;
        # If autocommit is true the methode will automatically commit to the database.
        # Columns = { 'id' : id,
        #            'Name': 'Max'}
        # Where = [["Id", "=", 2], "AND", "(", ["as", "65"], "OR",  ")",]

    
        Query = "UPDATE "
            
        Query += TableName
            
        Query += " SET "
    
        # Create the key value pair 
        temp = []
        for Key in Columns.keys():
            temp.append("{Key}=%({Key})s".format(Key = str(Key)))
        
        Query += ', '.join(temp)
    
        if Where != []:
            
            Query += " WHERE "
            
            for i in range(len(Where)):
                if type(Where[i]) == type([]):
                    Where[i] = [str(i) for i in Where[i]]
                    Query += str(Where[i][0])
                    if Where[i][1].upper() in ("=", "<", ">", "<>", "!=", ">=", "<=", "BETWEEN", "LIKE", "IN"):
                        Query += Where[i][1]
                        Query += "%({Where})s".format( Where = Where[i][0] + "Where") 
                        Columns[Where[i][0] + "Where"] = Where[i][2]
                    else:
                        Query += "=%({Where})s".format(Where = Where[i][0]+"Where")
                        Columns[Where[i][0] + "Where"] = Where[i][1]
                    
                elif type(Where[i]) == type(""):
                    if Where[i].upper() in ("(", ")", "AND", "OR"):
                        Query += " {} ".format(Where[i])
                    else:
                        raise ValueError( self._("The where type in your query is not in the list of valid types. {Error}").format(Error = Where[i]))
        Query += ";"
#         print(Query)
#         print(Columns)
#         print(Query % Columns)
        
        self.ExecuteTrueQuery(Cursor, Query, Columns)
        if Autocommit == True:
            # Autocommit the update to the server
            self.Commit(Cursor)
        return True
        
    def InsertEntry(self, Cursor, TableName, Columns={}, Duplicate = None, AutoCommit = False):
        #This method will insert any type of entry into the system
        Query = "INSERT INTO "
             
        Query += TableName + " ("
             
        Query += ', '.join( Columns.keys())     
        Query += ") VALUES (" 
        Query += ", ".join(["%("+str(i) + ")s" for i in  Columns.keys() ])
            
        Query += ")"
        
        if Duplicate != None:
            Query +=  " ON DUPLICATE KEY UPDATE "
            Duplicates = []
            for Key in Duplicate.keys():
                Duplicates.append("{Key} = %({Value})s".format(Key = str(Key),
                                                   Value = str(Key)
                                                   )
                                  )
                
            Query += ', '.join(Duplicates)
        Query += ";"
        
        #print(Query)
        
        Cursor.execute(Query, Columns)
            
        if AutoCommit:
             # Make sure data is committed to the database
            self.Commit(Cursor)
        return True

    def Commit(self, Cursor):
        try:
            self.DatabaseConnection.commit()
        except mysql.DatabaseConnection.Error as Error:
            self.LoggingObject.error( self._("The database connector returned following error: {Error}").format(Error = err))
            self.DatabaseConnection.rollback()
            
if __name__ == "__main__":
    print("online")
    import Main
    #import pprint
    Main.ObjectInitialiser()
    Cursor = GlobalObjects.ObjectHolder["SqlClass"].CreateCursor(Buffered=False, Dictionary=True,)
    print(GlobalObjects.ObjectHolder["SqlClass"].SelectEntry(
                                                       Cursor, 
                                                       FromTable="User_Table", 
                                                       Columns = ("External_User_Id",
                                                                  "Creation_Date",
                                                                  "User_Name",
                                                                  "First_Name",
                                                                  "Last_Name"),
                                                       Where = ["Internal_User_Id", "=", "%s"],
                                                       Data = (4,),
                                                       Distinct = False,))
#     GlobalObjects.ObjectHolder["SqlClass"].CreateMainDatabase(Cursor)
#     
#     
# 
#     GlobalObjects.ObjectHolder["SqlClass"].InsertEntry(Cursor, "user_table", {
#                                                                               "External_User_Id" : 32301786,
#                                                                               "First_Name" : "Adrian",
#                                                                               "Last_Name" : "Hornung",
#                                                                               "User_Name" : "TheRedFireFox"
#                                                                             }
#                                                        )
#     GlobalObjects.ObjectHolder["SqlClass"].InsertEntry(Cursor, "user_table", {
#                                                                               "External_User_Id" : 105654068,
#                                                                               "First_Name" : "Robin",
#                                                                               "Last_Name" : "",
#                                                                               "User_Name" : ""
#                                                                             }
#                                                        )
#     GlobalObjects.ObjectHolder["SqlClass"].InsertEntry(Cursor, "user_table", {
#                                                                               "External_User_Id" : 10620786,
#                                                                               "First_Name" : "Jonas",
#                                                                               "Last_Name" : "Löw",
#                                                                               "User_Name" : "kiritjom"
#                                                                             }
#                                                        )
    GlobalObjects.ObjectHolder["SqlClass"].DestroyCursor(Cursor)
    print("offline")
    
    