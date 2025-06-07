# Cobertura de tests y ejecución

Actualmente la cobertura total de código es baja (~11%).

## Cómo ejecutar los tests y ver cobertura

1. Instala las dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
2. Ejecuta todos los tests y muestra la cobertura:
   ```powershell
   pytest tests/ --disable-warnings --cov=modules --cov-report=term-missing
   ```

## Mejorar cobertura
- Revisa los archivos de tests en `tests/` y los reportes de cobertura para identificar módulos con baja cobertura.
- Agrega tests unitarios y de integración para los métodos críticos de cada controlador y modelo.

## Estado actual
- Los tests unitarios y de integración para los controladores principales están presentes, pero la cobertura es baja porque la mayoría del código en los módulos `view.py` y `model.py` no está cubierto.
- Se recomienda priorizar tests para lógica de negocio y controladores.

---

**Cobertura actual:**

![Cobertura](https://img.shields.io/badge/coverage-11%25-red)

> Actualiza este badge manualmente tras cada ejecución de tests.
