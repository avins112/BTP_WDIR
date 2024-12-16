from db import get_connection

def insert_data(data):
    conn = get_connection()
    cursor = conn.cursor()
    # Example SQL
    cursor.execute("INSERT INTO your_table (column1, column2) VALUES (?, ?)", (data['column1'], data['column2']))
    conn.commit()
    cursor.close()
    conn.close()
