class VidriosModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_vidrios(self):
        query = "SELECT * FROM vidrios"
        return self.db.ejecutar_query(query)

    def agregar_vidrio(self, datos):
        query = """
        INSERT INTO vidrios (tipo, ancho, alto, cantidad, proveedor, fecha_entrega)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def asignar_a_obra(self, id_vidrio, id_obra):
        query = """
        INSERT INTO vidrios_obras (id_vidrio, id_obra)
        VALUES (?, ?)
        """
        self.db.ejecutar_query(query, (id_vidrio, id_obra))
