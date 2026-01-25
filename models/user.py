from models.database import get_db_connection

def create_user(name, email, password):
    """建立新使用者"""
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    
    try:
        # 檢查 Email 是否重複
        check_sql = "SELECT id FROM user WHERE email=%s"
        cursor.execute(check_sql, (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return None  # Email 已存在
        
        # 建立使用者
        insert_sql = "INSERT INTO user(name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (name, email, password))
        con.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Database Error: {e}")
        return None
    finally:
        cursor.close()
        con.close()

def authenticate_user(email, password):
    """驗證使用者登入"""
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    
    try:
        sql = "SELECT id, name, email FROM user WHERE email=%s AND password=%s"
        cursor.execute(sql, (email, password))
        return cursor.fetchone()
    except Exception as e:
        print(f"Database Error: {e}")
        return None
    finally:
        cursor.close()
        con.close()