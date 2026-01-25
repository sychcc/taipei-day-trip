from models.database import get_db_connection

def create_booking(user_id, attraction_id, date, time, price):
    """建立預訂"""
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    
    sql = """
    INSERT INTO booking(user_id, attraction_id, date, time, price)
    VALUES(%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        attraction_id=VALUES(attraction_id),
        date = VALUES(date),
        time = VALUES(time),
        price = VALUES(price);
    """
    params = [user_id, attraction_id, date, time, price]
    
    try:
        cursor.execute(sql, params)
        con.commit()
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False
    finally:
        cursor.close()
        con.close()

def get_booking_by_user(user_id):
    """取得使用者的預訂"""
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    
    sql = """
    SELECT 
        b.attraction_id, b.date, b.time, b.price,
        a.name, a.address, a.file
    FROM booking AS b
    INNER JOIN attractions AS a
    ON b.attraction_id=a.id
    WHERE b.user_id=%s
    """
    
    try:
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Database Error: {e}")
        return None
    finally:
        cursor.close()
        con.close()

def delete_booking_by_user(user_id):
    """刪除使用者的預訂"""
    con = get_db_connection()
    cursor = con.cursor()
    
    sql = 'DELETE FROM booking WHERE user_id=%s'
    
    try:
        cursor.execute(sql, (user_id,))
        con.commit()
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False
    finally:
        cursor.close()
        con.close()