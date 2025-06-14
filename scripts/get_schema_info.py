\
import sys
import os
import json

# Añadir el directorio raíz del proyecto al PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Las importaciones de core.database y core.config se harán dentro de la clase/funciones
# para asegurar que el PYTHONPATH se haya actualizado primero.

class DatabaseSchemaInfo:
    def __init__(self):
        # Importar aquí para asegurar que PYTHONPATH esté configurado
        from core.database import BaseDatabaseConnection, InventarioDatabaseConnection, UsuariosDatabaseConnection, AuditoriaDatabaseConnection
        self.base_database_connection = BaseDatabaseConnection
        self.inventario_database_connection = InventarioDatabaseConnection
        self.usuarios_database_connection = UsuariosDatabaseConnection
        self.auditoria_database_connection = AuditoriaDatabaseConnection
        self.db_conn = None

    def _get_db_connection(self, db_name):
        if db_name == "inventario":
            return self.inventario_database_connection()
        elif db_name == "users":
            return self.usuarios_database_connection()
        elif db_name == "auditoria":
            return self.auditoria_database_connection()
        else:
            # Para bases de datos no mapeadas explícitamente, usamos base_database_connection
            return self.base_database_connection(database=db_name)

    def get_schema(self, db_name):
        schema = {"tablas": {}}
        error_message = None
        try:
            self.db_conn = self._get_db_connection(db_name)
            self.db_conn.conectar() # Asegura que la conexión esté activa

            if not self.db_conn.connection:
                error_message = f"Error: No se pudo establecer conexión con la base de datos {db_name}."
                # No imprimir aquí, retornar el error para que el llamador decida
                return schema, error_message

            cursor = self.db_conn.connection.cursor()
            query_tablas = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = ?"
            cursor.execute(query_tablas, db_name)
            tablas = cursor.fetchall()

            for (tabla_nombre,) in tablas:
                schema["tablas"][tabla_nombre] = {"columnas": {}}
                query_columnas = "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_CATALOG = ? AND TABLE_NAME = ? ORDER BY ORDINAL_POSITION"
                cursor.execute(query_columnas, db_name, tabla_nombre)
                columnas_data = cursor.fetchall()
                for col_row in columnas_data:
                    schema["tablas"][tabla_nombre]["columnas"][col_row.COLUMN_NAME] = {
                        "tipo": col_row.DATA_TYPE,
                        "nullable": col_row.IS_NULLABLE,
                        "default": col_row.COLUMN_DEFAULT
                    }
            
        except Exception as e:
            error_message = f"Error obteniendo esquema para BD {db_name}: {str(e)}"
        finally:
            if self.db_conn and self.db_conn.connection:
                self.db_conn.cerrar_conexion()
        
        return schema, error_message

if __name__ == "__main__":
    if len(sys.argv) > 1:
        db_name_arg = sys.argv[1]
        try:
            # Importar aquí para asegurar que PYTHONPATH esté configurado
            # from core.config import DB_SERVER, DB_USERNAME, DB_PASSWORD # No son necesarias aquí directamente
            
            schema_info = DatabaseSchemaInfo()
            schema_data, error = schema_info.get_schema(db_name_arg)
            
            if error:
                # Imprimir el error como JSON si ocurrió uno
                print(json.dumps({"error": error, "tablas_parciales": schema_data.get("tablas", {})}, indent=4))
            else:
                # Imprimir el esquema completo si no hubo errores
                print(json.dumps(schema_data, indent=4))

        except ImportError as ie:
            print(json.dumps({"error": f"ImportError: No se pudo importar un módulo necesario. Asegúrate que el script está en 'scripts' y PYTHONPATH está bien. Detalles: {str(ie)}"}, indent=4))
        except Exception as e:
            print(json.dumps({"error": f"Error inesperado en __main__: {str(e)}"}, indent=4))
    else:
        print(json.dumps({"error": "Por favor, proporciona el nombre de la base de datos como argumento (ej: users, inventario, auditoria)."}, indent=4))

