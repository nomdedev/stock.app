# Estándares de Logging

- Todos los módulos deben registrar eventos usando `core.logger.Logger`.
- Los errores críticos se registran con `log_error` y se muestran al usuario con feedback.
- Los logs se guardan en archivos rotados en `logs/` en formato de texto y JSON.
