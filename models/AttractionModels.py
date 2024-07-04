from db import connection_pool
from ErrorHandler import raise_custom_error

def get_attractions(page):
    try:
        query_paginated = ("SELECT * FROM data "
                    "ORDER BY id "
                    "LIMIT 12 OFFSET %s;")
        offset = page * 12
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(query_paginated, (offset,))
        return cursor.fetchall()
    except Exception:
        raise_custom_error(500, "Internal Server Error")
    finally:
        connection.close()

def get_attractions_by_keyword(page, keyword):
    try:
        query_keyword = ("SELECT * FROM data "
                "WHERE name LIKE %s OR mrt = %s "
                "ORDER BY id "
                "LIMIT 12 OFFSET %s;")
        offset = page * 12
        params = ("%" + keyword + "%", keyword, offset)
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(query_keyword, params)
        return cursor.fetchall()
    except Exception:
        raise_custom_error(500, "Internal Server Error")
    finally:
        connection.close()

def get_attraction_by_id(id):
    try:
        query_by_id = ("SELECT * FROM data "
					"WHERE id = %s;")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(query_by_id, (id,))
        return cursor.fetchone()
    except Exception:
        raise_custom_error(500, "Internal Server Error")
    finally:
        connection.close()
		