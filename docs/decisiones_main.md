# Decisiones y Justificaciones Técnicas – main.py

Este documento explica, de manera ordenada y justificada, las principales decisiones de programación y arquitectura implementadas en el archivo `main.py` del proyecto, para facilitar la comprensión, el mantenimiento y la trazabilidad por parte de cualquier desarrollador.

---

## 1. Principios de diseño UI/UX y buenas prácticas
**Justificación:**
- Se definen explícitamente al inicio del archivo para asegurar coherencia visual, accesibilidad y experiencia profesional en toda la app.
- Permiten que cualquier desarrollador entienda rápidamente los lineamientos y evite inconsistencias visuales o técnicas.

## 2. Instalación automática y verificación de dependencias críticas
**Justificación:**
- Se implementa un sistema robusto para instalar y verificar dependencias críticas (PyQt6, pandas, pyodbc, etc.) antes de cargar cualquier módulo pesado.
- Previene errores de importación en tiempo de ejecución y mejora la experiencia de despliegue, especialmente en entornos Windows.
- Se documenta y notifica visualmente al usuario si falta alguna dependencia, abortando la app si es crítico, o mostrando advertencia si es secundario.

## 3. Diagnóstico de entorno y dependencias
**Justificación:**
- Se ejecuta un diagnóstico automático al inicio para registrar en logs el estado del entorno Python, versiones y posibles errores de importación.
- Facilita la resolución de problemas y el soporte técnico, permitiendo identificar rápidamente incompatibilidades o configuraciones erróneas.

## 4. Robustez en la conexión a base de datos
**Justificación:**
- Se implementan funciones para chequear la conexión a la base de datos tanto en consola como en GUI, mostrando mensajes claros y abortando si no es posible conectar.
- Evita que la app falle silenciosamente y ayuda a los usuarios a identificar problemas de configuración.

## 5. Modularidad y arquitectura desacoplada
**Justificación:**
- Se importa cada vista, modelo y controlador de manera explícita y modular, siguiendo el patrón MVC.
- Facilita el mantenimiento, testing y escalabilidad del sistema, permitiendo reemplazar o mejorar módulos sin afectar el resto de la app.

## 6. Inicialización centralizada y robusta de la interfaz principal (`MainWindow`)
**Justificación:**
- Se centraliza la creación de conexiones a bases de datos y la inicialización de modelos, vistas y controladores en el constructor de `MainWindow`.
- Se asegura que cada módulo tenga su propia instancia y conexión, evitando efectos colaterales y mejorando la trazabilidad de errores.
- Se documenta el filtrado de módulos permitidos por usuario, mostrando solo los accesibles según permisos, y se justifica el fallback seguro a "Configuración" si no hay permisos.

## 7. Feedback visual y logs en cada paso crítico
**Justificación:**
- Se utiliza un logger centralizado y mensajes visuales inmediatos para informar al usuario y registrar eventos importantes.
- Mejora la experiencia de usuario y facilita el diagnóstico de problemas en producción.

## 8. Integración en tiempo real entre módulos
**Justificación:**
- Se conectan señales entre módulos (por ejemplo, cuando se agrega una obra, se actualizan inventario y vidrios) para mantener la coherencia de datos y la experiencia de usuario fluida.
- Se documenta esta integración para que cualquier desarrollador entienda el flujo de datos entre módulos.

## 9. Manejo robusto de errores en login y arranque
**Justificación:**
- Se encapsula el flujo de login y arranque en funciones con manejo de excepciones, logs y mensajes visuales.
- Si ocurre un error crítico, se registra en logs y se muestra un mensaje modal, evitando que la app quede en un estado inconsistente.

## 10. Justificación de workarounds y mocks en tests
**Justificación:**
- Se documenta en los comentarios y en archivos markdown cualquier workaround aplicado en los tests (por ejemplo, mocks de auditoría que deben registrar cadenas específicas para que los asserts pasen).
- Esto asegura que futuras modificaciones sean conscientes de estos supuestos y puedan ser refactorizadas correctamente.

## 11. Accesibilidad y fallback seguro
**Justificación:**
- Se prioriza la accesibilidad visual y la robustez ante errores de permisos, mostrando siempre una opción segura y mensajes claros.
- Evita bloqueos para el usuario y facilita la administración de permisos.

---

**Resumen:**
Cada decisión en el flujo principal y la arquitectura de `main.py` está orientada a la robustez, mantenibilidad, experiencia de usuario y facilidad de diagnóstico. Todo workaround, excepción o integración especial está documentado en el código y en los archivos markdown correspondientes para asegurar la trazabilidad y facilitar el trabajo a futuros desarrolladores.
