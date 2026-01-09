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

def create_booking_table():
    db_name = os.getenv('DB_DATABASE')
    server_con = get_server_connection()
    server_cursor = server_con.cursor()
    server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    server_con.close()
    
    con = get_db_connection()
    cursor = con.cursor()
    
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS booking (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        user_id BIGINT NOT NULL UNIQUE,
        attraction_id INT NOT NULL,
        date DATE NOT NULL,
        time VARCHAR(255) NOT NULL,
        price INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (attraction_id) REFERENCES attractions(id)
    );
    """
    cursor.execute(create_table_sql)
    con.commit()
    
    cursor.close()
    con.close()

if __name__ == "__main__":
    print("Starting to create booking table.")
    create_booking_table()
    print("Table 'booking' created successfully.")