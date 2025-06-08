# RESUMEN ACTUALIZADO DE TESTS Y COBERTURA (08/06/2025)

**Estado general:**
- Todos los módulos principales (Obras, Inventario, Pedidos, Contabilidad, Usuarios/Roles, Auditoría, Integración/E2E) cuentan con tests unitarios y de integración implementados, validados y alineados con los estándares de UI/UX, feedback, accesibilidad y robustez definidos en los checklists y documentación.
- El checklist de casos cubiertos y este README_TESTS.md están completamente actualizados, reflejando el estado real de la cobertura y los casos de negocio validados.
- La cobertura global reportada es del 11%. Aunque todos los flujos críticos y edge cases de negocio están cubiertos, la cobertura es baja principalmente por la falta de tests en vistas y modelos secundarios.

**Cobertura por módulo:**
- **Obras:** Todos los casos de alta, edición, duplicados, validaciones y edge/negativos cubiertos.
- **Inventario:** Reservas, devoluciones, ajustes, alertas de stock y feedback visual, incluyendo casos de error y edge.
- **Pedidos:** Generación, duplicados, recepción, rollback y auditoría.
- **Contabilidad:** Generación/anulación de recibos, balance, integración con obras y movimientos.
- **Usuarios/Roles:** Creación, edición, permisos, feedback visual y edge cases de permisos.
- **Auditoría:** Registro, consulta, exportación, filtros, errores y flujo de integración.
- **Integración/E2E:** Flujo completo desde alta de obra hasta pago y auditoría, incluyendo rollback y validación cruzada.

**Estándares y checklist:**
- Todos los tests están alineados con los estándares de feedback, accesibilidad, robustez y logging/auditoría.
- Cada caso está marcado como COMPLETO en `checklist_formularios_botones_ui.txt` y documentado en este README_TESTS.md.
- Se mantiene trazabilidad y justificación de cada test y excepción en los archivos de estándares y documentación.

**Próximos pasos recomendados:**
- Aumentar la cobertura en vistas (`view.py`) y modelos secundarios.
- Mantener el checklist y README actualizados ante cualquier cambio.
- Actualizar el badge de cobertura tras cada ejecución de tests.
- Seguir priorizando la cobertura de lógica de negocio y feedback visual/accesible.

---

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

---

## Checklist de casos cubiertos (actualizado 2025-06-07)

### OBRAS
- [x] test_alta_obra_exito
- [x] test_alta_obra_faltante
- [x] test_alta_obra_fechas_incorrectas
- [x] test_alta_obra_duplicada
- [x] test_editar_obra_rowversion
- [x] test_alta_obra_cliente_none
- [x] test_editar_obra_nombre_vacio
- [x] test_editar_obra_cliente_vacio

> Todos los tests de OBRAS implementados y validados. Ver checklist_formularios_botones_ui.txt para detalle de estándares y cobertura.

### INVENTARIO
- [x] test_reserva_exito
- [x] test_reserva_stock_insuficiente
- [x] test_reserva_cantidad_invalida
- [x] test_devolucion_exito
- [x] test_devolucion_cantidad_excedida
- [x] test_ajuste_stock_valido
- [x] test_ajuste_stock_negativo
- [x] test_alerta_stock_bajo

> Todos los tests de Inventario implementados y validados. Ver checklist_formularios_botones_ui.txt para detalle de estándares y cobertura.

### PEDIDOS
- [x] test_generar_pedido_faltante
- [x] test_generar_pedido_sin_faltantes
- [x] test_generar_pedido_duplicado
- [x] test_recibir_pedido_exito
- [x] test_recibir_pedido_repetido
- [x] test_recibir_pedido_estado_invalido
- [x] test_rollback_en_recepcion
- [x] test_auditoria_en_generar_pedido
- [x] test_auditoria_en_recepcion

> Todos los tests de Pedidos implementados y validados. Ver checklist_formularios_botones_ui.txt para detalle de estándares y cobertura.

### CONTABILIDAD
- [x] test_generar_recibo
- [x] test_anular_recibo
- [x] test_obtener_balance
- [x] test_carga_y_reflejo_en_tabla

> Todos los tests de Contabilidad implementados y validados. Ver checklist_formularios_botones_ui.txt para detalle de estándares y cobertura.

### USUARIOS/ROLES
- [x] test_crear_usuario
- [x] test_actualizar_estado_usuario
- [x] test_obtener_usuarios_activos
- [x] test_obtener_modulos_permitidos
- [x] test_obtener_usuarios
- [x] test_obtener_permisos_por_usuario
- [x] test_guardar_permisos_usuario_admin
- [x] test_guardar_permisos_usuario_no_admin
- [x] test_feedback_visual_sin_permisos

> Todos los tests de Usuarios/Roles implementados y validados. Ver checklist_formularios_botones_ui.txt para detalle de estándares y cobertura.

### AUDITORÍA
- [x] test_registrar_evento
- [x] test_registrar_evento_faltan_argumentos
- [x] test_obtener_logs
- [x] test_obtener_auditorias
- [x] test_exportar_auditorias
- [x] test_registrar_evento_error
- [x] test_exportar_auditorias_pdf
- [x] test_exportar_auditorias_formato_no_soportado
- [x] test_obtener_logs_vacio
- [x] test_obtener_auditorias_filtros_invalidos
- [x] test_flujo_integracion_registro_y_lectura
- [x] test_registrar_evento_guarda_evento
- [x] test_obtener_eventos_retorna_lista
- [x] test_no_conexion_real

> Todos los tests de Auditoría implementados y validados. Ver checklist_formularios_botones_ui.txt para detalle de estándares y cobertura.

### INTEGRACIÓN Y E2E
- [x] test_flujo_alta_obra_a_pago
- [x] test_rollback_en_flujo
- [x] test_auditoria_en_flujo

> Todos los tests de integración/E2E implementados y validados. Ver checklist_formularios_botones_ui.txt para detalle de estándares y cobertura.

---

## Test de mapeo módulo-vista en MainWindow

Se ha implementado el test automatizado `tests/test_mainwindow_module_view_mapping.py` para garantizar que la selección de cada módulo en el sidebar carga la vista correspondiente en el stack principal (`QStackedWidget`).

**Propósito:**
- Prevenir y detectar cualquier desincronización entre el orden de los módulos en el sidebar y el orden de agregado de vistas en el stack.
- Garantizar que cada módulo siempre muestre la vista correcta, evitando errores como el ocurrido con Vidrios, Compras y Logística.

**Cobertura:**
- El test recorre todos los módulos principales y valida que la clase de la vista cargada en el stack corresponde al módulo seleccionado.
- Si se detecta un desfase, el test falla con un mensaje claro indicando el módulo y la vista incorrecta.

**Ejecución:**
```bash
pytest tests/test_mainwindow_module_view_mapping.py --maxfail=1 --disable-warnings -v
```

**Resultado esperado:**
- Todos los módulos deben cargar la vista correcta. Si hay un error de mapeo, el test lo reporta inmediatamente.

**Estado:**
- [08/06/2025] Test implementado y validado tras la corrección del orden de vistas en `main.py`.
- Este test debe mantenerse actualizado ante cualquier cambio en el orden de módulos o vistas.

---

**Recuerda:**
- Marca cada test/caso como COMPLETO en el checklist tras implementarlo y validarlo.
- Mantén la cobertura y checklist actualizados tras cada avance.
