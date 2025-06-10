# Flujo de carga y gestión de obras, pedidos de material y vidrios

# ---
# INTEGRACIÓN Y TRAZABILIDAD DE PEDIDOS POR OBRA (ERP)
#
# Este checklist y documentación aplica a todos los módulos involucrados en la trazabilidad de pedidos por obra:
# - Inventario: gestión de materiales/perfiles por obra, estado de pedidos, integración con Obras y Contabilidad.
# - Vidrios: pedidos de vidrios por obra, estado y auditoría.
# - Herrajes: pedidos de herrajes por obra, estado y auditoría.
# - Obras: visualización del estado de pedidos de todos los módulos por obra.
# - Producción: consulta de si todos los pedidos están realizados y pagados para habilitar fabricación.
# - Contabilidad: registro y actualización de pagos de pedidos, seguimiento de fechas de acreditación.
# - Logística: consulta de obras listas para fabricar/entregar y asignación a colocador.
#
# Checklist de integración y pendientes (actualizado al 2025-06-10):
#
# [x] Vidrios: registrar y actualizar pedidos por obra y usuario, estado y auditoría.
# [x] Vidrios: mostrar pedidos por usuario y detalle de cada pedido.
# [x] Inventario: pestañas para perfiles y obras con estado de pedidos de material.
# [x] Inventario: lógica para impedir pedidos a obras inexistentes (validar contra módulo Obras).
# [x] Inventario: registrar y actualizar pedidos de material por obra, estado y auditoría.
# [x] Inventario: exponer métodos para consultar estado de pedidos por obra (para Obras y Producción).
# [x] Herrajes: unificar lógica de pedidos por obra, estado y auditoría.
# [x] Herrajes: exponer métodos para consultar estado de pedidos por obra.
# [x] Obras: mostrar estado de pedidos de todos los módulos por obra (vidrios, inventario, herrajes).
# [x] Obras: impedir pedidos a obras inexistentes desde otros módulos.
# [x] Producción: exponer método para saber si todos los pedidos están realizados y pagados.
# [x] Contabilidad: registrar y actualizar pagos de pedidos, exponer estado de pago por pedido.
# [x] Logística: consultar obras listas para fabricar/entregar y asignar colocador.
# [x] Documentar excepciones y justificaciones en docs/estandares_visuales.md y docs/flujo_obras_material_vidrios.md.
# [x] Implementar tests automáticos de integración y feedback visual.
# [x] Inventario: bloquear pedidos con stock negativo y validar con tests de edge cases (10/06/2025).
#
# Ver también: docs/flujo_obras_material_vidrios.md y docs/checklist_mejoras_uiux_por_modulo.md
# ---

## Objetivo

Describir paso a paso el proceso completo para garantizar que:

- Al cargar una obra (por ejemplo, en estado "Medición"), la obra se visualiza correctamente en la tabla de obras.
- Se permite solicitar material desde inventario para esa obra.
- Al cargar el pedido de material, se compara automáticamente contra el stock disponible y se calcula cuánto pedir de cada ítem.
- La obra se refleja en la tabla de vidrios para poder asignar y pedir los vidrios correspondientes.

---

## 1. Carga de una nueva obra

1. El usuario accede al módulo Obras y utiliza el botón "Agregar Obra".
2. Completa los campos requeridos (nombre, cliente, estado, fecha, etc.).
3. El estado inicial puede ser "Medición".
4. Al guardar, la obra debe aparecer en la tabla de obras con todos los datos y el estado correcto.
5. Se registra la acción en la auditoría.

## 2. Visualización y gestión de la obra

1. La obra cargada debe ser visible en la tabla principal de obras.
2. El usuario puede seleccionar la obra y ver sus detalles.
3. Si la obra está en estado "Medición" o similar, debe estar habilitada la opción de "Solicitar Material".

## 3. Solicitud de material desde inventario

1. El usuario, desde la obra seleccionada, accede a la opción "Solicitar Material".
2. Se abre un formulario/listado donde puede seleccionar los materiales requeridos para la obra.
3. Al confirmar el pedido:
    - El sistema compara la cantidad solicitada de cada ítem con el stock disponible en inventario.
    - Si hay stock suficiente, se descuenta automáticamente y se registra el movimiento.
    - Si falta stock, se calcula la cantidad faltante y se genera un pedido de compra para esos ítems.
4. El pedido de material queda asociado a la obra y visible en el historial de pedidos.
5. Se registra la acción en la auditoría.

## 4. Reflejo de la obra en la gestión de vidrios

1. Al cargar una obra, automáticamente debe aparecer en la tabla de vidrios (módulo Vidrios).
2. El usuario puede asignar los vidrios requeridos para esa obra desde el módulo Vidrios.
3. Se permite generar el pedido de vidrios, que queda asociado a la obra y visible en el historial.
4. El sistema puede validar stock de vidrios y generar pedidos de compra si es necesario.
5. Todas las acciones quedan registradas en la auditoría.

---

## 5. Consideraciones generales

- El flujo debe ser consistente y auditable en cada paso.
- El feedback visual debe ser inmediato y claro (éxito, error, advertencia).
- Toda excepción o caso especial debe documentarse en este archivo y en el código.
- Validar que los permisos de usuario permitan cada acción.
- El proceso debe ser testeable con datos simulados y cubrir edge cases (obra sin stock, pedido parcial, etc.).

---

## 6. Pendientes y mejoras

- Validar integración entre módulos (Obras, Inventario, Vidrios).
- Mejorar la experiencia de usuario en la selección y confirmación de materiales/vidrios.
- Documentar cualquier excepción visual o de lógica detectada.
- Revisar y actualizar este flujo ante cambios futuros en la app.

## 7. Ejemplos de mejoras y validaciones adicionales

- Validar que la obra recién cargada se refleje de inmediato en la tabla de obras y en la de vidrios, sin necesidad de recargar la app o cambiar de módulo.
- Verificar que el pedido de material compare correctamente contra el stock real y que, si falta material, el sistema genere automáticamente el pedido de compra solo por la diferencia faltante.
- Comprobar que la asociación entre la obra y los pedidos de material/vidrios quede registrada y sea visible en el historial de la obra y en la auditoría.
- Asegurar que los permisos de usuario no permitan cargar pedidos o asignar vidrios a obras en estados no válidos (por ejemplo, obras finalizadas o canceladas).
- Validar el feedback visual y los mensajes de error en cada paso del flujo, especialmente si hay falta de stock o errores de conexión.
- Sincronizar en tiempo real la información entre módulos (por ejemplo, si se actualiza el estado de la obra, reflejarlo en Inventario y Vidrios sin reiniciar la app).
- Permitir la edición y seguimiento de pedidos parciales o pendientes, mostrando claramente el estado de cada ítem/material/vidrio solicitado.
- Agregar tests automáticos para cubrir casos límite: obra sin stock, pedido parcial, error de conexión, permisos insuficientes, etc.
- Documentar cualquier excepción visual, lógica o de permisos detectada durante el uso real o los tests.
- Revisar periódicamente la experiencia de usuario y el rendimiento en flujos con muchas obras o pedidos simultáneos.

> Actualiza y amplía esta sección cada vez que se detecte una mejora, bug o necesidad de robustez en el flujo.

---

## 8. Mejoras propuestas para la experiencia de usuario y trazabilidad

- Al cargar la obra o el pedido de material, en la tabla de selección de materiales el usuario debe ver:
  - Cantidad solicitada de cada ítem.
  - Stock actual disponible de ese ítem.
  - Cantidad faltante (lo que se debe pedir/comprar).
- Al finalizar y guardar el pedido de material:
  - El usuario debe poder ver fácilmente un resumen de lo solicitado, con fecha y usuario responsable, en la interfaz (por ejemplo, en un historial o panel lateral).
  - Permitir filtrar y buscar pedidos por obra, fecha, usuario o estado.
  - Mostrar visualmente el estado de cada ítem: entregado, pendiente, en espera de compra, etc.
- Sugerencias adicionales:
  - Agregar opción de exportar el historial de pedidos a Excel/PDF.
  - Permitir comentarios u observaciones en cada pedido para trazabilidad.
  - Notificar al usuario (visual o por email) cuando el material esté disponible o el pedido haya sido procesado.
  - Incluir validaciones visuales (colores, íconos) para advertir si el stock es insuficiente antes de guardar el pedido.
  - Mejorar la navegación entre obras y pedidos, permitiendo ir de un pedido a la obra asociada y viceversa con un solo clic.
  - Registrar en la auditoría cada acción relevante (alta, edición, entrega, cancelación) con fecha, usuario y detalle.

> Suma aquí cualquier idea o mejora que surja para optimizar la experiencia y la trazabilidad del proceso.

---

## 9. Ideas adicionales para robustez, UX y escalabilidad

- Permitir edición y cancelación de pedidos de material/vidrios antes de ser procesados, con registro de cambios en la auditoría.
- Implementar confirmaciones visuales (diálogos modales) antes de acciones críticas como eliminar o modificar pedidos.
- Agregar indicadores visuales de progreso en procesos largos (por ejemplo, carga masiva de materiales o actualización de stock).
- Soporte para adjuntar archivos o imágenes a obras y pedidos (planos, fotos de avance, comprobantes).
- Integrar notificaciones push o alertas en la app para avisar sobre pedidos pendientes, materiales recibidos o cambios de estado relevantes.
- Optimizar la carga y paginación de tablas para soportar grandes volúmenes de obras y pedidos sin perder fluidez.
- Permitir personalización de columnas y filtros en las tablas de obras, pedidos y vidrios según preferencias del usuario.
- Incluir accesos rápidos (botones o atajos) para las acciones más frecuentes (nuevo pedido, exportar, ver historial).
- Mejorar la accesibilidad: navegación por teclado, descripciones para lectores de pantalla, contraste alto y foco visible en todos los elementos interactivos.
- Documentar flujos alternativos o excepcionales (por ejemplo, devolución de material, reasignación de vidrios, cierre anticipado de obra).
- Proveer un dashboard/resumen visual con KPIs: obras activas, pedidos pendientes, stock crítico, etc.
- Automatizar la generación de reportes periódicos (por email o descarga) para responsables de obra, compras y stock.

> Suma aquí cualquier otra idea que ayude a que la aplicación sea más robusta, usable y escalable.

---

## 10. Integración en tiempo real: edición y cancelación de pedidos

- Cuando un pedido es editado o cancelado desde el módulo de Pedidos/Compras:
    - Se emite una señal centralizada (`pedido_actualizado` o `pedido_cancelado`) desde el event_bus.
    - Los controladores de Inventario y Obras están suscritos a estas señales y refrescan automáticamente la vista, mostrando feedback visual inmediato (info o advertencia).
    - En caso de cancelación, el inventario se actualiza y se muestra un mensaje visual de advertencia en ambos módulos.
    - Todas las acciones quedan registradas en la auditoría con usuario, fecha y detalle.
- Este flujo asegura que los cambios de estado de los pedidos se reflejan en tiempo real en los módulos relevantes, sin necesidad de recargar la app.

---

## Excepciones y justificaciones (Herrajes)

- Si ocurre un error de conexión o consulta al obtener pedidos o estado de pedidos de herrajes, el sistema retorna un string de error y lo registra en la auditoría. Esto permite detectar problemas de integración y mantener la trazabilidad.
- Si no hay pedidos registrados para una obra, el estado retornado es 'pendiente' por convención, para facilitar la integración con Producción y Logística.
- Todos los métodos de consulta de pedidos y estado en Herrajes están documentados y expuestos para integración cruzada.

## Excepciones y justificaciones (Logística)

- Si ocurre un error al consultar obras listas para entrega o al asignar colocador, el sistema muestra feedback visual y registra el evento en auditoría.
- La consulta de obras listas integra los estados y pagos de todos los módulos (Inventario, Vidrios, Herrajes, Contabilidad) para asegurar robustez y trazabilidad.
- El método de asignación de colocador valida y registra la acción, permitiendo seguimiento y auditoría cruzada.

## Excepciones y justificaciones (Inventario)

- Si ocurre un error de conexión o consulta al obtener pedidos o estado de pedidos de material, el sistema retorna un string de error y lo registra en la auditoría.
- Si no hay pedidos registrados para una obra, el estado retornado es 'pendiente' para facilitar la integración y trazabilidad.
- Los métodos de consulta de pedidos y estado están documentados y expuestos para integración cruzada.

## Excepciones y justificaciones (Vidrios)

- Si ocurre un error al consultar pedidos o estado de vidrios, se muestra feedback visual y se registra el evento en auditoría.
- Si no hay pedidos de vidrios para una obra, el estado retornado es 'pendiente'.
- Los métodos de consulta y registro de pedidos están documentados y permiten trazabilidad total.

## Excepciones y justificaciones (Obras y Producción)

- Si algún módulo no puede consultar el estado de pedidos de una obra, se muestra advertencia visual y se registra en auditoría.
- La habilitación de fabricación en Producción depende de la consulta exitosa de todos los estados y pagos; si hay error, se bloquea la acción y se informa al usuario.
- El método de Producción para habilitar fabricación valida que todos los pedidos estén realizados y pagados, y documenta cualquier excepción o edge case.

> Actualiza este documento cada vez que se ajuste el flujo o se detecte un caso especial.
