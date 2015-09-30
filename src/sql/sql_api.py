#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
A additional MySql-interface needed for the DatabaseConnection.

It's a third party software developed by `oracle <http://www.oracle.com>`_.

some useful links:\n
    - download:\n
        http://dev.mysql.com/downloads/connector/python/
    - documentation:\n
        http://dev.mysql.com/doc/connector-python/en/index.html
"""
# standard library
import sys
# third party requirements
import mysql.connector
# The custom modules
import gobjects
import custom_logging
import language.language  # import the _() function!


class Api(object):
    """
    This class is user a mysql interface.
    
    It is a interface between the mysql connector that talks with 
    the database and the python code. As well dynamically creates
    the queries that have to be executed.
    
    DATABASE STRUCTURE:

        +------------------------------------------------------------+
        |Poll_Table                                                  |  
        +==================+===================+=====================+
        |Internal_Poll_Id  |conntains          |Integer              |
        |                  |the internal       |(auto_increment)     |
        |                  |polltable id       |                     |   
        +------------------+-------------------+---------------------+    
        |External_Poll_Id  |contains the MD5   |Binary(16)           |
        |                  |for external       |                     |
        |                  |use is the Id      |                     |   
        +------------------+-------------------+---------------------+    
        |CreationDate      |contains the       |TIMESTAMP            |
        |                  |creation date of   |CURRENT_TIMESTAMP    |
        |                  |of the poll        |                     |
        +------------------+-------------------+---------------------+    
        |Poll_Name         |contains           |Varchar(255)         |   
        |                  |the pollname like  |                     |
        |                  |poll 1             |                     |
        +------------------+-------------------+---------------------+        
        |Question          |contains the       |Varchar(999)         |   
        |                  |question that to   |                     |
        |                  |has to be asked    |                     |
        |                  |the group          |                     |  
        +------------------+-------------------+---------------------+        
        |Master_User       |contains           |Integer              |    
        |                  |the internal user  |                     |
        |                  |Id                 |                     |
        +------------------+-------------------+---------------------+ 
        |    UNIQUE (External_Poll_Id)                               |     
        +------------------------------------------------------------+    
        |    PRIMARY KEY (Internal_Poll_Id)                          |  
        +------------------------------------------------------------+
        
        +------------------------------------------------------------+
        |Options_Table                                               | 
        +==================+===================+=====================+
        |Id_Option         |contains the id of |Integer              |
        |                  |the question       |(auto_increment)     |    
        +------------------+-------------------+---------------------+        
        |Id-PollTable      |contains the id of |Integer              |
        |                  |the question       |                     |
        |                  |(from the          |                     |
        |                  |poll table)        |                     |
        +------------------+-------------------+---------------------+       
        |Option_Name       |contains the option|Varchar(128)         |                          
        |                  |to be displayed    |                     |
        +------------------+-------------------+---------------------+    
        |    PRIMARY KEY (Id_Option)                                 |
        +------------------------------------------------------------+
            
        +------------------------------------------------------------+    
        |User_Table                                                  |
        +==================+===================+=====================+  
        |Internal_User_ID  |contains the       |Integer              |  
        |                  |internal user id   |(auto_increment)     |              
        +------------------+-------------------+---------------------+        
        |External_User_ID  |contains the       |Integer              |                              
        |                  |external id        |                     | 
        +------------------+-------------------+---------------------+        
        |User_Name         |contains the user  |TEXT                 |          
        |                  |name if it exists  |                     |
        +------------------+-------------------+---------------------+      
        |First_Name        |contains the first |TEXT                 |         
        |                  |name if it exists  |                     |
        +------------------+-------------------+---------------------+
        |Last_Name         |contains the last  |TEXT                 |                       
        |                  |name id exists     |                     |
        +------------------+-------------------+---------------------+
        |PRIMARY KEY (Internal_User_ID)                              |
        +------------------------------------------------------------+
        
        +------------------------------------------------------------+    
        |Group_Table                                                 |
        +==================+===================+=====================+
        |Internal_Id       |contains the       |Integer              |
        |                  |internal group id  |(auto_increment)     |
        +------------------+-------------------+---------------------+        
        |External_Id       |contains the       |Integer              |                              
        |                  |external group id  |                     | 
        +------------------+-------------------+---------------------+        
        |Group             |contains the group |Varchar(255)         |                          
        |                  |name               |                     |
        +------------------+-------------------+---------------------+         
        |    UNIQUE (External_Poll_Id)                               | 
        +------------------------------------------------------------+             
        |    PRIMARY KEY (Internal_Id)                               |
        +------------------------------------------------------------+
        
        +------------------------------------------------------------+    
        |Settings_Of_Poll_Table                                      |  
        +==================+===================+=====================+
        |Setting_Id        |contains the       |Integer              | 
        |                  |internal settings  |(auto_increment)     | 
        |                  |id                 |                     |
        +------------------+-------------------+---------------------+
        |Setting_Name      |contains the name  |Varchar(128)         |   
        |                  |of the setting     |                     |
        +------------------+-------------------+---------------------+
        |Default_String    |contains the       |Varchar(256)         |                         
        |                  |default value for  |                     |
        |                  |the setting if     |                     |
        |                  |string             |                     |
        +------------------+-------------------+---------------------+    
        |Default_Integer   |contains the       |Integer              |                          
        |                  |default value for  |                     |
        |                  |the setting if     |                     |
        |                  |integer            |                     |
        +------------------+-------------------+---------------------+
        |Default_Boolean   |contains the       |Boolean              |                 
        |                  |default value for  |                     |
        |                  |the setting if     |                     |
        |                  |boolean            |                     |
        +------------------+-------------------+---------------------+    
        |PRIMARY KEY (Setting_Id)                                    |
        +------------------------------------------------------------+
        
        +------------------------------------------------------------+    
        |User_Setting_Of_Poll_Table                                  |
        +==================+===================+=====================+ 
        |Setting_Id        |contains the       |Integer              |               
        |                  |settings id        |(auto_increment)     |
        +------------------+-------------------+---------------------+
        |User_Id           |contains the       |Integer              |
        |                  |internal user id   |                     |
        +------------------+-------------------+---------------------+ 
        |User_String       |contains the set   |Varchar(256)         |                           
        |                  |string value for   |                     |
        |                  |the setting        |                     |
        +------------------+-------------------+---------------------+
        |User_Integer      |contains the set   |Integer              |                               
        |                  |integer value for  |                     |
        |                  |the setting        |                     |
        +------------------+-------------------+---------------------+ 
        |Boolean           |contains the set   |Boolean              |                      
        |                  |boolean value for  |                     |
        |                  |the setting        |                     | 
        +------------------+-------------------+---------------------+ 
        |PRIMARY KEY (User_Setting_Id)                               |
        +------------------------------------------------------------+
        
        +------------------------------------------------------------+
        |User_Answers_To_Poll                                        |  
        +==================+===================+=====================+         
        |Answer_Id         |contains the answer|Integer              |
        |                  |id                 |(auto_increment)     |
        +------------------+-------------------+---------------------+      
        |By_User           |contains the user  |Integer              |
        |                  |id the answer has  |                     |
        |                  |been submitted from|                     |
        +------------------+-------------------+---------------------+                
        |By_Group          |contains the group |  Integer            |
        |                  |id in that the     |                     |
        |                  |answer has been    |                     |
        |                  |submitted from     |                     | 
        +------------------+-------------------+---------------------+        
        |Poll_Id           |contains the poll  |Integer              |
        |                  |id for that the    |                     |
        |                  |answer has been    |                     |
        |                  |submitted for      |                     |
        +------------------+-------------------+---------------------+
        |Option_ID         |contains the id of |Integer              |
        |                  |option that has    |                     |
        |                  |submitted          |                     |
        +------------------+-------------------+---------------------+
        |PRIMARY KEY (Answer_Id)                                     |
        +------------------------------------------------------------+  
    """

    def __init__(self,
                 User,
                 Password,
                 DatabaseName=None,
                 Host="127.0.0.1",
                 Port="3306",
                 **OptionalObjects):

        """
        This API enables an easy DatabaseConnection to the mysql driver 
        and to the server with the database .
    
        VARIABLES:
            User                     ``string``                             
                contains the database user
            Password                 ``string``                               
                contains the database user password
            DatabaseName             ``string``                             
                contains the database name
            Host                     ``string``
                contains the database host ip
            Port                     ``string``
                contains the database port 
            OptionalObjects          ``dictionary``
                contains optional objects like the language object, 
                the logging object or else
        """

        self.User = User
        self.Password = Password
        self.Host = Host
        self.DatabaseName = DatabaseName
        self.Port = Port

        # This variable defines if the system should shutdown if no connection
        # was created.
        self._DieOnLostConnection = False

        # Predefining some attributes so that they later can be used for evil.
        self.LanguageObject = None
        self.LoggingObject = None

        if "LanguageObject" in OptionalObjects:
            self.LanguageObject = OptionalObjects["LanguageObject"]
        else:
            self.LanguageObject = (
                language.language.CreateTranslationObject()
            )

        # This is the language objects only value. 
        # It enables the translation of the texts. 
        self._ = self.LanguageObject.gettext

        if "LoggingObject" in OptionalObjects:
            self.LoggingObject = OptionalObjects["LoggingObject"]
        else:
            self.LoggingObject = custom_logging.Logger()

        # Create the connection to the database. 
        self.DatabaseConnection = self.CreateConnection()

    def CreateConnection(self):
        """
        This method creates the mysql connection database.
        
        This method will return a mysql connection object if the
        connection could be created successfully. If not it will
        catch the error and make a log entry. 
        
        Variables:
            \-
        """

        try:
            config = {
                "user": self.User,
                "password": self.Password,
                "host": self.Host,
                "port": 3306,
                # "use_pure":False,
                "raise_on_warnings": True,
            }
            if self.DatabaseName:
                config['database'] = self.DatabaseName

            return mysql.connector.connect(**config)

        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                self.LoggingObject.warning(
                    self._("The database connector returned following"
                           " error: {Error}").format(Error=err) + " " +
                    self._("Something is wrong with your user name or "
                           "password."),
                )
                if self._DieOnLostConnection is True:
                    raise SystemExit
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.LoggingObject.error(
                    self._("The database connector returned following"
                           " error: {Error}").format(Error=err) + " " +
                    self._(
                        "The database does not exist, please contact your "
                        "administrator.")
                )
                if self._DieOnLostConnection is True:
                    raise SystemExit
            elif err.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
                self.LoggingObject.critical(
                    self._("The database connector returned following"
                           " error: {Error}").format(Error=err) + " " +
                    self._(
                        "The database server seems to be offline, please "
                        "contact your administrator.")
                )
                if self._DieOnLostConnection is True:
                    raise SystemExit
            else:
                self.LoggingObject.error(err)
                if self._DieOnLostConnection is True:
                    raise SystemExit
        except:
            self.LoggingObject.critical(
                self._("The database connector returned following "
                       "error: {Error}").format(Error=sys.exc_info()[0]))
            if self._DieOnLostConnection is True:
                raise SystemExit

        else:
            self.CloseConnection()

    def CloseConnection(self, ):
        """
        This method will close the open connection for good.
        
        Variables:
            \-
        """
        try:
            self.DatabaseConnection.close()
        except mysql.connection.Error as err:
            self.LoggingObject.error(
                self._("The database connector returned following error: "
                       "{Error}").format(Error=err) + " " + self._(
                    "The database connection could not be closed correctly,"
                    " please contact your administrator!"))
        except Exception:
            self.LoggingObject.critical(
                self._("The database connector returned following error: "
                       "{Error}").format(Error=sys.exc_info()[0]))

    def DetectConnection(self):
        """
        This method will check if the database connection is open.

        It return True if the connection exists else False.
        It as well tries to reconnect if no connection is available.

        Variables:
            \-
        """
        import time
        # This is needed to sleep while trying
        # to reconnect to the server.
#        print(self.DatabaseConnection.is_connected())
        Connection = True
        while True:
            if self.DatabaseConnection is not None:
                try:
                    self.DatabaseConnection.reconnect()
                except mysql.connector.Error as err:
                    if (err.errno ==
                            mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR):
                        self.LoggingObject.warning(
                            self._("The database connector returned following"
                                   " error: {Error}").format(Error=err) + " " +
                            self._(
                                "Something is wrong with your user name or "
                                "password."),
                        )
                        if self._DieOnLostConnection is True:
                            raise SystemExit
                    elif (err.errno ==
                              mysql.connector.errorcode.ER_BAD_DB_ERROR):
                        self.LoggingObject.error(
                            self._("The database connector returned following"
                                   " error: {Error}").format(Error=err) + " " +
                            self._(
                                "The database does not exist, please contact"
                                " your administrator.")
                        )
                        if self._DieOnLostConnection is True:
                            raise SystemExit
                    elif (err.errno ==
                              mysql.connector.errorcode.CR_CONN_HOST_ERROR):
                        self.LoggingObject.critical(
                            self._("The database connector returned following"
                                   " error: {Error}").format(Error=err) + " " +
                            self._(
                                "The database server seems to be offline, "
                                "please contact your administrator.")
                        )
                        if self._DieOnLostConnection is True:
                            raise SystemExit
                    else:
                        self.LoggingObject.error(err)
                        if self._DieOnLostConnection is True:
                            raise SystemExit
                except Exception as Error:
                    self.LoggingObject.critical(
                        self._("The database connector returned following "
                               "error: {Error}").format(Error=Error))
                    if self._DieOnLostConnection is True:
                        raise SystemExit

                if self.DatabaseConnection.is_connected() is True:
                    if Connection is False:
                        self.LoggingObject.info(self._(
                            "The connection to the database server has been "
                            "reestablished.")
                        )
                    return True
                else:
                    Connection = False
                    self.LoggingObject.critical(self._(
                        "There is no connection to the database, please "
                        "contact your administrator!")
                    )
            else:
                self.DatabaseConnection = self.CreateConnection()

            # sleep for three seconds
            time.sleep(3)


    def CreateCursor(self,
                     Buffered=False,
                     Dictionary=True):
        """
        This method creates the connection cursor
        
        It returns the connection cursor.
        
        Variables:
            Buffered            ``boolean``
                If the cursor is buffered or not default to False.
           Dictionary           ``boolean``
               If the cursor should return a dictionary or not.
        """
        return self.DatabaseConnection.cursor(
            buffered=Buffered,
            dictionary=Dictionary
        )

    def GetLastRowId(self, Cursor):
        """
        This method returns the last used row id of the cursor.
        
        Variables:
            Cursor                ``object``
                cursor object.
        """
        return Cursor.lastrowid

    def DestroyCursor(self, Cursor):
        """
        This method closes the cursor.
        
        Variables:
            Cursor                ``object``
                cursor object.
        """
        return Cursor.close()

    def ExecuteTrueQuery(self,
                         Cursor,
                         Query,
                         Data=None):
        """
        A method to execute the query statements.
        
        All the query will be passed over this method so that the 
        exceptions can be catched at one central place. This method
        will return the results from the database.
        
        Variables:
            Cursor                ``object``
                contains the cursor object
            Query                 ``string``
                contains the query that has to be executed
            Data                  ``list``
                contains the data to be send to the databse
         
        .. code-block:: python\n       
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
                if not isinstance(Data, dict) and not isinstance(Data, list):
                    if isinstance(Data, int):
                        Data = (Data,)
                    elif isinstance(Data, str):
                        Data = (Data,)
                    Data = [str(i) for i in list(Data)]
                    Cursor.execute(Query, Data)
                else:
                    Cursor.execute(Query, Data)
            else:
                Cursor.execute(Query)

            CursorContent = []
            for Item in Cursor:
                CursorContent.append(Item)
            return CursorContent

        except mysql.connector.Error as err:
            self.LoggingObject.error(
                self._("The database returned following error: {Error}"
                       ).format(Error=err) + " " +
                self._(
                    "The executet query failed, please contact your "
                    "administrator."
                )
            )
            if isinstance(Data, list):
                Data = ', '.join((str(i) for i in Data))
            elif isinstance(Data, dict):
                Data = ', '.join("{Key}={Value}".format(
                    Key=Key, Value=Value) for (Key, Value) in Data.items()
                                 )
            self.LoggingObject.error(
                self._("The failed query is:\nQuery:\n{Query}\n\nData:\n{Data}"
                       ).format(
                    Query=Query,
                    Data=Data)
            )

    def CreateDatabase(self, Cursor, DatabaseName):
        """
        This method will create a database. Use with caution!
        
        Variables:
            Cursor                ``object``
                contains the cursor object
            DatabaseName          ``string``
                contains the database name that has to be created
        """
        Query = ("CREATE DATABASE IF NOT EXISTS {DatabaseName} DEFAULT "
                "CHARACTER SET 'utf8'".format(DatabaseName=DatabaseName))

        self.ExecuteTrueQuery(
            Cursor,
            Query
        )

    def DeleteDatabase(self, Cursor, DatabaseName):
        """
        This method will drop a database. Use with caution!
        
        Variables:
            Cursor                ``object``
                contains the cursor object
            DatabaseName          ``string``
                contains the database name that has to be dropped
        """
        Query = ("DROP DATABASE {DatabaseName};".format(
            DatabaseName=DatabaseName)
        )

        self.ExecuteTrueQuery(
            Cursor,
            Query
        )

    def CreateTable(self,
                    Cursor,
                    TableName,
                    TableData,
                    IfNotExists=True,
                    Engine="InnoDB"):
        """
        A method to dynamically create a table entry to the database.
        
        HOW TO USE:\n
        .. code-block:: python\n
            TableData = (
                ('Id', 'INT UNSIGNED NOT NULL AUTO_INCREMENT'),
                ('Unique', 'ID'),
                ('PRIMARY KEY', 'ID'),
                ('Foreigh Key', 'ID', 'Persons(P_Id)')
                )
                    
        Variables:
            Cursor                ``object``
                contains the cursor object
            TableName             ``string``
                contains the table name that has to be created
            TableData             ``array (list or tuple)``
                contains the table columns that will be created
            IfNotExists           ``boolean``
                determines if the query will be created with the prefix
                ``IF NOT EXISTS`` is used as a default since it doesn't 
                really matter
            Engine                ``string``
                determine what mysql engine will be used
                
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
                if (TableData[i][0].lower() != 'primary key' and
                            TableData[i][0].lower() != 'unique' and
                            TableData[i][0].lower() != 'foreign key'):
                    if i == 0:
                        Query += TableData[i][0] + " " + TableData[i][1]
                    else:
                        Query += ", " + TableData[i][0] + " " + TableData[i][1]

                else:
                    if (TableData[i][0].lower() == 'primary key'):
                        PrimaryKeyId = i
                    elif TableData[i][0].lower() == 'unique':
                        UniqueKeyId = i
                    elif TableData[i][0].lower() == 'foreign key':
                        ForeignKeyId = i

            # If a unique key has been added.
            if UniqueKeyId:
                if Query[-1] != ",":
                    Query += ","
                Query += (" " + TableData[UniqueKeyId][0] + " (" +
                          TableData[UniqueKeyId][1] + ")"
                          )

            # If a Primary Key has been added.
            if PrimaryKeyId:
                if Query[-1] != ",":
                    Query += ","
                Query += (" " + TableData[PrimaryKeyId][0] + " (" +
                          TableData[PrimaryKeyId][1] + ")"
                          )

            # If a Foreign Key has been added.
            if ForeignKeyId:
                if Query[-1] != ",":
                    Query += ","
                Query += (" " + TableData[ForeignKeyId][0] + " (" +
                          TableData[ForeignKeyId][1] + ") REFERENCES " +
                          TableData[ForeignKeyId][2]
                          )

            Query += ")"

            if Engine != None:
                if Engine in ("MRG_MYISAM",
                              "MyISAM",
                              "BLACKHOLE",
                              "CSV",
                              "MEMORY",
                              "ARCHIVE",
                              "InnoDB"):
                    Query += "ENGINE=" + Engine

            Query += ";"
            Cursor.execute(Query)
            return True

        except mysql.connector.Error as err:
            self.LoggingObject.error(
                self._("The database connector returned following error: "
                       "{Error}").format(Error=err) + " " +
                self._("The following database table \"{TableName}\" could not"
                       " be created, please contact your administrator."
                       ).format(TableName=TableName),
            )
            self.DatabaseConnection.rollback()
            return False

    def CreateMainDatabase(self,
                           Cursor):
        """
        This method will create all the default tables and data.
        
        Variables:
            Cursor                ``object``
                contains the cursor object        
        """

        # First all the tables
        # UserTable
        TableData = (
            ("Internal_User_Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("External_User_Id", "Integer"),
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("User_Name", "TEXT DEFAULT NULL"),
            ("First_Name", "TEXT DEFAULT NULL"),
            ("Last_Name", "TEXT DEFAULT NULL"),
            ("PRIMARY KEY", "Internal_User_ID")
        )

        self.CreateTable(Cursor, "User_Table", TableData, )

        # SessionHandling saves the last send command
        TableData = (
            ("Session_Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("Command_By_User", "Integer"),  # is the internal id of the user
            ("Command", "Varchar(256)"),
            ("Last_Used_Id", "Integer DEFAULT NULL"),
            ("PRIMARY KEY", "Session_Id"),
            ("UNIQUE", "Command_By_User"),
        )

        self.CreateTable(Cursor, "Session_Table", TableData, )

        # Settings
        TableData = (
            ("Setting_Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("Setting_Name", "Varchar(128)"),
            ("Default_String", "Varchar(256)"),
            ("Default_Integer", "Integer"),
            ("Default_Boolean", "Boolean"),
            ("PRIMARY KEY", "Setting_Id")
        )

        self.CreateTable(Cursor, "Setting_Table", TableData, )

        # UserSetSetting
        TableData = (
            ("Setting_Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("Master_Setting_Id", "Integer"),  # This settings master entry in
            ("Master_User_Id", "Integer"),  # This setting has been set by
            ("User_Integer", "Integer"),
            ("User_String", "Varchar(256)"),
            ("User_Boolean", "Boolean"),
            ("PRIMARY KEY", "Setting_Id"),
            ("FOREIGN KEY", "Master_Setting_Id", "Setting_Table(Setting_Id)"),
            ("FOREIGN KEY", "Master_User_Id", "User_Table(Internal_User_Id)"),
        )

        self.CreateTable(Cursor, "User_Setting_Table", TableData, )

        # GroupTable
        TableData = (
            ("Internal_Group_Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("External_Group_Id", "Integer"),
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("Group_Name", "Varchar(255)"),
            ("UNIQUE", "External_Group_Id"),
            ("PRIMARY KEY", "Internal_Group_Id")
        )

        self.CreateTable(Cursor, "Group_Table", TableData, )

        # The PollTable
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

        self.CreateTable(Cursor, "Poll_Table", TableData, )

        # Options for the Polls themselves
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

        self.CreateTable(Cursor, "Options_Table", TableData, )

        # All the available settings of the poll
        TableData = (
            ("Setting_Id", "Integer NOT NULL AUTO_INCREMENT"),
            ("Creation_Date", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"),
            ("Setting_Name", "Varchar(128)"),
            ("Default_Integer", "Integer"),
            ("Default_String", "Varchar(256)"),
            ("Default_Boolean", "Boolean"),
            ("PRIMARY KEY", "Setting_Id")
        )

        self.CreateTable(Cursor, "Settings_Of_Poll_Table", TableData, )

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

        self.CreateTable(Cursor, "User_Setting_Of_Poll_Table", TableData, )

        # User answer to the poll
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

        self.CreateTable(Cursor, "User_Answers_To_Poll_Table", TableData, )

        # Second all the inserts
        # The Settings for the default polls

        # The default language for the polls
        Columns = {
            "Setting_Name": "Language",
            "Default_String": "en_US"
        }

        self.InsertEntry(Cursor, "Settings_Of_Poll_Table", Columns)

        # The setting to define if a response should be forced
        Columns = {
            "Setting_Name": "ForceResponce",
            "Default_Boolean": False
        }

        self.InsertEntry(Cursor, "Settings_Of_Poll_Table", Columns)

        # The setting to define if multiple answer per persons are 
        # allowed.
        Columns = {
            "Setting_Name": "MultiAnswer",
            "Default_Boolean": False
        }

        self.InsertEntry(Cursor, "Settings_Of_Poll_Table", Columns)
        # the inserts for the settings 
        Columns = {
            "Setting_Name": "Language",
            "Default_String": "en_US"
        }
        self.InsertEntry(Cursor, "Setting_Table", Columns)

        # commit all the changes
        self.Commit()

        return True

    def SelectEntry(self,
                    Cursor,
                    FromTable,
                    Columns,
                    OrderBy=[None],
                    Amount=None,
                    Where=[],
                    Data=(),
                    Distinct=False, ):
        """
        A simple SQL SELECT builder method
        
        This method will be replaces in the future by the query class
        generator.
        
        Variables:
            Cursor                ``object``
                contains the cursor object  
                
            FromTable,            ``string``
                contains the table name from which the system takes
                the information
            
            Columns               ``array (list or tuple)``
                contains the columns to be inserted into
            
            OrderBy               ``array (list or tuple)``
                contains the order in which the data will be returned
                
                .. code-block:: python\n
                    Example
                        [
                            [
                                column_name, 
                                "ASC"
                            ],
                            [
                                column_name, 
                                    #if the order is empty ASC will be used
                            ],
                            [
                                column_name,
                                "DESC"
                            ]
                        ] 
                
            Amount                ``None or integer``
                is the limit of entries that will be returned
                
            Where                 ``array (list or tuple)`` 
                contains the filter of the query
                Example\n
                .. code-block:: python\n
                    [
                        [
                            'column_name', 
                            operator, 
                            value
                        ], 
                        operator,
                         [    
                             column_name, 
                             operator, 
                             "%s" 
                             # if %s is used the value has to be 
                             # mentioned in the Data variable
                        ]
                    ]
                    
            Data                 ``array (list or tuple)``
                contains the data that will be inserted into the query
                
            Distinct             ``boolean``
                determines if the search is distinct or not
        """

        Query = ["SELECT"]

        if Distinct:
            Query.append("DISTINCT")

        # columns
        for i in range(len(Columns)):
            if i + 1 < len(Columns):
                Query.append(Columns[i] + ",")
            else:
                Query.append(Columns[i])

        # from Table
        Query.append("FROM " + FromTable)

        # Where
        if Where != []:
            Query.append("WHERE")
            for i in range(len(Where)):
                if type(Where[i]) == type([]):
                    Query.append(Where[i][0])
                    Query.append(Where[i][1])
                    Query.append("{0}".format(Where[i][2]))
                elif type(Where[i]) == type(""):
                    Query.append(Where[i])

                #                 if i+1 != len(Where):
                #                     Query.append(",")

                # print(Where[i])

                # Query.append(Where[i])

        # Order By
        if OrderBy[0] is not None:
            Query.append("ORDER BY")

            for i in range(len(OrderBy)):
                for x in range(len(OrderBy[i])):
                    if not OrderBy[i] in ("and", "or"):
                        Query.append(OrderBy[i][x])
                    else:
                        Query.append(OrderBy[i])

                if i + 1 < len(OrderBy):
                    Query.append(",")



        # Limit
        if (Amount is not None) and (isinstance(Amount, int)):
            Query.append("LIMIT " + str(Amount))

        Query.append(";")

        Query = ' '.join([str(i) for i in Query])

        if Data == ():
            return self.ExecuteTrueQuery(Cursor, Query, )
        else:
            return self.ExecuteTrueQuery(Cursor, Query, Data)

    def UpdateEntry(self,
                    Cursor,
                    TableName,
                    Columns,
                    Where=[],
                    Autocommit=False):
        """
        This method will update a record in the database.
        
        This method will return something like this:\n
        .. code-block:: sql\n
            UPDATE table_name
            SET column1=value1,column2=value2,...
            WHERE some_column=some_value;
        
        Variables:
            Cursor                ``object``
                contains the cursor object 
                 
            TableName             ``string``
                contains the table name into wich the system will 
                insert the information 
                
            Columns               ``dictionary``
                contains the columns into that will be inserted
                Example\n
                .. code-block:: python\n
                    {
                        'id' : id,
                        Name': 'Max'
                    }
                
            Where                 ``array (list or tuple)``
                contains the query filter
                Example\n
                .. code-block:: python\n
                    [
                        [
                            "Id", 
                            "=", 
                            2
                        ], 
                        "AND", 
                        "(", 
                        [
                            "as", 
                            "65" 
                            # Here will automatically the equality 
                            # operator be used. ("=")
                            
                        ], 
                        "OR", # This will raise an error
                        ")",
                    ]
                
            Autocommit            ``boolean``
                If autocommit is true the method will automatically
                commit the values to the database.
            
        """

        Query = "UPDATE "

        Query += TableName

        Query += " SET "

        # Create the key value pair 
        temp = []
        for Key in Columns.keys():
            temp.append("{Key}=%({Key})s".format(Key=str(Key)))

        Query += ', '.join(temp)

        if Where != []:

            Query += " WHERE "

            # This variable is used to ensure that no 2 operator will 
            # follow each other
            LastTypeAnOperator = False
            for i in range(len(Where)):

                if type(Where[i]) == type([]):
                    LastTypeAnOperator = False
                    Where[i] = [str(i) for i in Where[i]]
                    Query += str(Where[i][0])
                    if Where[i][1].upper() in ("=",
                                               "<",
                                               ">",
                                               "<>",
                                               "!=",
                                               ">=",
                                               "<=",
                                               "BETWEEN",
                                               "LIKE",
                                               "IN"):
                        Query += Where[i][1]
                        Query += "%({Where})s".format(Where=Where[i][0] +
                                                            "Where"
                                                      )
                        Columns[Where[i][0] + "Where"] = Where[i][2]
                    else:
                        Query += "=%({Where})s".format(Where=Where[i][0] +
                                                             "Where"
                                                       )
                        Columns[Where[i][0] + "Where"] = Where[i][1]

                elif isinstance(Where[i], str):
                    if LastTypeAnOperator is False:
                        LastTypeAnOperator = True
                        if Where[i].upper() in ("(", ")", "AND", "OR"):
                            Query += " {} ".format(Where[i])
                        else:
                            raise ValueError(self._(
                                "The where type in your query is not in the "
                                "list of valid types. {Error}").format(
                                Error=Where[i])
                            )
                    else:
                        raise ValueError(self._("There where two operator "
                                                "behind each other that "
                                                "doesn't work.")
                                         )
        Query += ";"
        #         print(Query)
        #         print(Columns)
        #         print(Query % Columns)

        self.ExecuteTrueQuery(Cursor, Query, Columns)
        if Autocommit is True:
            # Autocommit the update to the server
            self.Commit()
        return True

    def InsertEntry(self,
                    Cursor,
                    TableName,
                    Columns={},
                    Duplicate=None,
                    AutoCommit=False):
        """
        This method will insert any type of entry into the database.
        
        This method will return something like this:\n
        .. code-block:: sql\n
            UPDATE table_name
            SET column1=value1,column2=value2,...
            WHERE some_column=some_value;
        
        Variables:
            Cursor                ``object``
                contains the cursor object 
                 
            TableName             ``string``
                contains the table name into wich the system will 
                insert the information 
                
            Columns               ``dictionary``
                contains the columns into that will be inserted
                Example\n
                .. code-block:: python\n
                    {
                        'id' : id,
                        Name': 'Max'
                    }
            Duplicate             ``None or dictionary``
                contains the columns in those the possible duplicates 
                values exist
                
            Autocommit            ``boolean``
                If autocommit is true the method will automatically
                commit the values to the database.
        """

        Query = "INSERT INTO "

        Query += TableName + " ("

        Query += ', '.join(Columns.keys())
        Query += ") VALUES ("
        Query += ", ".join(["%(" + str(i) + ")s" for i in Columns.keys()])

        Query += ")"

        if Duplicate != None:
            Query += " ON DUPLICATE KEY UPDATE "
            Duplicates = []
            for Key in Duplicate.keys():
                Duplicates.append("{Key} = %({Value})s".format(Key=str(Key),
                                                               Value=str(Key)
                                                               )
                                  )

            Query += ', '.join(Duplicates)
        Query += ";"

        # print(Query)

        self.ExecuteTrueQuery(Cursor, Query, Columns)

        if AutoCommit:
            # Make sure data is committed to the database
            self.Commit()
        return True

    def DeleteEntry(self,
                    Cursor,
                    TableName,
                    Where={},
                    AutoCommit=False ):
        """
        This method will delete the selected entry.

        .. code-block:: sql\n
            DELETE FROM table_name WHERE some_column=some_value;

        .. code-block:: python\n
            Where = {
                some_column:some_value,
                some_column2:some_value2;
            }
        """

        try:
            Query = ["DELETE",
                     "FROM",
                     TableName,
                     "WHERE"
                     ]

            if not Where:
                raise AttributeError(self._("The where clause is not "
                                            "available")
                                     )

            for Key, Value in Where:
                Query.append("{Value}=%({Key})s".format(
                    Value=Value,
                    Key=Value
                )
                )

            # Join the query to a string and append a semicolon.
            Query = " ".join(Query)+";"
            self.ExecuteTrueQuery(Cursor, Query, Where)

            if AutoCommit:
                # Make sure data is committed to the database
                self.Commit()

            return True

        except AttributeError as Error:
            self.LoggingObject.error(Error)
            raise

        except Exception as Error:
            self.LoggingObject.error(
                self._("The database connector returned following error: "
                       "{Error}").format(Error = Error)
            )

            return False

    def Commit(self, ):
        """
        This method will commit the changes to the database.
        
        Variables:
            Cursor                ``object``
                contains the cursor object 
        """
        try:
            self.DatabaseConnection.commit()
        except mysql.DatabaseConnection.Error as Error:
            self.LoggingObject.error(
                self._("The database connector returned following error:"
                       " {Error}").format(Error=Error))
            self.DatabaseConnection.rollback()
