import sqlite3 as sql
import time
import config

import logging
log = logging.getLogger(__name__)

class MusicInfo:
    def __init__(self):
        self.url = None
        self.source = None
        self.filename = None
        self.metadata = None

def execute(conn, sql_command, params = None, return_rows = False):
    """ execute a given sql statement
    conn -> Connection object
    sql_command -> any sql statement
    params -> a tuple containg variables that can be plugged into the sql_command
    """
    ret = False
    try:
        c = conn.cursor()
        if params is None:
            c.execute(sql_command)
        else:
            c.execute(sql_command, params)

        ret = True
        if return_rows:
                    rows = c.fetchall()
                    return (ret, rows)
        return (ret)
    except sql.Error as e:
        logging.error("SQL Error:: %s",str(e))
        ret = False
    except:
        logging.error("Unexpected Error!")
        ret = False
    if return_rows:
            return(ret, None)
    return ret

def insert_music_base_info(o_music_info):
    timestamp = int(time.time())
    #insert an entry to table
    insert_into_base_sql =  """
                                INSERT INTO base (LogTime, Url,
                                    Source, Filename, Metadata)
                                VALUES (?, ?, ?, ?, ?)
                            """
    insert_into_base_values_tup = (timestamp, o_music_info.url,
                                    o_music_info.source, o_music_info.filename , o_music_info.metadata)
    if (execute (conn, insert_into_base_sql, insert_into_base_values_tup)):
        conn.commit()
        return True
    else:
        return False

def is_music_present_in_db(url):
    sql_check_url = "SELECT Filename, Metadata FROM base WHERE Url = \'"+url+"\'"
    ret, rows = execute (conn, sql_check_url, None, True)
    if (ret and len(rows)!= 0):
             return (rows[0][0], rows[0][1])
    return None

def get_files_not_uploaded_to_cloud():
    sql_query = "SELECT Filename FROM base WHERE SavedToCloud = 0"
    ret, rows = execute (conn, sql_query, None, True)
    if (ret and len(rows)!= 0):
        ret_list = []
        for file_tup in rows:
            if file_tup[0] not in ret_list:
                ret_list.append(file_tup[0])
        return (ret_list)
    return []

def update_SavedToCloud_for_file(filename_list):
    if not filename_list:
        logging.info ("No Files to check SavedToCloud flag")
        return True
    sql_query = "UPDATE base SET SavedToCloud = 1 WHERE Filename IN ("
    for file in filename_list:
        sql_query += "\'"+file+"\', "
    sql_query = sql_query[:-2]
    sql_query += ")"
    if (execute (conn, sql_query)):
        conn.commit()
        return True
    else:
        return False

#create and connect to the db if not already present
database = config.DB_PATH
try:
    conn = sql.connect(database)
except sql.Error as e:
    logging.info (f"Exception while creating/connecting to database file [{database}]:[{str(e)}]")

#create table "base" if not already present
sql_create_base_table = """ CREATE TABLE IF NOT EXISTS base (
                                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    LogTime INT,
                                    Url TEXT,
                                    Source TEXT,
                                    Filename TEXT,
                                    Metadata TEXT,
                                    SavedToCloud INT DEFAULT 0
                                ); """

if (not execute(conn, sql_create_base_table)):
    logging.error("Failed to create table [base]!")


#conn.close()
