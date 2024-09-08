import pymysql

def get_mysql_connection():
    db_config = {
        'host': 'localhost',
        'port': '3306',
        'user': 'ali',
        'password': 'mysql2023',
        'database': 'citycodes_qa_records',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }


    return pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        db=db_config['database'],
        charset=db_config['charset'],
        cursorclass=db_config['cursorclass']
    )

def fetch_website_url(city, state_id):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT website FROM records WHERE city = %s AND state_id = %s", (city, state_id))
        result = cursor.fetchone()
        return result['website'] if result else None
    finally:
        connection.close()

def fetch_record_data(url):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT building_department_main_phone, municipality_main_tel, building_department_main_email, chief_building_official_name FROM records WHERE website = %s", (url,))
        return cursor.fetchone()
    finally:
        connection.close()


def fetch_record(city, state_id):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT building_department_main_phone, municipality_main_tel, building_department_main_email, chief_building_official_name FROM records  WHERE city = %s AND state_id = %s", (city, state_id))
        return cursor.fetchone()
    finally:
        connection.close()

def update_record(url, updates):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    try:
        for value, field in updates:
            cursor.execute(f"UPDATE records SET {field} = %s WHERE website = %s", (value, url))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

def update_record_data(city, state_id, updates):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    try:
        for value, field in updates:
            query = f"UPDATE records SET {field} = %s WHERE city = %s AND state_id = %s"
            cursor.execute(query, (value, city, state_id))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()  # Close the cursor
        connection.close()

