# Python file that will deal with database-related functions

import sqlite3
import pickle


# store object
def store_pickle(obj):
    pickle_obj = pickle.dumps(obj)



# create DB connection
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection successful")
        return connection
    except Exception as e:
        print("[x]",e)

# execute DB query
def query(connection,query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query succesfull")
    except Exception as e:
        print("[x]",e)