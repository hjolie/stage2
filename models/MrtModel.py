from db import connection_pool
from ErrorHandler import raise_custom_error

def get_mrts():
    try:
        query_mrt_count = ("SELECT mrt, COUNT(id) AS mrt_count "
                            "FROM data "
                            "GROUP BY mrt "
                            "ORDER BY mrt_count DESC;")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(query_mrt_count)
        return cursor.fetchall()
    except Exception:
        raise_custom_error(500, "Internal Server Error")
    finally:
        connection.close()