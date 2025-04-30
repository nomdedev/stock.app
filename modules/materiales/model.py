class MaterialesModel:
    def __init__(self, db_connection):
        self.db = InventarioDatabaseConnection()

    def obtener_materiales(self):
        query = "SELECT * FROM materiales"
        return self.db.ejecutar_query(query)

    def agregar_material(self, datos):
        query = "INSERT INTO materiales (nombre, cantidad, proveedor) VALUES (?, ?, ?)"
        self.db.ejecutar_query(query, datos)
