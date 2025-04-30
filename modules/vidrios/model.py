class VidriosModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_vidrios(self):
        query = "SELECT * FROM vidrios"
        return self.db.ejecutar_query(query)

    def agregar_vidrio(self, datos):
        query = "INSERT INTO vidrios (tipo, dimensiones, cantidad) VALUES (?, ?, ?)"
        self.db.ejecutar_query(query, datos)
