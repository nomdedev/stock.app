import unittest
from unittest.mock import Mock
from modules.auditoria.model import AuditoriaModel

class MockDBConnection:
    def __init__(self):
        self.auditorias = []
        self.last_id = 1
        self.last_query = None
        self.last_params = None
    def ejecutar_query(self, query, params=None, *args, **kwargs):
        self.last_query = query
        self.last_params = params
        if "INSERT INTO auditorias_sistema" in query:
            # (modulo_afectado, tipo_evento, detalle, ip_origen)
            # Asegurar que params nunca sea None
            safe_params = tuple(params) if params is not None else ()
            auditoria = (self.last_id,) + safe_params
            self.auditorias.append(auditoria)
            self.last_id += 1
            return []
        if "SELECT * FROM auditorias_sistema" in query:
            if params:
                # Mejorar parsing de WHERE para soportar espacios y mayúsculas
                import re
                # Buscar todos los campos de la cláusula WHERE (soporta varios)
                matches = re.findall(r"([a-zA-Z_]+)\s*=\s*\?", query, re.IGNORECASE)
                if matches:
                    campo_indices = {
                        "modulo_afectado": 1,
                        "tipo_evento": 2,
                        "detalle": 3,
                        "ip_origen": 4
                    }
                    # Filtrar por todos los campos encontrados
                    resultados = self.auditorias
                    for i, campo in enumerate(matches):
                        idx = campo_indices.get(campo.lower(), 1)
                        valor = params[i] if i < len(params) else None
                        resultados = [a for a in resultados if a[idx] == valor]
                    return resultados
                # Si no hay WHERE válido, devolver todo
                return list(self.auditorias)
            return list(self.auditorias)
        return []

class MockAuditoriaView:
    def __init__(self):
        self.tabla_data = []
        self.label = Mock()
    def actualizar_tabla(self, data):
        self.tabla_data = data

class TestAuditoriaIntegracion(unittest.TestCase):
    def setUp(self):
        self.mock_db = MockDBConnection()
        self.model = AuditoriaModel(self.mock_db)
        self.view = MockAuditoriaView()
    def tearDown(self):
        self.mock_db.auditorias.clear()
    def test_registrar_y_reflejar_evento(self):
        self.model.db.ejecutar_query("INSERT INTO auditorias_sistema (modulo_afectado, tipo_evento, detalle, ip_origen) VALUES (?, ?, ?, ?)", ("usuarios", "inserción", "Usuario creado", "192.168.1.1"))
        auditorias = self.mock_db.ejecutar_query("SELECT * FROM auditorias_sistema")
        self.assertTrue(any(a[1] == "usuarios" for a in auditorias))
        self.view.actualizar_tabla(auditorias)
        self.assertEqual(self.view.tabla_data, auditorias)
    def test_filtrar_por_modulo(self):
        self.model.db.ejecutar_query("INSERT INTO auditorias_sistema (modulo_afectado, tipo_evento, detalle, ip_origen) VALUES (?, ?, ?, ?)", ("inventario", "modificación", "Stock ajustado", "192.168.1.2"))
        auditorias = self.mock_db.ejecutar_query("SELECT * FROM auditorias_sistema WHERE modulo_afectado = ?", ("inventario",))
        self.assertTrue(all(a[1] == "inventario" for a in auditorias))
        self.view.actualizar_tabla(auditorias)
        self.assertEqual(self.view.tabla_data, auditorias)

if __name__ == "__main__":
    unittest.main()
