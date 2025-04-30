class NotificacionesModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_notificaciones(self):
        query = "SELECT * FROM notificaciones"
        return self.db.ejecutar_query(query)

    def agregar_notificacion(self, datos):
        query = "INSERT INTO notificaciones (mensaje, fecha, tipo) VALUES (?, ?, ?)"
        self.db.ejecutar_query(query, datos)
