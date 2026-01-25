from models.database import get_db_connection

def get_attractions(page, page_size, category=None, keyword=None):
    """取得景點列表"""
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    
    sql = """
        SELECT _id,name,CAT,description,address,direction,MRT,latitude,longitude,file
        FROM attractions    
    """
    params = []

    if category:
        sql += "WHERE CAT=%s"
        params.append(category)
    
    if keyword:
        if category:
            sql += "AND (name LIKE %s OR MRT LIKE %s)"
        else:
            sql += "WHERE (name LIKE %s OR MRT LIKE %s)"
        kw = f"%{keyword}%"
        params.extend([kw, kw])
    
    sql += "LIMIT %s OFFSET %s"
    params.extend([page_size, page * page_size])
    
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    except Exception as e:
        return {"error": True, "message": "server database error"}
    finally:
        cursor.close()
        con.close()

    return rows

def get_attraction_by_id(attractionId):
    """根據ID取得景點"""
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    sql = """
        SELECT _id,name,CAT,description,address,direction,MRT,latitude,longitude,file
        FROM attractions WHERE _id=%s;
    """
    params = [attractionId]

    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    except Exception as e:
        return {"error": True, "message": "server database error"}
    finally:
        cursor.close()
        con.close()
    
    return rows

def get_categories():
    """取得所有分類"""
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    sql = "SELECT DISTINCT CAT FROM attractions"
    
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except Exception as e:
        return {"error": True, "message": "server database error"}
    finally:
        cursor.close()
        con.close()

    return rows

def get_mrts():
    """取得所有捷運站"""
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT MRT, COUNT(*) AS attraction_count 
    FROM attractions WHERE MRT IS NOT NULL AND MRT !='' 
    GROUP BY MRT 
    ORDER BY attraction_count DESC
    """
    
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except Exception as e:
        return {"error": True, "message": "server database error"}
    finally:
        cursor.close()
        con.close()
    
    return rows