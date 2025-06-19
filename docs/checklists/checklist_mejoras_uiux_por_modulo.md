# Checklist de Unificación Visual y UX por Módulo

**Leyenda:**
- ✅ Unificado y documentado
- ⚠️ Parcial o pendiente de unificación
- ❌ No implementado

| Módulo      | Título de módulo | Headers de tabla | Botones (sombra/color) | Feedback visual | Accesibilidad/tooltips | Documentación QSS | Bordes/Paddings/Márgenes |
|-------------|------------------|------------------|------------------------|-----------------|-----------------------|-------------------|--------------------------|
| Obras       | ✅ (setObjectName, layout y QSS global OK) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad) | ✅ | ✅ (bordes, paddings, márgenes) |
| Vidrios     | ✅ (setObjectName, layout y QSS global OK) | ✅ | ✅ (sombra, color, ubic., accesibilidad) | ✅ | ✅ (tooltips y accesibilidad) | ✅ | ✅ (bordes, paddings, márgenes) |
| Compras     | ✅ (setObjectName, diálogos y autocompletado implementados) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad mejorados) | ✅ | ✅ (bordes, paddings, márgenes, diálogos) |
| Pedidos     | ✅ (setObjectName, diálogos y autocompletado implementados) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad mejorados) | ✅ | ✅ (bordes, paddings, márgenes, diálogos) |
| Logística   | ✅ (usa setObjectName y QSS, sombra y accesibilidad en botones)        | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad mejorados) | ✅ | ✅ (bordes, paddings, márgenes, formularios) |
| Producción  | ✅ (setObjectName, layout y QSS global OK) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad) | ✅ | ✅ (bordes, paddings, márgenes) |
| Usuarios    | ✅ (setObjectName, sombra y accesibilidad en botón principal) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad mejorados) | ✅ | ✅ (bordes, paddings, márgenes, formularios) |
| Inventario  | ✅ (setObjectName, sombra y accesibilidad en botones principales) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad mejoradas) | ✅ | ✅ (bordes, paddings, márgenes, formularios) |
| Herrajes    | ✅ (setObjectName, sombra y accesibilidad en botones principales y de pedidos) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad mejoradas) | ✅ | ✅ (bordes, paddings, márgenes, formularios) |
| Mantenimiento | ✅ (setObjectName, layout y QSS global OK, filtros) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad) | ✅ | ✅ (bordes, paddings, márgenes, filtros) |
| Configuración | ✅ (setObjectName, layout y QSS global OK) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad) | ✅ | ✅ (bordes, paddings, márgenes) |
| Contabilidad | ✅ (setObjectName, layout y QSS global OK) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad) | ✅ | ✅ (bordes, paddings, márgenes) |
| Notificaciones | ✅ (setObjectName, layout y QSS global OK) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad) | ✅ | ✅ (bordes, paddings, márgenes) |

## Pendientes generales
- Aplicar setObjectName a los títulos de módulo en todos los view.py para que tomen el QSS unificado.
- Verificar y aplicar sombra en todos los botones principales/secundarios.
- Mejorar y documentar accesibilidad/tooltips en todos los módulos.
- Revisar y documentar bordes, paddings y márgenes en QSS.
- Documentar cualquier excepción visual en los QSS.
- Unificar lógica de pedidos por obra en Inventario y Herrajes, y exponer estado de pedidos para consulta cruzada.
- Impedir pedidos a obras inexistentes desde cualquier módulo (validar contra Obras).
- Mostrar en Obras el estado de pedidos de todos los módulos (vidrios, inventario, herrajes).
- Integrar Producción y Logística para que solo se habilite fabricación/entrega si todos los pedidos están realizados y pagados.
- Registrar y actualizar pagos de pedidos en Contabilidad, y exponer estado de pago por pedido.
- Implementar tests automáticos de integración y feedback visual.

# Checklist de mejoras UI/UX por módulo

Este documento resume sugerencias específicas para mejorar la experiencia de usuario y la interfaz en cada módulo del ERP. Está basado en la revisión del repositorio a fecha 2025‑06‑08 y en las guías existentes en `docs/` y los checklists previos.

## Auditoría
### Prioridad alta
- [ ] Simplificar los filtros de búsqueda y permitir guardar filtros frecuentes.
### Prioridad media
- [ ] Incluir paginación en la tabla de registros.
- [ ] Mostrar resumen en la parte superior con totales (acciones por usuario/módulo).
### Prioridad baja
- [ ] Agregar atajos de teclado para exportar (`Ctrl+E`) y para cerrar (`Esc`).

## Compras
### Prioridad alta
- [ ] Revisar que todos los botones utilicen `estilizar_boton_icono`.
- [ ] Permitir búsqueda rápida de proveedores al crear un pedido.
### Prioridad media
- [ ] Unificar el diálogo de "Cargar presupuesto" con la estética general (bordes 8‑12 px).
### Prioridad baja
- [ ] Documentar íconos faltantes en `checklist_botones_iconos.txt`.

## Configuración
### Prioridad alta
- [ ] Añadir validación visual al probar conexión de base de datos.
### Prioridad media
- [ ] Guardar la configuración de tema y recargar la vista al aplicar cambios.
- [ ] Incluir mensajes de éxito/error en `label_feedback`.

## Contabilidad
### Prioridad alta
- [ ] Incorporar filtros por fecha y por obra.
- [ ] Implementar banner de feedback al registrar pagos.
### Prioridad media
- [ ] Mejorar la legibilidad de la tabla de facturas (alineación de montos a la derecha).

## Herrajes
### Prioridad alta
- [ ] Completar pendientes del archivo `checklist_mejoras_herrajes.md` (filtros avanzados, historial de cambios, notificaciones).
- [ ] Validar stock en tiempo real en el modal de pedido.
### Prioridad media
- [ ] Optimizar el orden de tabulación y añadir atajos de teclado.

## Inventario
### Prioridad alta
- [ ] Verificar que todos los headers de tablas sigan el estándar (fondo `#f8fafc`, radio `4px`, fuente `10px`).
- [ ] Mejorar el feedback cuando falla la conexión a la base de datos.
### Prioridad media
- [ ] Incorporar un buscador global de items en la parte superior.
- [ ] Permitir personalizar columnas visibles desde la UI.

## Logística
### Prioridad alta
- [ ] Revisar la accesibilidad de los tabs (orden de tabulación y nombres accesibles).
### Prioridad media
- [ ] Agregar indicadores visuales para el progreso de cada envío.
### Prioridad baja
- [ ] Documentar cualquier excepción de estilo en `docs/estandares_visuales.md`.

## Mantenimiento
### Prioridad alta
- [ ] Centralizar mensajes de error en un banner reutilizable.
- [ ] Confirmar que los botones tengan tooltip y `accessibleName`.
### Prioridad media
- [ ] Añadir filtros por fecha de mantenimiento y estado.

## Notificaciones
### Prioridad alta
- [ ] Implementar paginación o scroll infinito en la tabla de notificaciones.
### Prioridad media
- [ ] Permitir filtrar por tipo o estado de notificación.
- [ ] Añadir opción de "marcar todas como leídas".

## Obras
### Prioridad alta
- [ ] Migrar estilos embebidos de los diálogos a QSS global cuando sea posible.
- [ ] Incorporar validación visual más clara en el alta y edición de obras.
### Prioridad media
- [ ] Añadir botones de acción directa en la tabla (editar/eliminar) con confirmación.

## Pedidos
### Prioridad alta
- [ ] Hacer persistente la configuración de columnas de la tabla de pedidos por usuario.
- [ ] Mejorar la búsqueda de obras y materiales con autocompletado.
### Prioridad media
- [ ] Incluir feedback visual al crear o cancelar un pedido.

## Usuarios
### Prioridad alta
- [ ] Revisar que todos los combos y botones tengan `accessibleName` descriptivo.
### Prioridad media
- [ ] Añadir opción para restablecer contraseña con confirmación.
- [ ] Mostrar un resumen de permisos en un panel lateral o popup más compacto.

## Vidrios
### Prioridad alta
- [ ] Agregar filtro por tipo y espesor de vidrio.
### Prioridad media
- [ ] Permitir cambiar entre vista detallada y compacta de la tabla.
### Prioridad baja
- [ ] Documentar íconos nuevos en `checklist_botones_iconos.txt`.

---

Mantener este checklist actualizado y marcar cada punto una vez implementado. Todas las mejoras deben seguir los estándares definidos en `docs/estandares_visuales.md` y `docs/estandares_feedback.md`.

### Cambios recientes
#### Logística
- [x] Visualización de estado y fecha de pago de colocación en la tabla y modal.
- [x] Diálogo modal para registrar/editar pagos de colocación.
- [x] Lógica de backend para registrar, editar y consultar pagos (integración con Contabilidad).
- [x] Registro de excepciones de colocación sin pago y feedback visual inmediato.
- [x] Cumplimiento de estándares visuales y de accesibilidad en todos los formularios y tablas.
- [x] Tests automáticos de integración y feedback visual para pagos y trazabilidad implementados y validados (09/06/2025).
- [x] Validación de habilitación de colocación solo si el pago está realizado (test).
- [x] Registro de excepción y feedback visual si se realiza colocación sin pago (test).
- [x] Visualización de estado y fecha de pago (test).
- [x] Interacción con Contabilidad para consultar pagos (test).
- [x] Feedback visual inmediato en la UI (test).

#### Contabilidad
- [x] Métodos para registrar, editar y consultar pagos por pedido/obra/módulo.
- [x] Exposición de estado de pago para otros módulos.
- [x] Visualización de pagos en la UI y feedback visual robusto.

#### General
- [x] Documentación de estándar visual y selectores QSS en docs/estandares_visuales.md.
- [x] Checklist actualizado con integración de pagos y feedback visual.
- [ ] Tests automáticos de integración y feedback visual pendientes de ejecutar.

### Producción
- [x] Auditoría de accesibilidad y visuales completada el 18/06/2025. Todos los botones, tablas y headers cumplen con QSS global, tooltips, accessibleName y focus. Se recomienda solo revisar inputs secundarios para agregar accessibleName si falta.
