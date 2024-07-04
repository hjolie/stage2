from db import connection_pool
from ErrorHandler import raise_custom_error

def create_order_data(order_number, user_id, attraction_id, attraction_name, attraction_date, attraction_time, price, name, email, phone):
    try:
        create_new_order = ("INSERT INTO order_data "
                        "(order_number, user_id, attraction_id, attraction_name, attraction_date, attraction_time, price, name, email, phone) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        new_order_data = (order_number, user_id, attraction_id, attraction_name, attraction_date, attraction_time, price, name, email, phone)
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(create_new_order, new_order_data)
        connection.commit()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Creating New Order")
    finally:
        connection.close()

def get_order_id(order_number):
    try:
        get_order_id = ("SELECT id from order_data "
                        "WHERE order_number = %s")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(get_order_id, (order_number,))
        result = cursor.fetchone()
        return result
    except Exception:
        raise_custom_error(500, "Internal Server Error - Getting Order ID")
    finally:
        connection.close()

def save_payment_success(order_id, status, msg, amount, acquirer, currency, rec_trade_id, bank_transaction_id, auth_code, last_four, bin_code, transaction_time_millis, card_identifier, merchant_id):
    try:
        save_payment = ("INSERT INTO payment "
                        "(order_id, status, msg, amount, acquirer, currency, rec_trade_id, bank_transaction_id, auth_code, last_four, bin_code, transaction_time_millis, card_identifier, merchant_id) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        payment_data = (order_id, status, msg, amount, acquirer, currency, rec_trade_id, bank_transaction_id, auth_code, last_four, bin_code, transaction_time_millis, card_identifier, merchant_id)
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(save_payment, payment_data)
        connection.commit()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Saving Payment Data")
    finally:
        connection.close()

def save_payment_failed(order_id, status, msg, rec_trade_id, merchant_id):
    try:
        save_payment = ("INSERT INTO payment "
                        "(order_id, status, msg, rec_trade_id, merchant_id) "
                        "VALUES (%s, %s, %s, %s, %s)")
        payment_data = (order_id, status, msg, rec_trade_id, merchant_id)
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(save_payment, payment_data)
        connection.commit()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Saving Payment Failed Data")
    finally:
        connection.close()

def update_order_status(order_id):
    try:
        update_status = ("UPDATE order_data "
                         "SET status = 'paid' "
                         "WHERE id = %s")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(update_status, (order_id,))
        connection.commit()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Updating Order Status")
    finally:
        connection.close()

def delete_booking_page_data(user_id):
    try:
        delete_booking = ("DELETE FROM booking "
                    "WHERE user_id = %s")
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(delete_booking, (user_id,))
        connection.commit()
    except Exception:
        raise_custom_error(500, "Internal Server Error - Deleting Booking Page Data")
    finally:
        connection.close()