# TEST OPTIMISTIC LOCK: conflicto concurrente
import pytest
from modules.obras.model import ObrasModel, OptimisticLockError
from core.database import ObrasDatabaseConnection
import pyodbc

def test_editar_obra_conflicto_rowversion(monkeypatch):
    """
    Prueba el bloqueo optimista: si la rowversion cambia, debe lanzar OptimisticLockError.
    1. Inserta una obra y obtiene su rowversion.
    2. Simula un cambio externo (UPDATE directo).
    3. Intenta editar con la rowversion antigua → debe fallar.
    """
    # Setup: conexión real o mock
    db = ObrasDatabaseConnection()
    model = ObrasModel(db)
    # Insertar obra de prueba
    query_insert = """
    INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) OUTPUT INSERTED.id, INSERTED.rowversion
    VALUES (?, ?, ?, GETDATE(), GETDATE())
    """
    nombre = "Obra Test Optimistic"
    cliente = "Cliente Test"
    estado = "En curso"
    with db.connection.cursor() as cursor:
        cursor.execute(query_insert, (nombre, cliente, estado))
        row = cursor.fetchone()
        id_obra = row[0]
        rowversion_orig = row[1]
    # Simular cambio externo
    query_update = "UPDATE obras SET estado = ? WHERE id = ?"
    with db.connection.cursor() as cursor:
        cursor.execute(query_update, ("Finalizada", id_obra))
        db.connection.commit()
    # Intentar editar con rowversion antigua
    datos = {"estado": "Cancelada"}
    with pytest.raises(OptimisticLockError):
        model.editar_obra(id_obra, datos, rowversion_orig)
    # Limpiar
    db.ejecutar_query(f"DELETE FROM obras WHERE id = ?", (id_obra,))
