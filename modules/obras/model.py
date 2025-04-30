import pandas as pd
from fpdf import FPDF
from core.database import ObrasDatabaseConnection  # Importar la clase correcta

class ObrasDatabaseConnection:
    def ejecutar_query(self, query, params=None):
        # Implementación de la conexión específica a la base de datos de obras
        pass

class ObrasModel:
    def __init__(self, db_connection=None):
        self.db = db_connection or ObrasDatabaseConnection()  # Usar ObrasDatabaseConnection

    def obtener_obras(self):
        query = "SELECT * FROM obras"
        return self.db.ejecutar_query(query)

    def agregar_obra(self, datos):
        query = "INSERT INTO obras (nombre, cliente, estado) VALUES (?, ?, ?)"
        self.db.ejecutar_query(query, datos)

    def obtener_cronograma_por_obra(self, id_obra):
        query = "SELECT * FROM cronograma_obras WHERE id_obra = ?"
        return self.db.ejecutar_query(query, (id_obra,))

    def agregar_etapa_cronograma(self, datos):
        query = """
        INSERT INTO cronograma_obras (id_obra, etapa, fecha_programada, fecha_realizada, observaciones, responsable, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def actualizar_estado_obra(self, id_obra, nuevo_estado):
        query = "UPDATE obras SET estado_general = ? WHERE id = ?"
        self.db.ejecutar_query(query, (nuevo_estado, id_obra))

    def obtener_materiales_por_obra(self, id_obra):
        query = "SELECT * FROM materiales_por_obra WHERE id_obra = ?"
        return self.db.ejecutar_query(query, (id_obra,))

    def asignar_material_a_obra(self, datos):
        query = """
        INSERT INTO materiales_por_obra (id_obra, id_item, cantidad_necesaria, cantidad_reservada, estado)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def exportar_cronograma(self, formato, id_obra):
        query = """
        SELECT etapa, fecha_programada, fecha_realizada, estado, responsable
        FROM cronograma_obras
        WHERE id_obra = ?
        """
        datos = self.db.ejecutar_query(query, (id_obra,))

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
        self.db.ejecutar_query(query, (id_etapa,))

    def obtener_estadisticas_obras(self):
        query = """
        SELECT estado_general, COUNT(*) as total
        FROM obras
        GROUP BY estado_general
        """
        return self.db.ejecutar_query(query)
