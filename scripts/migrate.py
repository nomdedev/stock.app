import os
import glob
import sqlite3  # Cambia a pyodbc o el driver que uses para SQL Server

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'db')
DB_PATH = os.environ.get('DB_PATH', 'inventario.db')  # Ajusta según tu config

# Para SQL Server, reemplaza por pyodbc y la cadena de conexión centralizada

def run_migrations():
    sql_files = sorted(glob.glob(os.path.join(MIGRATIONS_DIR, '*.sql')))
    if not sql_files:
        print('No se encontraron scripts de migración.')
        return
    # Ejemplo para SQLite. Para SQL Server, usa pyodbc.connect(...)
    conn = sqlite3.connect(DB_PATH)
    try:
        for sql_file in sql_files:
            with open(sql_file, encoding='utf-8') as f:
                sql = f.read()
            print(f'Ejecutando migración: {os.path.basename(sql_file)}')
            conn.executescript(sql)
        conn.commit()
        print('Migraciones aplicadas correctamente.')
    finally:
        conn.close()

if __name__ == '__main__':
    run_migrations()
