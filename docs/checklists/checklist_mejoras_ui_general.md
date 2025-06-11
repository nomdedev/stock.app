# Checklist de Mejoras Generales de UI/UX

Fecha: 08/06/2025

Este checklist resume puntos de mejora transversales a todos los módulos de la aplicación.
El objetivo es unificar la apariencia y la interacción con el usuario.

# ---
# POLÍTICA DE ACTUALIZACIÓN Y DOCUMENTACIÓN
#
# - Este checklist debe actualizarse tras cada mejora visual, de accesibilidad o feedback en cualquier módulo.
# - Si se detecta una excepción visual, registrar el motivo en `ESTANDARES_Y_CHECKLISTS.md`.
# - Extender los tests automáticos de UI para cubrir los nuevos ítems marcados como completados.
# - Para detalles y justificaciones, ver la documentación central en `docs/ESTANDARES_Y_CHECKLISTS.md`.
#
# ---

## 1. Tablas
- [x] Verificar que **todas** las tablas usen el mismo QSS de cabecera
  - Fondo `#f8fafc`, radio `4px`, fuente `10px`, sin negrita.
  - Altura máxima de filas `25px`, colores de selección `#e3f6fd`.
- [x] Revisar que la fuente y tamaño de celdas sea consistente (12 px o menor).
- [x] Confirmar que las columnas importantes estén alineadas (número a la derecha, texto a la izquierda).
- [x] Dejar establecido un tamaño de 200 px de ancho para cada uno de los recuadros donde se debe llenar informacion en los formularios y buscadores, con sus respectivos bordes redondeados con radio '4px'.



## 2. Botones
- [x] Todos los botones principales y secundarios deben utilizar el helper `estilizar_boton_icono`.
- [x] Los botones de acción deben ubicarse en la misma zona de cada vista (por ejemplo, barra superior o panel lateral).
- [x] Todos los botones visibles deben tener un ícono SVG/PNG definido en `resources/icons` y documentarse en `checklist_botones_iconos.txt`.
- [x] Añadir `setAccessibleName` y `setToolTip` descriptivos.

## 3. Layout y modales
- [x] Mantener márgenes y paddings mínimos de **20 px** vertical y **24 px** horizontal.
- [x] Bordes redondeados de diálogos entre **8 px** y **12 px**.
- [x] Deshabilitar botones mientras se realiza una acción (evita doble clic) y mostrar feedback de carga.

## 4. Feedback visual
- [x] Centralizar todos los mensajes en `label_feedback` o componentes equivalentes.
- [x] Colores estándar: info `#e3f6fd`, éxito `#d1f7e7`, error `#fee2e2`, advertencia `#fef9c3`.
- [x] Permitir cerrar manualmente banners o mensajes largos.

## 5. Accesibilidad
- [x] Revisar el orden de tabulación en formularios.
- [x] Incluir atajos de teclado en acciones frecuentes (por ejemplo, `Ctrl+E` para exportar).
- [x] Comprobar que lectores de pantalla anuncien correctamente botones e inputs.

## 6. Documentación y tests
- [ ] Actualizar este archivo al implementar cada mejora.
- [ ] Extender los tests de UI para cubrir nuevas verificaciones de estilo e íconos.

## 7. Ventanas y formularios
- [ ] Usar QFrame o QDialog con QGraphicsDropShadowEffect para cada ventana de formulario.
- [ ] Bordes redondeados entre 8‑12 px, igual que #login_card en theme_light.qss.
- [ ] Asignar setObjectName("form_input") (o nombre común) a cada QLineEdit, QComboBox y QTextEdit.
- [ ] Definir estilos generales en theme_light.qss para QLineEdit#form_input y variantes.
- [ ] Colocar setToolTip y setAccessibleName en cada input.
- [ ] Todos los botones principales deben usar estilizar_boton_icono y tener ícono en resources/icons/.
- [ ] Añadir setAccessibleName y setToolTip a los botones.
- [ ] Deshabilitar botones mientras se ejecuta la acción (evita doble clic).
- [ ] Aplicar QGraphicsDropShadowEffect sutil a los botones principales.
- [ ] Incluir label_feedback en cada formulario con colores estándar (info #e3f6fd, éxito #d1f7e7, error #fee2e2, advertencia #fef9c3).
- [ ] Permitir cerrar manualmente banners de mensajes largos.
- [ ] Mantener mínimo 20 px vertical y 24 px horizontal en los layouts de formularios.
- [ ] Revisar alineación y evitar superposición de barras de scroll.

## 8. Modales y ventanas principales
- [ ] Usar QFrame principal con setObjectName("dialog_card") para heredar estilo de bordes y sombras.
- [ ] Títulos de cada modal con setObjectName("label_titulo") y definir tamaño/peso en theme_light.qss.
- [ ] Ventanas de confirmación/advertencia deben seguir la misma paleta visual que el login.

## 9. Integración con controlador
- [ ] Formularios deben comunicarse con su Controller por señales, nunca manipular la base de datos directamente.
- [ ] Feedback de éxito o error visible al cerrar la ventana.

## 10. Indicadores de carga
- [ ] Formularios con operaciones largas deben mostrar spinner o barra de progreso y deshabilitar botones hasta terminar.

## 11. Orden de tabulación y atajos
- [ ] Revisar el orden de tabulación (setTabOrder) para que sea lógico.
- [ ] Definir atajos de teclado (Ctrl+S para guardar, Esc para cancelar, etc.) y documentarlos en tooltips.

## 12. Unificación y checklist por módulo
- [ ] Marcar en checklist_mejoras_uiux_por_modulo.md cada módulo conforme se corrija.
- [ ] Registrar nuevos íconos en checklist_botones_iconos.txt.
- [ ] Documentar excepciones o estilos especiales en docs/estandares_visuales.md.

## 13. Tests de UI
- [ ] Añadir pruebas automáticas para verificar estilos (bordes, sombras, tooltips, headers).
- [ ] Extender los tests existentes en tests/ para cubrir nuevas verificaciones de estilo.

## 14. Sincronización con temas
- [ ] Garantizar que al aplicar set_theme(app, DEFAULT_THEME) todas las vistas carguen el QSS.
- [ ] Revisar theme_manager.py para guardar preferencia de usuario y recargar la UI si cambia.

