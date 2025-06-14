# Documentación Detallada de Tablas y Uso por Módulo

**Actualizado al 13/06/2025**

Este documento describe en detalle, módulo por módulo, todas las tablas utilizadas en el sistema, sus columnas, el propósito de cada campo y cómo se relacionan con la lógica de la aplicación. Es referencia obligatoria para desarrollo, QA, auditoría y sincronización con la base de datos.

---

## Índice
1. [Obras](#obras)
2. [Inventario](#inventario)
3. [Herrajes](#herrajes)
4. [Vidrios](#vidrios)
5. [Pedidos de Materiales](#pedidos-de-materiales)
6. [Producción](#producción)
7. [Logística](#logística)
8. [Contabilidad](#contabilidad)
9. [Usuarios y Auditoría](#usuarios-y-auditoría)
10. [Configuración](#configuración)

---

## Obras

**Tabla:** `obras`
- **Módulo:** Obras
- **Columnas:**
  - `id` (PK, int, autoincremental): Identificador único de la obra.
  - `nombre` (varchar): Nombre de la obra.
  - `cliente` (varchar): Cliente asociado.
  - `fecha_medicion` (date): Fecha de medición.
  - `fecha_entrega` (date): Fecha de entrega pactada.
  - `estado` (varchar): Estado general de la obra (Medición, Fabricación, Entrega, etc).
  - `direccion` (varchar): Dirección de la obra.
  - `observaciones` (text): Observaciones generales.
  - `usuario_creador` (int, FK a usuarios): Usuario que creó la obra.
  - `fecha_creacion` (datetime): Fecha de alta.
  - `fecha_modificacion` (datetime): Última modificación.
  - `estado_actual` (varchar): Estado actual de la obra.
  - `ultima_actualizacion` (datetime): Fecha de la última actualización del estado.
- **Uso:** Gestión central de obras, integración con pedidos, producción, logística y contabilidad.

**Tabla:** `historial_estados`
- **Módulo:** Obras
- **Columnas:**
  - `id` (PK, int, autoincremental): Identificador único del registro.
  - `id_obra` (FK a obras): Relación con la tabla `obras`.
  - `estado` (varchar): Estado de la obra en ese momento.
  - `fecha_cambio` (datetime): Fecha en que se cambió al estado.
  - `detalles` (varchar): Información adicional sobre el cambio.
- **Uso:** Registrar el historial de cambios de estado de las obras para trazabilidad.

---

## Inventario

**Tabla:** `inventario`
- **Módulo:** Inventario
- **Columnas:**
  - `id` (PK, int): Identificador del material.
  - `nombre` (varchar): Nombre del material.
  - `descripcion` (varchar): Descripción.
  - `stock` (int): Cantidad disponible.
  - `stock_minimo` (int): Stock mínimo recomendado.
  - `ubicacion` (varchar): Ubicación física.
  - `unidad` (varchar): Unidad de medida.
  - `activo` (bit): Si el material está activo.
- **Uso:** Control de stock, reservas, devoluciones, generación de pedidos.

**Tabla:** `movimientos_inventario`
- **Módulo:** Inventario
- **Columnas:**
  - `id` (PK, int)
  - `id_material` (FK a inventario)
  - `tipo_movimiento` (varchar): Entrada, salida, reserva, devolución.
  - `cantidad` (int)
  - `fecha` (datetime)
  - `usuario` (FK a usuarios)
  - `motivo` (varchar)
- **Uso:** Auditoría y trazabilidad de movimientos de stock.

**Tabla:** `vidrios_por_obra` (actualización)
- **Nuevas Columnas:**
  - `fecha_actualizacion` (datetime): Fecha de la última actualización del pedido de vidrios.
- **Uso:** Registrar cuándo se actualizó por última vez el estado del pedido de vidrios.

**Tabla:** `herrajes_por_obra` (actualización)
- **Nuevas Columnas:**
  - `fecha_actualizacion` (datetime): Fecha de la última actualización del pedido de herrajes.
- **Uso:** Registrar cuándo se actualizó por última vez el estado del pedido de herrajes.

---

## Herrajes

**Tabla:** `herrajes`
- **Módulo:** Herrajes
- **Columnas:**
  - `id` (PK, int)
  - `nombre` (varchar)
  - `tipo` (varchar)
  - `stock` (int)
  - `proveedor` (varchar)
  - `activo` (bit)
- **Uso:** Catálogo y stock de herrajes.

**Tabla:** `pedidos_herrajes`
- **Módulo:** Herrajes, Pedidos
- **Columnas:**
  - `id` (PK, int)
  - `id_obra` (FK a obras)
  - `fecha` (datetime)
  - `estado` (varchar)
  - `usuario` (FK a usuarios)
- **Uso:** Seguimiento de pedidos de herrajes por obra.

---

## Vidrios

**Tabla:** `vidrios`
- **Módulo:** Vidrios
- **Columnas:**
  - `id` (PK, int)
  - `tipo` (varchar)
  - `espesor` (float)
  - `medidas` (varchar)
  - `stock` (int)
  - `proveedor` (varchar)
  - `activo` (bit)
- **Uso:** Catálogo y stock de vidrios.

**Tabla:** `pedidos_vidrios`
- **Módulo:** Vidrios, Pedidos
- **Columnas:**
  - `id` (PK, int)
  - `id_obra` (FK a obras)
  - `fecha` (datetime)
  - `estado` (varchar)
  - `usuario` (FK a usuarios)
- **Uso:** Seguimiento de pedidos de vidrios por obra.

---

## Pedidos de Materiales

**Tabla:** `pedidos_materiales`
- **Módulo:** Pedidos, Inventario
- **Columnas:**
  - `id` (PK, int)
  - `id_obra` (FK a obras)
  - `fecha` (datetime)
  - `estado` (varchar)
  - `usuario` (FK a usuarios)
- **Uso:** Seguimiento de pedidos de materiales por obra.

**Tabla:** `pedidos_material`
- **Módulo:** Inventario
- **Columnas:**
  - `id` (PK, int): Identificador único del pedido.
  - `id_obra` (FK a obras): Obra asociada al pedido.
  - `id_perfil` (FK a inventario_perfiles): Material solicitado.
  - `cantidad` (int): Cantidad solicitada.
  - `estado` (varchar): Estado del pedido (pendiente, completado, etc.).
  - `fecha` (datetime): Fecha del pedido.
  - `usuario` (FK a usuarios): Usuario que realizó el pedido.
- **Uso:** Registro de pedidos de materiales asociados a obras.

**Tabla:** `reservas_stock`
- **Módulo:** Inventario
- **Columnas:**
  - `id` (PK, int): Identificador único de la reserva.
  - `id_item` (FK a inventario): Material reservado.
  - `id_obra` (FK a obras): Obra asociada a la reserva.
  - `cantidad_reservada` (int): Cantidad reservada.
  - `estado` (varchar): Estado de la reserva (activa, pendiente, etc.).
  - `fecha_reserva` (datetime): Fecha de la reserva.
- **Uso:** Gestión de reservas de stock para obras.

**Tabla:** `detalle_pedido`
- **Módulo:** Compras
- **Columnas:**
  - `id` (PK, int): Identificador único del detalle.
  - `id_pedido` (FK a pedidos): Pedido asociado.
  - `id_item` (FK a inventario): Ítem solicitado.
  - `cantidad` (int): Cantidad solicitada.
  - `precio_unitario` (decimal): Precio unitario del ítem.
  - `subtotal` (decimal): Subtotal del detalle.
- **Uso:** Almacenar detalles de pedidos realizados.

---

## Usuarios y Auditoría

**Tabla:** `usuarios`
- **Módulo:** Usuarios
- **Columnas:**
  - `id` (PK, int)
  - `nombre` (varchar)
  - `email` (varchar)
  - `rol` (varchar)
  - `activo` (bit)
- **Uso:** Gestión de usuarios y permisos.

**Tabla:** `auditoria`
- **Módulo:** Auditoría
- **Columnas:**
  - `id` (PK, int)
  - `usuario` (FK a usuarios)
  - `fecha` (datetime)
  - `accion` (varchar)
  - `modulo` (varchar)
  - `detalle` (text)
- **Uso:** Registro de acciones y eventos para trazabilidad.

**Tabla:** `notificaciones`
- **Módulo:** Notificaciones
- **Columnas:**
  - `id` (PK, int): Identificador único de la notificación.
  - `usuario_id` (FK a usuarios): Usuario destinatario de la notificación.
  - `mensaje` (varchar): Contenido de la notificación.
  - `fecha_envio` (datetime): Fecha de envío de la notificación.
  - `estado` (varchar): Estado de la notificación (pendiente, leída, etc.).
- **Uso:** Gestión de alertas y mensajes a los usuarios.

**Tabla:** `permisos_modulos`
- **Módulo:** Usuarios
- **Columnas:**
  - `id` (PK, int): Identificador único del permiso.
  - `id_usuario` (FK a usuarios): Usuario al que se le asigna el permiso.
  - `modulo` (varchar): Módulo al que aplica el permiso.
  - `puede_ver` (bit): Indica si el usuario puede ver el módulo.
  - `puede_modificar` (bit): Indica si el usuario puede modificar el módulo.
  - `puede_aprobar` (bit): Indica si el usuario puede aprobar acciones en el módulo.
- **Uso:** Gestión de permisos de acceso a módulos específicos.

**Tabla:** `logs_usuarios`
- **Módulo:** Auditoría
- **Columnas:**
  - `id` (PK, int): Identificador único del log.
  - `usuario_id` (FK a usuarios): Usuario que realizó la acción.
  - `accion` (varchar): Acción realizada.
  - `modulo` (varchar): Módulo donde se realizó la acción.
  - `fecha_hora` (datetime): Fecha y hora de la acción.
  - `detalle` (varchar): Detalles adicionales de la acción.
  - `ip_origen` (varchar): Dirección IP desde donde se realizó la acción.
- **Uso:** Registro de acciones de los usuarios para auditoría.

---

## Configuración

**Tabla:** `configuracion`
- **Módulo:** Configuración
- **Columnas:**
  - `id` (PK, int)
  - `clave` (varchar)
  - `valor` (varchar)
  - `descripcion` (varchar)
- **Uso:** Almacenamiento de parámetros críticos y configuración dinámica.

---

## Actualización: Base de Datos por Tabla

### Obras
**Base de Datos:** `obras`
- **Tabla:** `obras`
- **Tabla:** `historial_estados`

### Inventario
**Base de Datos:** `inventario`
- **Tabla:** `inventario`
- **Tabla:** `movimientos_inventario`
- **Tabla:** `vidrios_por_obra`
- **Tabla:** `herrajes_por_obra`

### Herrajes
**Base de Datos:** `herrajes`
- **Tabla:** `herrajes`
- **Tabla:** `pedidos_herrajes`

### Vidrios
**Base de Datos:** `vidrios`
- **Tabla:** `vidrios`
- **Tabla:** `pedidos_vidrios`

### Pedidos de Materiales
**Base de Datos:** `pedidos`
- **Tabla:** `pedidos_materiales`
- **Tabla:** `pedidos_material`
- **Tabla:** `reservas_stock`
- **Tabla:** `detalle_pedido`

### Usuarios y Auditoría
**Base de Datos:** `users`
- **Tabla:** `usuarios`
- **Tabla:** `permisos_modulos`
- **Tabla:** `notificaciones`

**Base de Datos:** `auditoria`
- **Tabla:** `auditoria`
- **Tabla:** `logs_usuarios`

### Configuración
**Base de Datos:** `configuracion`
- **Tabla:** `configuracion`

---

## Relaciones entre Tablas y Flujo de Datos

### Relaciones Clave entre Tablas

1. **Obras y su Historial de Estados**:
   - La tabla `obras` se relaciona con `historial_estados` mediante la columna `id` de `obras` y `id_obra` de `historial_estados`.
   - Uso: Permite rastrear los cambios de estado de una obra a lo largo del tiempo.

2. **Inventario y Movimientos de Inventario**:
   - La tabla `inventario` se relaciona con `movimientos_inventario` mediante la columna `id` de `inventario` y `id_material` de `movimientos_inventario`.
   - Uso: Proporciona trazabilidad de entradas, salidas y reservas de materiales.

3. **Usuarios y Auditoría**:
   - La tabla `usuarios` se relaciona con `auditoria` mediante la columna `id` de `usuarios` y `usuario` de `auditoria`.
   - Uso: Registro de acciones realizadas por los usuarios en el sistema.

4. **Pedidos y Detalles de Pedidos**:
   - La tabla `pedidos_materiales` se relaciona con `detalle_pedido` mediante la columna `id` de `pedidos_materiales` y `id_pedido` de `detalle_pedido`.
   - Uso: Almacenar los ítems solicitados en cada pedido.

### Flujo de Datos entre Módulos

1. **Gestión de Obras**:
   - Los datos de `obras` se integran con `pedidos_materiales`, `vidrios_por_obra` y `herrajes_por_obra` para gestionar los materiales requeridos.
   - El estado de las obras se actualiza en `historial_estados` para mantener trazabilidad.

2. **Control de Inventario**:
   - Los movimientos de inventario (`movimientos_inventario`) se generan a partir de pedidos (`pedidos_materiales`) y reservas (`reservas_stock`).

3. **Auditoría y Seguridad**:
   - Todas las acciones de los usuarios se registran en `auditoria` y `logs_usuarios` para garantizar trazabilidad y seguridad.

### Ejemplos de Consultas SQL

1. **Obtener el historial de estados de una obra específica**:
   ```sql
   SELECT h.estado, h.fecha_cambio, h.detalles
   FROM historial_estados h
   INNER JOIN obras o ON h.id_obra = o.id
   WHERE o.nombre = 'Obra Ejemplo';
   ```

2. **Consultar el stock disponible de un material específico**:
   ```sql
   SELECT nombre, stock, ubicacion
   FROM inventario
   WHERE nombre = 'Material Ejemplo';
   ```

3. **Listar las acciones realizadas por un usuario en un módulo específico**:
   ```sql
   SELECT a.fecha, a.accion, a.detalle
   FROM auditoria a
   INNER JOIN usuarios u ON a.usuario = u.id
   WHERE u.nombre = 'Usuario Ejemplo' AND a.modulo = 'Inventario';
   ```

### Diagramas de Relaciones

Se recomienda utilizar herramientas como [dbdiagram.io](https://dbdiagram.io) o similares para generar diagramas visuales de las relaciones entre tablas. Esto facilitará la comprensión de la estructura y el flujo de datos.

---

**Notas:**
- Todas las claves foráneas (`FK`) deben estar correctamente definidas y referenciar las tablas correspondientes.
- Los tipos de datos pueden variar según el motor de base de datos (ajustar según SQL Server, MySQL, etc.).
- Si algún módulo requiere tablas adicionales (por ejemplo, historial, logs, relaciones N a N), documentar aquí y en el modelo correspondiente.

---

**Este archivo debe mantenerse actualizado tras cada cambio en los modelos o la base de datos.**
