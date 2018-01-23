import sqlite3
from sqlite3 import Error

# LOGICAL LEVEL   #
###################
# id, x, y, error #
###################

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None

if __name__ == '__main__':
    create_connection('paths.db')

