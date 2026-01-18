import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_DATABASE')
    )

def get_server_connection():
    return mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST')
    )

def create_orders_table():
    db_name = os.getenv('DB_DATABASE')
    server_con = get_server_connection()
    server_cursor = server_con.cursor()
    server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    server_con.close()
    
    con = get_db_connection()
    cursor = con.cursor()
    
    # status: 0 表示已付款，1 表示未付款
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS orders (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        number VARCHAR(255) NOT NULL UNIQUE,
        user_id BIGINT NOT NULL,
        price INT NOT NULL,
        attraction_id INT NOT NULL,
        attraction_name VARCHAR(255),
        attraction_address VARCHAR(255),
        attraction_image TEXT,
        date DATE NOT NULL,
        time VARCHAR(255) NOT NULL,
        contact_name VARCHAR(255) NOT NULL,
        contact_email VARCHAR(255) NOT NULL,
        contact_phone VARCHAR(255) NOT NULL,
        status INT NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user(id)
    );
    """
    
    try:
        cursor.execute(create_table_sql)
        con.commit()
        print("Table 'orders' created successfully.")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        cursor.close()
        con.close()
if __name__ == "__main__":
    print("Starting to create orders table.")
    create_orders_table()
    print("Table 'orders' created successfully.")