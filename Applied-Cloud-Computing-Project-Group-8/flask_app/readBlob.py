import mysql.connector
import os
from mysql.connector import Error

def convertAndSaveFile(fileName, fileExtension, data):
    my_path_to_data = os.environ.get('PATH_TO_DOWNLOADED_RESULTS')
    fullFileName = str(fileName+"."+fileExtension)
    try:
        with open(my_path_to_data+fullFileName,"w+") as file:
            file.write(data)
        file.close()
    except:
        print("Could not write to file {} with given data.".format(fullFileName))

    return 

def retrive_result(xmlFileFullName):
    my_host = os.environ.get('DB_HOST_ADDRESS')
    my_database = os.environ.get('DB_DATABASE_NAME')
    my_user = os.environ.get('DB_USER_BROKER')
    my_password = os.environ.get('DB_PASSWORD_BROKER')

    my_fileName, separator, my_fileExtension = xmlFileFullName.partition(".")

    try:
        #Connecting to the database
        myconnection = mysql.connector.connect(host=my_host,
                                        database=my_database,
                                        user=my_user,
                                        password=my_password)
        mycursor = myconnection.cursor()
        

        sql_select_Query = "SELECT * FROM "+str(my_fileName)+";" 
        print(sql_select_Query)
        mycursor.execute(sql_select_Query)
        records = mycursor.fetchall()
        for row in records:
            convertAndSaveFile(row[0], row[1], row[2])
	
    except mysql.connector.Error as error:
        print("Failed connecting to database {} and retrive table {} with error {}".format(my_database, my_fileName, error))

    finally:
        if (myconnection.is_connected()):
            myconnection.close()
            mycursor.close()
            print("MySQL connection is closed")
    return
	
def check_if_result_exists(fullFileName):
    my_host = os.environ.get('DB_HOST_ADDRESS')
    my_database = os.environ.get('DB_DATABASE_NAME')
    my_user = os.environ.get('DB_USER_BROKER')
    my_password = os.environ.get('DB_PASSWORD_BROKER')

    my_fileName, separator, my_fileExtension = fullFileName.partition(".")
    db_table_name_list = []

    doesResultExist = None

    try:
        #Connecting to the database
        myconnection = mysql.connector.connect(host=my_host,
                                        database=my_database,
                                        user=my_user,
                                        password=my_password)
        mycursor = myconnection.cursor()
        

        #Extracting table names
        mycursor.execute("SHOW TABLES")
        for (table,) in mycursor:
            db_table_name_list.append(table)
        
        #Return if table name already exist
        if my_fileName in db_table_name_list:
            doesResultExist = True
        else:
            doesResultExist = False
  
        if (myconnection.is_connected()):
            myconnection.close()
            mycursor.close()
            print("MySQL connection is closed")

    except mysql.connector.Error as error:
        print("Failed connecting to database {} and retrive table {} with error {}".format(my_database, my_fileName, error))

#    finally:
#        if (myconnection.is_connected()):
#            myconnection.close()
#            mycursor.close()
#            print("MySQL connection is closed")
    
    return doesResultExist

