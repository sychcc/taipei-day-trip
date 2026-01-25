
import mysql.connector.pooling
import os
from dotenv import load_dotenv

load_dotenv()

# 資料庫設定
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}

# 建立連線池
db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    **db_config
)

def get_db_connection():
    """從連線池取得資料庫連線"""
    return db_pool.get_connection()