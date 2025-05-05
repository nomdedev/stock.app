import pandas as pd
from fpdf import FPDF
from core.database import BaseDatabaseConnection  # Importar la clase base correcta

class ObrasModel:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def obtener_datos_obras(self):
        """Obtiene los datos de la tabla de obras desde la base de datos."""
        query = "SELECT id, nombre, cliente, estado, fecha FROM obras"
        return self.db_connection.ejecutar_query(query)

    def obtener_obras(self):
        query = "SELECT * FROM obras"
        return self.db_connection.ejecutar_query(query)

    def agregar_obra(self, datos):
        """Agrega una nueva obra a la base de datos."""
        query = """
            INSERT INTO obras (nombre, cliente, estado, fecha)
            VALUES (?, ?, ?, ?)
        """
        self.db_connection.ejecutar_query(query, datos)

    def verificar_obra_existente(self, nombre, cliente):
        """Verifica si ya existe una obra con el mismo nombre y cliente."""
        query = "SELECT COUNT(*) FROM obras WHERE nombre = ? AND cliente = ?"
        resultado = self.db_connection.ejecutar_query(query, (nombre, cliente))
        return resultado[0][0] > 0

    def obtener_cronograma_por_obra(self, id_obra):
        query = "SELECT * FROM cronograma_obras WHERE id_obra = ?"
        return self.db_connection.ejecutar_query(query, (id_obra,))

    def agregar_etapa_cronograma(self, datos):
        query = """
        INSERT INTO cronograma_obras (id_obra, etapa, fecha_programada, fecha_realizada, observaciones, responsable, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db_connection.ejecutar_query(query, datos)

    def actualizar_estado_obra(self, id_obra, nuevo_estado):
        query = "UPDATE obras SET estado_general = ? WHERE id = ?"
        self.db_connection.ejecutar_query(query, (nuevo_estado, id_obra))

    def obtener_materiales_por_obra(self, id_obra):
        query = "SELECT * FROM materiales_por_obra WHERE id_obra = ?"
        return self.db_connection.ejecutar_query(query, (id_obra,))

    def asignar_material_a_obra(self, datos):
        query = """
        INSERT INTO materiales_por_obra (id_obra, id_item, cantidad_necesaria, cantidad_reservada, estado)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db_connection.ejecutar_query(query, datos)

    def exportar_cronograma(self, formato, id_obra):
        query = """
        SELECT etapa, fecha_programada, fecha_realizada, estado, responsable
        FROM cronograma_obras
        WHERE id_obra = ?
        """
        datos = self.db_connection.ejecutar_query(query, (id_obra,))

        if formato == "excel":
            df = pd.DataFrame(datos, columns=["Etapa", "Fecha Programada", "Fecha Realizada", "Estado", "Responsable"])
            df.to_excel(f"cronograma_obra_{id_obra}.xlsx", index=False)
            return "Cronograma exportado a Excel."

        elif formato == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Cronograma de Obra {id_obra}", ln=True, align="C")
            for row in datos:
                pdf.cell(200, 10, txt=str(row), ln=True)
            pdf.output(f"cronograma_obra_{id_obra}.pdf")
            return "Cronograma exportado a PDF."

        return "Formato no soportado."

    def eliminar_etapa_cronograma(self, id_etapa):
        query = "DELETE FROM cronograma_obras WHERE id = ?"
        self.db_connection.ejecutar_query(query, (id_etapa,))

    def obtener_estadisticas_obras(self):
        query = """
        SELECT estado_general, COUNT(*) as total
        FROM obras
        GROUP BY estado_general
        """
        return self.db_connection.ejecutar_query(query)

    def obtener_todas_las_fechas(self):
        """Obtiene todas las fechas programadas del cronograma."""
        query = "SELECT fecha_programada FROM cronograma_obras"
        return [row[0] for row in self.db_connection.ejecutar_query(query)]
