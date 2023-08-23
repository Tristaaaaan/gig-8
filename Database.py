import json
import os
import mysql.connector
from contextlib import contextmanager
from mysql.connector import pooling
import threading

# JSON file for local storage
LOCAL_STORAGE_PATH = "local_storage.json"

class DatabaseManager:
    def __init__(self):
        self.cnxpool = None


    def setup_connection_pool(self, host, user, passwd, database, pool_size=5):
        if not self.cnxpool:
            self.cnxpool = pooling.MySQLConnectionPool(pool_name="mypool",
                                                      pool_size=pool_size,
                                                      host=host,
                                                      user=user,
                                                      passwd=passwd,
                                                      database=database)

    def get_database_connection(self):
        if not self.cnxpool:
            raise ValueError("Connection pool not set up. Call setup_connection_pool() first.")
        return self.cnxpool.get_connection()



    def load_data_from_database(self):
        with database_connection() as database:
            cursor = database.cursor()
            cursor.execute("SELECT * FROM enquiry_form")
            result = cursor.fetchall()

            local_data = {"put_data": []}
            for row in result:
                data = {
                    "parents_name": row[1],
                    "student_name": row[2],
                    "class_name": row[3],
                    "address": row[4],
                    "phone1": row[5],
                    "phone2": row[6],
                    "other_details": row[7],
                    "follow_date": row[8],
                    "message": row[9],
                    "message_datetime": row[10],
                    "status": row[11],
                    "username": row[12],

                }
                local_data['put_data'].append(data)

            # Save fetched data to the local storage
            local_storage.save_data(local_data)

db_manager = DatabaseManager()
db_manager.setup_connection_pool("sql741.main-hosting.eu", "u404857937_gdvk", "Gdvk123@", "u404857937_aenquiry")

#db_manager.setup_connection_pool("sql741.main-hosting.eu", "u404857937_gdvk", "Gdvk123@", "u404857937_aenquiry")

class LocalStorage:
    def __init__(self, file_path):
        self.file_path = file_path

    def save_data(self, data):
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return None

local_storage = LocalStorage(LOCAL_STORAGE_PATH)

@contextmanager
def database_connection():
    connection = db_manager.get_database_connection()
    try:
        yield connection
    finally:
        connection.close()

def execute_query_and_fetch_result(query, params):
    with database_connection() as database:
        cursor = database.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result

def verify_credentials(username, password):
    data = local_storage.load_data()
    if data and 'login_data' in data and (username, password) in data['login_data']:
        return True
    query = "SELECT * FROM login_data WHERE username = %s AND password = %s"
    params = (username, password)
    result = execute_query_and_fetch_result(query, params)
    return result is not None

def save_login_data_in_local_storage(username, password):
    data = local_storage.load_data() or {'login_data': []}
    data['login_data'].append((username, password))
    local_storage.save_data(data)

def register_user(username, full_name, password):
    with database_connection() as database:
        cursor = database.cursor()
        sql = "INSERT INTO login_data (username, full_name, password) VALUES (%s, %s, %s)"
        val = (username, full_name, password)
        cursor.execute(sql, val)
        database.commit()
        data = local_storage.load_data() or {}
        data.setdefault('register_user', []).append({
            'username': username,
            'full_name': full_name,
            'password': password
        })
        local_storage.save_data(data)

def put_data(parents_name, student_name, class_name, address, phone1, phone2, other_details, follow_date, selected_item):
    data = {
        "parents_name": parents_name,
        "student_name": student_name,
        "class_name": class_name,
        "address": address,
        "phone1": phone1 if phone1 else None,
        "phone2": phone2 if phone2 else None,
        "other_details": other_details,
        "follow_date": follow_date if follow_date else None,
        "status": selected_item,
        "username": None,
        "message": None,
        "message_datetime": None,
    }
    local_data = local_storage.load_data() or {'put_data': []}
    local_data['put_data'].append(data)
    local_storage.save_data(local_data)
    threading.Thread(target=put_data_in_database, args=(data,)).start()

def put_data_in_database(data):
    with database_connection() as database:
        cursor = database.cursor()
        sql = """INSERT INTO enquiry_form (parents_name, student_name, class_name, address, phone1, phone2, other_details, follow_date, status, username)
                     VALUES (%(parents_name)s, %(student_name)s, %(class_name)s, %(address)s, %(phone1)s, %(phone2)s, %(other_details)s, %(follow_date)s, %(status)s, %(username)s)"""
        cursor.execute(sql, data)
        database.commit()

def view_data():
    local_data = local_storage.load_data()
    if local_data and 'put_data' in local_data:
        return local_data['put_data']

def update_data(parents_name, new_messages, message_datetime, username):
    local_data = local_storage.load_data()
    if local_data is None:
        local_data = {}
    if 'put_data' not in local_data:
        local_data['put_data'] = []

    # Search for the data to update
    for data in local_data['put_data']:
        if data['parents_name'] == parents_name:
            # Update the data
            data['message'] = new_messages
            data['message_datetime'] = message_datetime
            data['username'] = username
            break
    else:
        # If no existing data was found, add a new one
        updated_data = {
            'parents_name': parents_name,
            'message': new_messages,
            'message_datetime': message_datetime,
            'username': username
        }
        local_data['put_data'].append(updated_data)

    # Save the updated data back to local storage
    local_storage.save_data(local_data)
    threading.Thread(target=update_data_in_database,
                     args=(parents_name, new_messages, message_datetime, username)).start()


def update_data_in_database(parents_name, new_messages, message_datetime, username):
    with database_connection() as database:
        cursor = database.cursor()
        cursor.execute(
            "UPDATE enquiry_form SET message_data=%s, message_datetime=%s, username=%s WHERE parents_name=%s",
            (new_messages, message_datetime, username, parents_name))
        database.commit()

def update_status(parents_name, status):
    local_data = local_storage.load_data()
    if local_data is None:
        local_data = {}
    if 'put_data' not in local_data:
        local_data['put_data'] = []

    # Search for the data to update
    for data in local_data['put_data']:
        if data['parents_name'] == parents_name:
            # Update the status
            data['status'] = status
            break
    else:
        # If no existing data was found, add a new one
        updated_status = {
            'parents_name': parents_name,
            'status': status
        }
        local_data['put_data'].append(updated_status)

    # Save the updated data back to local storage
    local_storage.save_data(local_data)
    threading.Thread(target=update_status_in_database, args=(parents_name, status)).start()

def update_status_in_database(parents_name, status):
    with database_connection() as database:
        cursor = database.cursor()
        cursor.execute("UPDATE enquiry_form SET status=%s WHERE parents_name=%s", (status, parents_name))
        database.commit()
