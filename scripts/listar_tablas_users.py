import pyodbc
from core.database import get_connection_string, BaseDatabaseConnection

def main():
    driver = BaseDatabaseConnection.detectar_driver_odbc()
    conn_str = get_connection_string(driver, 'users')
    try:
        with pyodbc.connect(conn_str, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES')
            tablas = [row[0] for row in cursor.fetchall()]
            print('Tablas en la base de datos users:')
            for t in tablas:
                print(f'- {t}')
    except Exception as e:
        print(f'Error al listar tablas: {e}')

if __name__ == '__main__':
    main()
