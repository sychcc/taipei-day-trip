from models.database import get_db_connection

def create_order(order_number, user_id, price, attraction_id, attraction_name, 
                 attraction_address, attraction_image, date, time, 
                 contact_name, contact_email, contact_phone):
    """建立訂單（未付款）"""
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    
    insert_sql = """
        INSERT INTO orders (
            number, user_id, price, attraction_id, attraction_name, 
            attraction_address, attraction_image, date, time, 
            contact_name, contact_email, contact_phone, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
    """
    
    try:
        cursor.execute(insert_sql, (
            order_number, user_id, price, 
            attraction_id, attraction_name,
            attraction_address, attraction_image,
            date, time,
            contact_name, contact_email, contact_phone
        ))
        con.commit()
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False
    finally:
        cursor.close()
        con.close()

def update_order_status(order_number, status):
    """更新訂單狀態"""
    con = get_db_connection()
    cursor = con.cursor()
    
    try:
        cursor.execute("UPDATE orders SET status = %s WHERE number = %s", (status, order_number))
        con.commit()
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False
    finally:
        cursor.close()
        con.close()

def get_order_by_number(order_number):
    """根據訂單編號取得訂單"""
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM orders WHERE number = %s", (order_number,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Database Error: {e}")
        return None
    finally:
        cursor.close()
        con.close()