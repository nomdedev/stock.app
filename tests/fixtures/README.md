# Fixtures de tests

Esta carpeta contiene todos los datos de prueba reutilizables (fixtures) para los tests unitarios y de integración del proyecto.

## ¿Qué es un fixture?
Un fixture es un archivo (JSON, CSV, SQL, etc.) que contiene datos de ejemplo o configuraciones necesarias para ejecutar tests de manera consistente y repetible, sin depender de datos reales ni del entorno de producción.

## Convenciones de uso
- Todos los datos de prueba deben estar aquí, organizados por módulo si es necesario (por ejemplo: `obras.json`, `inventario.csv`, etc.).
- Los tests deben cargar los datos desde esta carpeta usando rutas relativas.
- No incluir datos sensibles ni credenciales reales.
- Si un test requiere un fixture nuevo, créalo aquí y documenta su propósito en este README.

## Ejemplo de uso en un test (pytest):
```python
import json
from pathlib import Path

def test_algo():
    fixture_path = Path(__file__).parent / 'fixtures' / 'obras.json'
    with open(fixture_path) as f:
        data = json.load(f)
    # Usar data en el test...
```

## Tipos de archivos permitidos
- `.json`, `.csv`, `.sql`, `.xlsx`, `.yml`, etc.

## Buenas prácticas
- Mantén los fixtures pequeños y representativos.
- Si un fixture queda obsoleto, elimínalo.
- Documenta cualquier convención especial aquí.
