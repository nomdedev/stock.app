from core.database import DatabaseConnection

class MaterialModel:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection

    def crear_tabla_materiales(self):
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='materiales' AND xtype='U')
        CREATE TABLE materiales (
            id INT IDENTITY(1,1) PRIMARY KEY,
            codigo VARCHAR(50) NOT NULL,
            descripcion VARCHAR(255),
            cantidad INT NOT NULL,
            ubicacion VARCHAR(100),
            fecha_ingreso DATETIME DEFAULT GETDATE(),
            observaciones TEXT
        );
        """
        self.db.ejecutar_query(query)

    def agregar_material(self, codigo, descripcion, cantidad, ubicacion, observaciones):
        query = """
        INSERT INTO materiales (codigo, descripcion, cantidad, ubicacion, observaciones)
        VALUES (?, ?, ?, ?, ?);
        """
        self.db.ejecutar_query(query, (codigo, descripcion, cantidad, ubicacion, observaciones))

    def obtener_materiales(self):
        query = "SELECT * FROM materiales;"
        return self.db.ejecutar_query(query)

    def actualizar_material(self, id_material, codigo, descripcion, cantidad, ubicacion, observaciones):
        query = """
        UPDATE materiales
        SET codigo = ?, descripcion = ?, cantidad = ?, ubicacion = ?, observaciones = ?
        WHERE id = ?;
        """
        self.db.ejecutar_query(query, (codigo, descripcion, cantidad, ubicacion, observaciones, id_material))

    def eliminar_material(self, id_material):
        query = "DELETE FROM materiales WHERE id = ?;"
        self.db.ejecutar_query(query, (id_material,))
