import os
from modules.contabilidad.model import ContabilidadModel  # Confirmar que la ruta es correcta

class MockDB:
    def ejecutar_query(self, query, params):
        # Simula una base de datos con un recibo existente
        if params[0] == 1:
            return [("2023-10-01", 101, 5000.0, "Pago de servicios", "Cliente XYZ", "firma_hash_123")]
        return []  # Simula que no se encuentra el recibo

def test_generar_recibo_pdf():
    # Configuración
    db = MockDB()
    model = ContabilidadModel(db)  # Corregido: pasar db_connection al constructor

    # Caso 1: Recibo existente
    resultado = model.generar_recibo_pdf(1)
    assert resultado == "Recibo exportado como recibo_1.pdf.", f"Error: {resultado}"
    assert os.path.exists("recibo_1.pdf"), "El archivo PDF no fue generado."
    os.remove("recibo_1.pdf")  # Limpieza

    # Caso 2: Recibo inexistente
    resultado = model.generar_recibo_pdf(999)
    assert resultado == "Recibo no encontrado.", f"Error: {resultado}"

if __name__ == "__main__":
    try:
        test_generar_recibo_pdf()
        print("Todos los tests pasaron correctamente.")
    except AssertionError as e:
        print(f"Test fallido: {e}")
