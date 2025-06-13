# Inventario de Tests por Módulo y Propósito

Fecha de actualización: 13 de junio de 2025

Esta tabla organiza todos los archivos de test según el módulo en el que actúan y su propósito principal (permisos, feedback visual, integración, accesibilidad, etc.). Mantener este inventario actualizado facilita la trazabilidad, auditoría y mantenimiento de la cobertura de tests.

| Módulo         | Archivo de Test                                         | Propósito principal                                                        |
|---------------|--------------------------------------------------------|----------------------------------------------------------------------------|
| **Usuarios**   | tests/usuarios/test_usuarios_permisos.py              | Permisos de usuario (acceso, acciones, visibilidad)                        |
|               | tests/usuarios/test_usuarios_model_init.py             | Inicialización y lógica de modelo de usuarios (incluye permisos)           |
|               | tests/usuarios/test_usuariosmodel_init.py              | Inicialización y lógica de modelo de usuarios (incluye permisos)           |
|               | tests/usuarios/test_usuarios_integracion.py            | Integración de usuarios (flujo completo, permisos, feedback)               |
|               | tests/usuarios/test_usuarios.py                        | Funcionalidad general de usuarios                                          |
|               | tests/test_usuarios_controller.py                      | Controlador de usuarios (validación de permisos y feedback)                |
|               | tests/test_usuarios_accesibilidad.py                   | Accesibilidad y feedback visual en usuarios                                |
| **Sidebar/UI** | tests/sidebar/test_sidebar_permisos.py                 | Visibilidad de módulos según permisos en la UI                             |
|               | tests/ui/test_tablas_consistencia_visual.py            | Consistencia visual y feedback en tablas                                   |
| **Login**      | tests/test_login_feedback.py                           | Feedback visual y mensajes claros en login                                 |
|               | tests/test_login.py                                    | Casos de login, incluyendo edge cases de permisos                          |
| **Permisos**   | tests/test_permissions.py                              | Validación de permisos en acciones generales y feedback visual             |
| **Vidrios**    | tests/vidrios/test_vidrios_view.py                    | Permisos y feedback visual en vistas de vidrios                            |
|               | tests/vidrios/test_vidrios_model.py                    | Lógica de modelo y permisos en vidrios                                     |
|               | tests/vidrios/test_vidrios_integracion.py              | Integración y flujo completo en vidrios                                    |
|               | tests/vidrios/test_vidrios_reasignacion.py             | Casos de reasignación y permisos en vidrios                                |
|               | tests/vidrios/test_vidrios_realtime.py                 | Permisos y feedback en operaciones en tiempo real                          |
|               | tests/vidrios/test_vidrios_accesibilidad.py            | Accesibilidad específica en vidrios                                        |
| **Inventario** | tests/inventario/test_inventario.py                   | Permisos, feedback visual y lógica de inventario                           |
| **Obras**      | tests/obras/ (varios)                                 | Permisos, feedback y lógica de obras                                       |
| **Compras**    | tests/compras/ (varios)                               | Permisos, feedback y lógica de compras                                     |
| **Logística**  | tests/logistica/ (varios)                             | Permisos, feedback y lógica de logística                                   |
| **Herrajes**   | tests/herrajes/ (varios)                              | Permisos, feedback y lógica de herrajes                                    |
| **Mantenimiento** | tests/mantenimiento/ (varios)                       | Permisos, feedback y lógica de mantenimiento                               |
| **Contabilidad** | tests/contabilidad/ (varios)                         | Permisos, feedback y lógica de contabilidad                                |
| **Configuración** | tests/configuracion/ (varios)                       | Permisos, feedback y lógica de configuración                               |
| **Otros**      | tests/test_theme_manager.py                           | Temas y feedback visual                                                    |
|               | tests/test_write_file.py                               | Escritura de archivos, feedback                                            |
|               | tests/test_write_desktop.py                            | Escritura en escritorio, feedback                                          |
|               | tests/tests_fallando_registro.md                       | Listado de tests pendientes/fallando, a revisar/corregir                   |

**Notas:**
- Para detalles de cada test, revisar el archivo correspondiente.
- Mantener esta tabla sincronizada con los cambios en la estructura de tests.
- Consultar los checklists y estándares en `docs/ESTANDARES_Y_CHECKLISTS.md` para asegurar cumplimiento de feedback, accesibilidad y seguridad.
