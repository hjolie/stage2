from db import connection_pool
from ErrorHandler import raise_custom_error

def find_user(email):
    try:
        find_user = ("SELECT * FROM user "
            "WHERE email = %s")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(find_user, (email,))
        return cursor.fetchall()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Finding User")
    finally:
        connection.close()

def signup_user(name, email, password):
    try:
        add_new_user = ("INSERT INTO user "
                "(name, email, password) "
                "VALUES(%s, %s, %s)")
        new_user_data = (name, email, password)
        connection =  connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(add_new_user, new_user_data)
        connection.commit()
        return {"ok": True}
    except Exception:
        raise_custom_error(500, "Internal Server Error - Adding New User")
    finally:
        connection.close()

def signin_user(email, password):
    try:
        find_user = ("SELECT id, name FROM user "
            "WHERE email = %s "
            "and password = %s")
        user_credential = (email, password)
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(find_user, user_credential)
        return cursor.fetchall()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Verifying User")
    finally:
        connection.close()