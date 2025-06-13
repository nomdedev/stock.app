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
- **Uso:** Gestión central de obras, integración con pedidos, producción, logística y contabilidad.

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

---

## Producción

**Tabla:** `produccion`
- **Módulo:** Producción
- **Columnas:**
  - `id` (PK, int)
  - `id_obra` (FK a obras)
  - `estado` (varchar)
  - `fecha_inicio` (datetime)
  - `fecha_fin` (datetime)
  - `responsable` (FK a usuarios)
- **Uso:** Seguimiento de avance de producción por obra.

---

## Logística

**Tabla:** `logistica`
- **Módulo:** Logística
- **Columnas:**
  - `id` (PK, int)
  - `id_obra` (FK a obras)
  - `fecha_entrega` (datetime)
  - `transportista` (varchar)
  - `estado` (varchar)
  - `observaciones` (text)
- **Uso:** Gestión de entregas y movimientos logísticos.

---

## Contabilidad

**Tabla:** `facturas`
- **Módulo:** Contabilidad
- **Columnas:**
  - `id` (PK, int)
  - `id_obra` (FK a obras)
  - `monto` (decimal)
  - `fecha` (datetime)
  - `estado` (varchar)
  - `usuario` (FK a usuarios)
- **Uso:** Registro y control de facturación.

**Tabla:** `pagos`
- **Módulo:** Contabilidad
- **Columnas:**
  - `id` (PK, int)
  - `id_factura` (FK a facturas)
  - `monto` (decimal)
  - `fecha` (datetime)
  - `usuario` (FK a usuarios)
- **Uso:** Seguimiento de pagos.

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

**Notas:**
- Todas las claves foráneas (`FK`) deben estar correctamente definidas y referenciar las tablas correspondientes.
- Los tipos de datos pueden variar según el motor de base de datos (ajustar según SQL Server, MySQL, etc.).
- Si algún módulo requiere tablas adicionales (por ejemplo, historial, logs, relaciones N a N), documentar aquí y en el modelo correspondiente.

---

**Este archivo debe mantenerse actualizado tras cada cambio en los modelos o la base de datos.**
