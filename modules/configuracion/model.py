from core.database import ConfiguracionDatabaseConnection  # Importar la clase correcta

class ConfiguracionModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_configuracion(self):
        query = "SELECT clave, valor, descripcion FROM configuracion_sistema"
        result = self.db.ejecutar_query(query)
        return result if result is not None else []

    def actualizar_configuracion(self, clave, valor):
        query = "UPDATE configuracion_sistema SET valor = ? WHERE clave = ?"
        self.db.ejecutar_query(query, (valor, clave))

    def obtener_apariencia_usuario(self, usuario_id):
        query = "SELECT modo_color, idioma_preferido, mostrar_notificaciones, tamaño_fuente FROM apariencia_usuario WHERE usuario_id = ?"
        return self.db.ejecutar_query(query, (usuario_id,))

    def actualizar_apariencia_usuario(self, usuario_id, datos):
        query = """
        UPDATE apariencia_usuario
        SET modo_color = ?, idioma_preferido = ?, mostrar_notificaciones = ?, tamaño_fuente = ?
        WHERE usuario_id = ?
        """
        self.db.ejecutar_query(query, (*datos, usuario_id))

    def guardar_configuracion_conexion(self, datos):
        query = """
        UPDATE configuracion_sistema
        SET valor = ?
        WHERE clave = ?
        """
        for clave, valor in datos.items():
            self.db.ejecutar_query(query, (valor, clave))

    def activar_modo_offline(self):
        query = "UPDATE configuracion_sistema SET valor = 'True' WHERE clave = 'modo_offline'"
        self.db.ejecutar_query(query)

    def desactivar_modo_offline(self):
        query = "UPDATE configuracion_sistema SET valor = 'False' WHERE clave = 'modo_offline'"
        self.db.ejecutar_query(query)

    def obtener_estado_notificaciones(self):
        query = "SELECT valor FROM configuracion_sistema WHERE clave = 'notificaciones_activas'"
        resultado = self.db.ejecutar_query(query)
        return resultado[0][0] == "True" if resultado else False

    def actualizar_estado_notificaciones(self, estado):
        query = "UPDATE configuracion_sistema SET valor = ? WHERE clave = 'notificaciones_activas'"
        self.db.ejecutar_query(query, ("True" if estado else "False",))
