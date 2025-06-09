# Test de integración: requiere base de datos real y soporte de rowversion
# Ejecutar solo en entorno preparado para integración
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
    db = ObrasDatabaseConnection()
    model = ObrasModel(db)
    query_insert = (
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) OUTPUT INSERTED.id, INSERTED.rowversion "
        "VALUES (?, ?, ?, GETDATE(), GETDATE())"
    )
    nombre = "Obra Test Optimistic"
    cliente = "Cliente Test"
    estado = "En curso"
    id_obra = None
    try:
        # Validar que la conexión está activa
        if not hasattr(db, 'connection') or db.connection is None:
            pytest.skip("No hay conexión activa a la base de datos. Test de integración omitido.")
        with db.connection.cursor() as cursor:
            cursor.execute(query_insert, (nombre, cliente, estado))
            row = cursor.fetchone()
            assert row is not None, "No se pudo insertar la obra de prueba. Verifica la base de datos y los permisos."
            id_obra = row[0]
            rowversion_orig = row[1]
        # Simular cambio externo
        query_update = "UPDATE obras SET estado = ? WHERE id = ?"
        with db.connection.cursor() as cursor:
            cursor.execute(query_update, ("Finalizada", id_obra))
            if hasattr(db.connection, 'commit'):
                db.connection.commit()
        # (Opcional) Verificar que la rowversion cambió realmente
        with db.connection.cursor() as cursor:
            cursor.execute("SELECT rowversion FROM obras WHERE id = ?", (id_obra,))
            row = cursor.fetchone()
            assert row is not None, "No se encontró la obra luego del update."
            rowversion_nueva = row[0]
            assert rowversion_nueva != rowversion_orig, "La rowversion no cambió tras el update externo."
        datos = {"estado": "Cancelada"}
        # El test debe fallar si no se lanza la excepción
        with pytest.raises(OptimisticLockError):
            model.editar_obra(id_obra, datos, rowversion_orig)
    finally:
        # Limpieza: eliminar la obra de prueba si fue insertada
        if id_obra is not None:
            try:
                db.ejecutar_query(f"DELETE FROM obras WHERE id = ?", (id_obra,))
            except Exception:
                pass  # No interrumpir el test por error en cleanup
