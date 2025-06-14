import pyodbc
from core.database import get_connection_string, BaseDatabaseConnection

def listar_tablas(db_name, tablas_esperadas):
    driver = BaseDatabaseConnection.detectar_driver_odbc()
    conn_str = get_connection_string(driver, db_name)
    try:
        with pyodbc.connect(conn_str, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES')
            tablas = [row[0] for row in cursor.fetchall()]
            print(f'Tablas en la base de datos {db_name}:')
            for t in tablas:
                print(f'- {t}')
            
            # Comparar tablas
            tablas_faltantes = set(tablas_esperadas) - set(tablas)
            tablas_sobrantes = set(tablas) - set(tablas_esperadas)
            print(f'Tablas faltantes en {db_name}: {tablas_faltantes}')
            print(f'Tablas sobrantes en {db_name}: {tablas_sobrantes}')
    except Exception as e:
        print(f'Error al listar tablas en {db_name}: {e}')

def main():
    bases_de_datos = {
        'auditoria': ['auditorias_sistema', 'errores_sistema'],
        'users': ['usuarios'],
        'inventario': ['inventario', 'categorias', 'proveedores']
    }
    for db_name, tablas_esperadas in bases_de_datos.items():
        listar_tablas(db_name, tablas_esperadas)

if __name__ == '__main__':
    main()
