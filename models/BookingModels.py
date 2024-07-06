from db import connection_pool
from ErrorHandler import raise_custom_error

# POST /api/booking
def find_booking(user_id):
    try:
        find_booking = ("SELECT id FROM booking "
                "WHERE user_id = %s")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(find_booking, (user_id,))
        return cursor.fetchall()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Finding Booking")
    finally:
        connection.close()

def delete_booking(id):
    try:
        delete_attraction = ("DELETE FROM booking "
                    "WHERE id = %s")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(delete_attraction, (id,))
        connection.commit()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Deleting Existing Booking")
    finally:
        connection.close()

def create_booking(user_id, attractionId, date, time, price):
    try:
        save_attraction = ("INSERT INTO booking "
                        "(user_id, attraction_id, date, time, price) "
                        "VALUES (%s, %s, %s, %s, %s)")
        booking_data = (user_id, attractionId, date, time, price)
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(save_attraction, booking_data)
        connection.commit()
        return {"ok": True}
    except Exception:
        raise_custom_error(500, "Internal Server Error - Saving Booking")
    finally:
        connection.close()

# GET /api/booking
def get_booking(user_id):
    try:
        find_booking = ("SELECT attraction_id, date, time, price FROM booking "
                "WHERE user_id = %s")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(find_booking, (user_id,))
        return cursor.fetchall()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Finding Booking")
    finally:
        connection.close()

def get_attraction(attraction_id):
    try:
        find_attraction = ("SELECT name, address, images FROM data "
                "WHERE id = %s")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(find_attraction, (attraction_id,))
        return cursor.fetchall()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Finding Attraction")
    finally:
        connection.close()

# DELETE /api/booking
def delete_booking(user_id):
    try:
        delete_booking = ("DELETE FROM booking "
                "WHERE user_id = %s")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(delete_booking, (user_id,))
        connection.commit()
        return {"ok": True}
    except Exception:
        raise_custom_error(500, "Internal Server Error - Deleting Booking")
    finally:
        connection.close()