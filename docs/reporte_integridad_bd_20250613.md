# Reporte de Integridad de Estructura de Base de Datos

**Fecha:** 13/06/2025  
**Test ejecutado:** `tests/test_integridad_estructura_bd.py`  
**Comparación:** Documentación (`docs/estructura_tablas_por_modulo.md`) vs. base de datos real (`inventario`)

---

## Tablas faltantes en la base de datos (documentadas pero NO existen)

- inventario
- herrajes
- pedidos_herrajes
- vidrios
- pedidos_vidrios
- pedidos_materiales
- produccion
- logistica
- facturas
- pagos
- usuarios
- auditoria
- configuracion

---

## Columnas extra en la base de datos (existen en la BD pero NO están documentadas)

**Tabla: obras**
- id
- nombre
- direccion
- telefono
- fecha_creacion
- cliente
- estado
- fecha
- fecha_entrega
- cantidad_aberturas
- fecha_compra
- pago_completo
- pago_porcentaje
- monto_usd
- monto_ars
- tipo_obra
- usuario_creador
- fecha_medicion
- dias_entrega
- rowversion

**Tabla: movimientos_inventario**
- id
- material_id
- tipo_movimiento
- cantidad
- fecha_movimiento

(Otras tablas pueden tener columnas extra, revisar el log completo del test para detalles.)

---

## Tablas extra en la base de datos (existen en la BD pero NO están documentadas)

- pedidos
- materiales_por_obra
- proveedores
- materiales_proveedores
- vidrios_por_obra
- obra_materiales
- herrajes_por_obra
- pagos_por_obra
- logistica_por_obra
- reserva_materiales
- movimientos_stock
- inventario_items
- detalle_pedido
- reservas_stock
- reservas_materiales
- pedidos_compra
- inventario_perfiles
- cronograma_obras
- estado_material
- historial
- auditorias_sistema
- pedidos_pendientes
- perfiles_por_obra
- materiales

---

## Recomendaciones

- Crear o migrar las tablas y columnas faltantes según la documentación.
- Actualizar la documentación para reflejar las tablas y columnas realmente usadas si alguna es necesaria y no está documentada.
- Eliminar o justificar tablas/columnas extra si no son necesarias.
- Mantener sincronizados: código, documentación y base de datos.

---
