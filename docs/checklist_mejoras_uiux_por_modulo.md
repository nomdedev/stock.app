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
- [x] Añadir validación visual al probar conexión de base de datos.
### Prioridad media
- [ ] Guardar la configuración de tema y recargar la vista al aplicar cambios.
- [x] Incluir mensajes de éxito/error en `label_feedback`.

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
- [x] Verificar que todos los headers de tablas sigan el estándar (fondo `#f8fafc`, radio `4px`, fuente `10px`).
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
- [x] Revisar que todos los combos y botones tengan `accessibleName` descriptivo.
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
