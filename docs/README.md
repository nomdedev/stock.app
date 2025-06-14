# Índice de documentación y estándares

Este índice centraliza el acceso a todos los documentos clave del proyecto. Consulta cada estándar antes de modificar o agregar código.

## Estándares y guías
- [Estándares visuales](estandares_visuales.md)
- [Estándares de logging y feedback visual](estandares_logging.md)
- [Formato y rotación de logs (JSON y texto)](estandares_logging.md#formato-json-y-rotacion)
- [Estándares de seguridad y manejo de datos sensibles](estandares_seguridad.md)
- [Estándares de feedback visual y procedimientos de carga](estandares_feedback.md)
- [Estándares de auditoría y registro de acciones](estandares_auditoria.md)

## Flujos y buenas prácticas
- [Flujo de integración Obras/Material/Vidrios](flujo_obras_material_vidrios.md)
- [Buenas prácticas en configuraciones críticas](buenas_practicas_configuraciones_criticas.md)
- [Errores frecuentes en login y soluciones](errores_frecuentes_login.md)
- [Decisiones de diseño en main.py](decisiones_main.md)
- [Pendientes de tests y controladores](pendientes_tests_y_controladores.md)
- [Bloqueo de tests UI y motivos](bloqueo_tests_ui.md)

## Auditoría y reportes
- [Auditoría y reportes](auditoria/README.md)

## Organización de recursos y estructura del proyecto

- **QSS:** Todos los archivos de estilos están en `resources/qss/`.
- **Íconos:** Todos los íconos SVG y PNG están en `resources/icons/`.
- **Scripts de base de datos:** Centralizados en `scripts/db/`.
- **PDFs y Excels de auditoría:** En `docs/auditoria/`.
- **Estructura de tablas por módulo:** [Estructura de tablas](estructura_tablas_por_modulo.md).
- **Tests:** Subcarpetas por módulo en `tests/` y datos de prueba en `tests/fixtures/`.

Consulta el README principal para detalles y convenciones de cada carpeta.

---

## Conexión robusta a base de datos: timeout y reintentos

La conexión a la base de datos implementa:
- **Timeout configurable:** El tiempo máximo de espera para conectar se define por variable de entorno (`DB_TIMEOUT`) o parámetro.
- **Reintentos automáticos:** Si la conexión falla, se reintenta hasta `DB_MAX_RETRIES` veces (por defecto 3), con backoff exponencial.
- **Logging detallado:** Cada intento y error se registra en los logs para trazabilidad y diagnóstico.

**Justificación:**
- Mejora la resiliencia ante caídas temporales de red o base de datos.
- Evita fallos inmediatos por problemas transitorios.
- Permite ajustar el comportamiento según el entorno (desarrollo, producción, CI).
- Facilita el monitoreo y la auditoría de problemas de conectividad.

**Convención:** Usa siempre la clase `BaseDatabaseConnection` o sus derivadas para aprovechar este mecanismo. No implementes reintentos manuales en los módulos.

---

**Convención:** Si agregas un nuevo estándar, guía o flujo, enlázalo aquí y describe brevemente su propósito.

Última actualización: 1 de junio de 2025
