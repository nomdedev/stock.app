## Instrucciones de Instalación y Configuración

### Requisitos Previos
- Python 3.8 o superior
- PostgreSQL 12 o superior
- Librería `pyodbc` para la conexión a SQL Server.
- Controlador ODBC para SQL Server (recomendado: **ODBC Driver 17 for SQL Server**).

### Pasos para la Instalación
1. Clonar el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd stock.admin
   ```

2. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate
   ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

   Asegúrate de que `pyodbc` esté incluido en el archivo `requirements.txt`. Si no, instálalo manualmente:
   ```bash
   pip install pyodbc
   ```

4. Instalar el controlador ODBC para SQL Server:
   - Descarga e instala el controlador desde [Microsoft ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).

5. Configurar la base de datos:
   - Crear las bases de datos necesarias ejecutando el script `MPS_SQL_COMPLETO_SIN_PREFIJOS.sql` en PostgreSQL.
   - Configurar las credenciales de la base de datos en el archivo `core/database.py`.

6. Ejecutar el proyecto:
   ```bash
   python main.py
   ```

### Configuración de Variables Globales

El sistema permite configurar variables globales desde el archivo `core/config.py` o desde el módulo de configuración en la aplicación.

### Variables Disponibles

#### Conexión a la Base de Datos
- **DB_SERVER**: Dirección o IP del servidor SQL.
- **DB_USERNAME**: Usuario de la base de datos.
- **DB_PASSWORD**: Contraseña del usuario.
- **DB_PORT**: Puerto del servidor SQL (por defecto: 1433).
- **DB_DEFAULT_DATABASE**: Base de datos predeterminada.
- **DB_TIMEOUT**: Tiempo de espera para la conexión (en segundos).

#### Configuración General
- **DEBUG_MODE**: Activar o desactivar modo de depuración.
- **FILE_STORAGE_PATH**: Ruta para almacenar archivos generados.
- **DEFAULT_LANGUAGE**: Idioma predeterminado de la aplicación.
- **DEFAULT_TIMEZONE**: Zona horaria predeterminada.
- **NOTIFICATIONS_ENABLED**: Activar o desactivar notificaciones globales.

### Edición desde la Aplicación
Estas configuraciones también pueden ser modificadas desde el módulo de configuración, en las pestañas "General" y "Base de Datos".

### Configuración de Conexión a la Base de Datos

El archivo `core/config.py` contiene información sensible como credenciales de la base de datos. **No debe subirse al repositorio**. Asegúrate de que esté incluido en el archivo `.gitignore`.

Si necesitas compartir configuraciones genéricas, utiliza un archivo de ejemplo como `config.example.py` y excluye las credenciales reales.

Para configurar las credenciales de conexión a la base de datos, edita el archivo `core/config.py` y define los valores correspondientes:

```python
# filepath: c:\Users\Escorpio\Desktop\Martin\Proyectos\stock.app\core\config.py
DB_SERVER = "192.168.1.100"  # Dirección o IP del servidor SQL
DB_USERNAME = "sa"           # Usuario de la base de datos
DB_PASSWORD = "mps.1887"     # Contraseña del usuario
```

### Notas:
- Asegúrate de que el servidor SQL permita conexiones remotas.
- Si cambias el puerto predeterminado (1433), incluye el puerto en `DB_SERVER`, por ejemplo: `"192.168.1.100,1434"`.
- No compartas este archivo públicamente, ya que contiene información sensible.

### Configuración Inicial
- Crear un usuario administrador desde el módulo de usuarios.
- Configurar los parámetros iniciales en el módulo de configuración.

### Notas sobre la Conexión a la Base de Datos
El sistema ahora utiliza `pyodbc` para conectarse a SQL Server. Asegúrate de que el controlador ODBC esté instalado y configurado correctamente.

## Bases de Datos y Tablas Existentes

### Bases de Datos
1. **mps.app-inventario**
2. **mps.app-users**

---

### Tablas en `mps.app-inventario`
- **dbo.estado_herrajes**: Estado de los herrajes.
- **dbo.historial**: Historial de movimientos o cambios.
- **dbo.inventario**: Inventario general de herrajes.
- **dbo.herrajes**: Detalles de los herrajes.
- **dbo.herrajes_proveedores**: Relación entre herrajes y proveedores.
- **dbo.movimientos_inventario**: Movimientos registrados en el inventario.
- **dbo.obras**: Información de las obras.
- **dbo.obras_materiales**: Relación entre obras y herrajes asignados.
- **dbo.obra_materiales**: Detalles específicos de herrajes por obra.
- **dbo.pedidos**: Pedidos realizados (ahora gestionados dentro del módulo Compras).
- **dbo.pedidos_pendientes**: Pedidos que aún no han sido completados (parte del módulo Compras).
- **dbo.pedidos_por_obra**: Pedidos relacionados con obras específicas.
- **dbo.perfiles_por_obra**: Perfiles asignados a obras.
- **dbo.proveedores**: Información de los proveedores.

---

### Tablas en `mps.app-users`
- **dbo.usuarios**: Información de los usuarios registrados.

---

### Conexión persistente a la Base de Datos

- Todas las operaciones de base de datos utilizan ahora la clase `BaseDatabaseConnection` y sus derivadas para mantener una única conexión persistente.
- Se ha descontinuado el uso de la clase `DatabaseConnection`, que abría y cerraba conexiones por cada consulta.
- Cada módulo debe instanciar su propia conexión específica (por ejemplo, `InventarioDatabaseConnection`, `ObrasDatabaseConnection`, etc.).
- Esto evita conexiones duplicadas, reduce la sobrecarga y mejora el rendimiento general del sistema.

---

### Notas Importantes
1. **Nombres de Tablas**: Solo se deben usar los nombres de tablas existentes. No se deben crear tablas con nombres diferentes sin previa consulta y aprobación.
2. **Creación de Nuevas Tablas**: Si se necesita crear una nueva tabla, consulta primero y espera la aprobación antes de proceder.
3. **Consistencia**: Asegúrate de que las consultas y operaciones en la base de datos utilicen los nombres exactos de las tablas listadas aquí.

---

Si necesitas agregar más información o realizar cambios en las bases de datos, por favor consulta con el equipo antes de proceder.

## Resumen de Flujo, Estructura y Relaciones de Datos (2025)

### Estructura General del Sistema
- **Arquitectura modular**: cada módulo (Inventario, Obras, Usuarios, Logística, Compras, etc.) tiene su propio modelo, vista y controlador.
- **Conexión a base de datos centralizada**: se crea una única conexión persistente por base de datos y se inyecta en los modelos, evitando conexiones redundantes.
- **Auditoría y permisos**: todas las acciones relevantes pasan por un decorador que valida permisos y registra auditoría.
- **Interfaz visual unificada**: cada módulo tiene un solo botón principal de acción, con icono SVG y sombra, y el sidebar es visual y minimalista.

### Flujo de Trabajo Digitalizado
1. **Inventario**: permite alta, ajuste, reserva y consulta de materiales/herrajes. Cada movimiento queda registrado en auditoría.
2. **Obras**: permite crear obras, asociar materiales, y visualizar el cronograma tipo Kanban. El usuario puede agregar obras, asignar materiales y ver el estado de avance.
3. **Asociación de materiales a obras**: desde el módulo Obras, se pueden asignar materiales a cada obra, especificando cantidades y estado. Esto se refleja en la tabla `materiales_por_obra`.
4. **Cronograma Kanban**: cada obra tiene una fecha de medición y una fecha de entrega (editable, por defecto 90 días). El Kanban muestra visualmente el avance y permite identificar fechas clave.
5. **Exportación y reportes**: los módulos permiten exportar datos a Excel y PDF.
6. **Gestión de usuarios y permisos**: los roles definen qué acciones puede realizar cada usuario.

### Principales Tablas y Relaciones
- **inventario_items**: ítems/materiales disponibles en stock.
- **movimientos_stock**: historial de movimientos de stock (ingresos, egresos, ajustes, reservas).
- **reservas_stock**: reservas de materiales para obras.
- **obras**: datos principales de cada obra (nombre, cliente, estado, fecha de medición, fecha de entrega).
- **materiales_por_obra**: relación N a N entre obras y materiales, con cantidades y estado.
- **cronograma_obras**: etapas y fechas programadas/realizadas para cada obra.
- **usuarios**: usuarios del sistema y sus roles.
- **auditorias_sistema**: registro de todas las acciones relevantes.

#### Relación de datos clave
- Una obra puede tener muchos materiales asociados (`materiales_por_obra`).
- Cada material puede estar asociado a muchas obras.
- El cronograma de cada obra se almacena en `cronograma_obras`.
- Los movimientos de stock y reservas se vinculan a obras y usuarios.

### Lógica de Asociación y Cronograma
- Al crear una obra, se puede definir la fecha de entrega (por defecto 90 días desde la medición, editable).
- Al asignar materiales, se crea un registro en `materiales_por_obra`.
- El Kanban se alimenta de la tabla `obras` y muestra nombre, cliente, fecha de medición y fecha de entrega.
- El usuario puede editar la fecha de entrega y los materiales asociados desde la interfaz.

### Ejemplo de SQL relevante
```sql
CREATE TABLE obras (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    cliente VARCHAR(100),
    estado VARCHAR(50),
    fecha DATE, -- fecha de medición
    fecha_entrega DATE -- fecha de entrega (editable)
);

CREATE TABLE materiales_por_obra (
    id SERIAL PRIMARY KEY,
    id_obra INT REFERENCES obras(id),
    id_item INT,
    cantidad_necesaria DECIMAL,
    cantidad_reservada DECIMAL,
    estado VARCHAR(30)
);
```

### Notas sobre la implementación
- El sistema evita conexiones redundantes a la base de datos.
- Todas las acciones importantes quedan registradas en auditoría.
- El flujo de trabajo es digital, modular y auditable.
- La interfaz es moderna, con botones principales únicos y sidebar visual.

---

## MUSTS del proyecto

- **Sincronización automática de columnas:**  
  Todas las vistas que muestran datos de tablas SQL deben obtener los headers (nombres de columnas) automáticamente desde la base de datos al iniciar.  
  No se deben definir headers manualmente en el código, salvo fallback temporal.  
  Si la estructura de la tabla cambia, la vista debe reflejarlo automáticamente.

- **Persistencia de configuración de columnas por usuario:**  
  Cada usuario puede elegir qué columnas ver u ocultar en las tablas.  
  Esta configuración se guarda (por ejemplo, en un archivo JSON) y se restaura automáticamente en la próxima sesión del usuario.

- **Prohibido desincronizar headers:**  
  No puede haber desincronización entre los headers de la vista y los de la tabla SQL.  
  Si se modifica la estructura de una tabla, la vista debe actualizarse automáticamente.

- **Nombres y orden de columnas:**  
  Los nombres y el orden de las columnas en la vista deben coincidir exactamente con los de la tabla SQL correspondiente.

- **Ejemplo de obtención dinámica de headers:**
  ```python
  # Ejemplo para obtener headers desde la base de datos
  query = "SELECT TOP 0 * FROM inventario_perfiles"
  cursor.execute(query)
  headers = [column[0] for column in cursor.description]
  ```

- **Tabla principal del módulo inventario:**  
  Al ingresar al módulo inventario, se debe mostrar la tabla `inventario_perfiles` con los siguientes headers (columnas):

  ```
  id, codigo, descripcion, tipo, acabado, numero, vs, proveedor,
  longitud, ancho, alto, necesarias, stock, faltan, ped_min, emba, pedido, importe
  ```

> **Estas reglas son obligatorias para todos los módulos y vistas del proyecto.**

## Requerimiento obligatorio de tablas

Todas las tablas del sistema (QTableWidget) deben permitir:
- Mostrar/ocultar columnas mediante menú contextual en el encabezado.
- Ajustar el ancho de columnas manualmente y autoajustar con doble clic.
- Persistir las preferencias de visibilidad y ancho de columnas por usuario/sesión (archivo JSON).

Este patrón debe aplicarse a todos los módulos que presenten tablas.

---

## Patrón universal de tablas responsive (QTableWidget)

Todas las tablas principales de la aplicación (QTableWidget) deben aplicar el mixin `TableResponsiveMixin` y el método `make_table_responsive` para garantizar que la tabla se expanda y adapte correctamente al modo fullscreen o maximizado, tanto en ancho como en alto.

**Ejemplo de uso:**

```python
from core.table_responsive_mixin import TableResponsiveMixin

class MiVista(QWidget, TableResponsiveMixin):
    def __init__(self):
        super().__init__()
        self.tabla = QTableWidget()
        self.make_table_responsive(self.tabla)
        # ...
```

Esto asegura una experiencia de usuario moderna y consistente en todos los módulos.

---

## Integración UI + Base de Datos: verificación automática

Cada operación relevante sobre datos (agregar, editar, eliminar, exportar, etc.) debe reflejarse tanto en la base de datos como en la UI (tabla principal). Esto se verifica mediante tests de integración automáticos que:

- Simulan operaciones sobre el modelo (mock DB).
- Simulan la actualización de la tabla en la vista (mock UI).
- Verifican que los datos insertados/actualizados/eliminados aparecen correctamente en ambos lugares.

**Ejemplo de test de integración:**

```python
class MockDBConnection:
    # ... implementación ...

class MockVista:
    def actualizar_tabla(self, data):
        self.tabla_data = data

class TestModuloIntegracion(unittest.TestCase):
    def setUp(self):
        self.mock_db = MockDBConnection()
        self.model = MiModelo(self.mock_db)
        self.view = MockVista()
    def test_agregar_y_reflejar(self):
        self.model.agregar_algo(datos)
        items = self.mock_db.ejecutar_query("SELECT * FROM tabla")
        self.view.actualizar_tabla(items)
        self.assertEqual(self.view.tabla_data, items)
```

Este patrón es obligatorio para todos los módulos y garantiza robustez y trazabilidad en la experiencia del usuario y la integridad de los datos.

---

## Módulo Contabilidad

El módulo de Contabilidad centraliza la gestión financiera y administrativa del sistema, permitiendo un control integral de movimientos, pagos y recibos asociados a las obras y operaciones generales.

### Mejoras técnicas y de UX implementadas

- **Sincronización dinámica de headers**: Las tablas de Balance y Recibos obtienen sus columnas directamente de la base de datos, adaptándose automáticamente a cambios en la estructura.
- **Selector de obra en formularios**: Al agregar un recibo o movimiento, se utiliza un selector desplegable que muestra todas las obras disponibles, facilitando la asociación precisa.
- **Filtros y búsqueda rápida**: Todas las tablas del módulo (Balance, Pagos, Recibos) cuentan con un campo de búsqueda rápida que filtra resultados en tiempo real por cualquier columna.
- **Mejoras visuales y tooltips**: Botones de acción flotantes, tooltips descriptivos y estilos modernos aseguran una experiencia clara y profesional.
- **Alta de recibos**: El botón para agregar recibo está en la esquina superior derecha de la pestaña Recibos. Al pulsarlo, se abre un diálogo con los campos requeridos y un selector de obra. El recibo se persiste en la base de datos y se refleja inmediatamente en la tabla.
- **Persistencia y actualización**: Todos los cambios (alta de recibos, movimientos, etc.) se reflejan en la base de datos y en la interfaz de manera inmediata.

### Pestañas principales

1. **Balance General (Entradas y Salidas)**
   - Tabla con todos los movimientos de dinero (ingresos y egresos), con columna de tipo (entrada/salida).
   - Botón flotante para agregar movimiento: abre ventana para registrar ingreso o salida, con selector de obra, campos requeridos y persistencia automática.
   - Exportar a Excel/PDF, menú de columnas, QR, filtros y búsqueda rápida.

2. **Seguimiento de Pagos por Obra**
   - Tabla con estado de pagos de cada obra: monto total, pagado, pendiente, monto para colocador, etc.
   - Integración con otras tablas para obtener datos de obras y pagos.
   - Permite agregar o actualizar pagos realizados.
   - Filtros, exportación, menú de columnas, QR, etc.

3. **Recibos**
   - Tabla con todos los recibos generados, mostrando datos clave (obra, monto, concepto, destinatario, fecha, estado).
   - Botón flotante para agregar recibo (esquina superior derecha): abre diálogo con selector de obra y campos requeridos.
   - Opción de imprimir o guardar el recibo como PDF.
   - Exportación, menú de columnas, QR, filtros y búsqueda rápida.

4. **Estadísticas**
   - Gráfico de barras de ingresos vs egresos (Entradas vs Salidas).
   - Resumen de totales: entradas, salidas y saldo neto.
   - Preparado para filtros por fecha, obra y tipo de movimiento.
   - Visualización moderna y tooltips.

### Integración con Obras

- Desde el módulo Obras, cualquier usuario puede cargar una nueva obra (sin restricciones de permisos para alta de obra).
- Los movimientos y recibos pueden asociarse a obras existentes mediante el selector en los formularios.

### Estándar UX en Tablas

- Todas las tablas del módulo incluyen:
  - Menú de columnas (mostrar/ocultar).
  - Persistencia de configuración de columnas.
  - Ajuste de ancho de columnas.
  - Exportar a Excel/PDF.
  - Visualización de QR al seleccionar fila.
  - Filtros y búsqueda rápida.
  - Tooltips y feedback visual en acciones.

---

## Contabilidad

El módulo de Contabilidad cuenta con una interfaz de pestañas (QTabWidget) con las siguientes secciones:

- **Balance**: muestra todos los movimientos de entrada y salida de dinero. Permite agregar nuevos movimientos mediante un diálogo y persiste los datos en la base de datos.
- **Seguimiento de Pagos**: permite visualizar el estado de pagos por obra, montos adeudados, montos pagados y detalles por colocador. Los datos se obtienen de las tablas relacionadas.
- **Recibos**: muestra todos los recibos, permite agregar nuevos recibos mediante un formulario, y generar/guardar/imprimir el PDF del recibo seleccionado.
- **Estadísticas**: proporciona visualizaciones gráficas de ingresos vs egresos, resumen de totales y filtros avanzados.

Todas las tablas de este módulo implementan el patrón UX universal:
- Menú de mostrar/ocultar columnas (clic izquierdo en el encabezado)
- Persistencia de preferencias de columnas por usuario/sesión
- Ajuste manual y automático de ancho de columnas
- Generación y visualización de código QR al seleccionar una fila (con opción de guardar/imprimir como PDF)

**Requisito obligatorio:** Este patrón UX es obligatorio y debe estar presente en todos los módulos que utilicen QTableWidget.

---

## Flujo de integración e interacción entre módulos (estilo SAP)

### Visión general del flujo

1. **Inventario**
   - Alta, ajuste, reserva y consulta de materiales/herrajes.
   - Cada movimiento (alta, ajuste, reserva, entrega, eliminación) queda registrado en auditoría.
   - Las reservas y entregas de materiales impactan en Obras y Logística.
   - Exportación de inventario y generación de QR disponibles.

2. **Obras**
   - Creación y edición de obras, asignación de materiales desde Inventario.
   - El avance de obra (Kanban) depende de la disponibilidad y entrega de materiales.
   - Los cambios de estado de obra (medición, producción, colocación, finalizada) se reflejan en Logística y Contabilidad.
   - Toda acción relevante se audita.

3. **Logística**
   - Planificación y registro de entregas de materiales a obras.
   - El estado de las entregas depende de la reserva y disponibilidad en Inventario.
   - Al finalizar una entrega, se actualiza el stock y se registra en auditoría.
   - Generación de actas de entrega y exportación a PDF.

4. **Compras y Pedidos**
   - Generación de pedidos de compra cuando el stock es insuficiente.
   - Los pedidos impactan en Inventario al ser recibidos.
   - Auditoría de todo el ciclo de compra y recepción.

5. **Contabilidad**
   - Registro de movimientos financieros asociados a obras y compras.
   - Los pagos y recibos se asocian a obras y quedan disponibles para consulta cruzada.

6. **Usuarios y Permisos**
   - Control de acceso a acciones críticas mediante roles y permisos.
   - Todo intento de acción sin permiso queda registrado y muestra feedback visual.

7. **Auditoría**
   - Registro centralizado de todas las acciones relevantes de todos los módulos.
   - Permite filtrar por usuario, módulo, fecha y tipo de acción.

8. **Mantenimiento, Notificaciones, Herrajes, Vidrios, Configuración**
   - Integrados al flujo general: cualquier acción relevante (alta, edición, exportación, mantenimiento programado, notificación enviada, etc.) se audita y puede impactar en Inventario, Obras o Logística según el caso.

### Ejemplo de interacción típica entre módulos

- Un usuario reserva materiales en Inventario para una obra → se crea una reserva, se descuenta stock, se registra en auditoría y se refleja en la vista de Obras.
- Logística programa la entrega de esos materiales → al finalizar la entrega, se actualiza el estado en Inventario y Obras, y se genera un acta de entrega.
- Si falta stock, Compras genera un pedido → al recibir el pedido, se actualiza Inventario y se notifica a Obras y Logística.
- Todo el ciclo queda registrado en Auditoría y puede ser consultado por usuario, obra o material.

### Diagrama de flujo de integración

![Diagrama de flujo de integración](img/diagrama-de-flujo-detallado.png)

---

> **Este flujo asegura que cada módulo no es un silo, sino parte de un sistema integrado, donde cada acción tiene impacto y trazabilidad global, replicando la lógica de integración de SAP.**

---

## Flujo de integración e interacción entre módulos (estilo SAP)

### Visión general
El sistema está diseñado para que todos los módulos interactúen de forma integrada, con trazabilidad y feedback visual en cada paso. Cada acción relevante en un módulo puede impactar en otros, y todo queda registrado en auditoría. El flujo es digital, auditable y visualmente unificado.

### Ejemplo de flujo típico y relaciones entre módulos

1. **Alta de obra (Obras)**
   - El usuario crea una nueva obra desde el módulo Obras.
   - Se registra en la tabla `obras` y se audita la acción.
   - La obra queda disponible para ser seleccionada en otros módulos (Inventario, Logística, Contabilidad, Pedidos).

2. **Asignación de materiales a obra (Obras ↔ Inventario)**
   - Desde Obras, se asignan materiales/perfiles a la obra (tabla `materiales_por_obra`).
   - El sistema consulta el stock en Inventario y permite reservar materiales.
   - Si hay stock suficiente, se descuenta y se registra el movimiento en Inventario (`movimientos_stock` y `reservas_stock`).
   - Si falta stock, se genera una reserva pendiente y puede disparar un pedido de compra (módulo Compras).
   - Todo el proceso queda auditado.

3. **Reserva y entrega de materiales (Inventario ↔ Logística ↔ Obras)**
   - Cuando se reserva material para una obra, Logística puede programar la entrega (tabla `entregas_obras`).
   - El estado de la entrega se refleja en la obra y en el inventario.
   - El usuario puede ver el avance y los pendientes desde Obras y Logística.

4. **Pedidos y compras (Obras/Inventario ↔ Compras)**
   - Si hay faltantes, el sistema permite generar un pedido desde Inventario o desde Obras.
   - El pedido se gestiona en Compras, y al recibir el material, se actualiza el stock y se notifica a los módulos involucrados.
   - Todo el ciclo queda registrado y auditado.

5. **Movimientos contables y recibos (Obras ↔ Contabilidad)**
   - Los movimientos de avance de obra, pagos y cobros se reflejan en Contabilidad.
   - Los recibos y movimientos contables se asocian a obras y quedan disponibles para consulta cruzada.

6. **Auditoría y permisos (Todos los módulos)**
   - Cada acción relevante (alta, edición, reserva, entrega, exportación, cambio de estado, etc.) queda registrada en el módulo de Auditoría, con usuario, fecha, IP y detalle.
   - Los permisos se validan en cada acción sensible, y los intentos fallidos también se auditan.

7. **Feedback visual y sincronización (Todos los módulos)**
   - Cada acción muestra feedback inmediato y claro en la UI (barra de estado, mensajes, tooltips, colores por tipo de mensaje/rol).
   - Las tablas se sincronizan dinámicamente con la base de datos y persisten la configuración de columnas por usuario.
   - Los cambios en un módulo se reflejan en tiempo real en los módulos relacionados.

### Diagrama de flujo y navegación
- Ver `img/diagrama-de-flujo-detallado.png` para el diagrama visual de integración.
- El usuario puede navegar entre módulos y ver el impacto de cada acción en tiempo real.

### Resumen de integración
- **Obras** es el eje central: conecta con Inventario, Logística, Compras y Contabilidad.
- **Inventario** gestiona stock y reservas, y se integra con Obras, Compras y Logística.
- **Logística** coordina entregas y refleja el estado en Obras e Inventario.
- **Compras** gestiona pedidos y abastece Inventario y Obras.
- **Contabilidad** refleja los movimientos económicos asociados a Obras y Pedidos.
- **Auditoría** y **Permisos** son transversales a todo el sistema.

> **Este flujo integrado garantiza trazabilidad, robustez y una experiencia SAP-like, donde cada módulo es parte de un todo y la información fluye de manera transparente y auditable.**

---

## Visión SAP: Integración Total y Experiencia Unificada

### Objetivo: Un sistema integrado, robusto y auditable, con experiencia SAP

El objetivo de este sistema es lograr una integración total de todos los módulos (Inventario, Obras, Logística, Producción, Compras, Usuarios, Auditoría, Mantenimiento, Notificaciones, Herrajes, Vidrios, Configuración, Contabilidad, Pedidos) bajo una experiencia unificada y robusta, similar a SAP. Esto implica:

- **Integración real de datos y flujos**: Todas las acciones y movimientos de cada módulo impactan y se reflejan en los demás módulos relevantes, garantizando trazabilidad y consistencia global.
- **Auditoría centralizada**: Cada acción relevante (alta, edición, eliminación, exportación, reserva, entrega, cambio de estado, etc.) queda registrada en el módulo de auditoría, con usuario, fecha, IP y detalle.
- **Permisos y roles**: Todas las acciones sensibles están protegidas por validación de permisos (decorador PermisoAuditoria), con feedback visual claro y registro de intentos fallidos.
- **Feedback visual y UX consistente**: Todas las acciones muestran feedback inmediato y claro en la UI (barra de estado, mensajes, tooltips, colores por tipo de mensaje/rol), siguiendo el estándar visual moderno (botones 32x32, icono 20x20, label de usuario estilizado).
- **Sincronización dinámica de tablas**: Todas las tablas obtienen headers y estructura directamente de la base de datos, y persisten la configuración de columnas por usuario.
- **Exportación y QR**: Todos los módulos con datos tabulares permiten exportar a Excel/PDF y generar códigos QR donde aplique.
- **Robustez ante errores**: El sistema nunca crashea por errores de base de datos; muestra avisos claros y mantiene la funcionalidad posible.
- **Pruebas automáticas**: Cada módulo cuenta con tests unitarios e integración que verifican la correcta integración UI+DB, feedback visual y registro en auditoría.
- **Checklist y documentación**: Cada módulo tiene checklist funcional y visual, y la documentación describe flujos, permisos, feedback, integración y casos de error.

### Estándares visuales y de feedback (UX SAP-like)
- Todos los botones principales de acción usan el utilitario `estilizar_boton_icono` (icono SVG 20x20, botón 32x32, estilo moderno, padding y border-radius).
- El label de usuario en la barra de estado muestra color y borde según el rol, con fondo sutil y tipografía moderna.
- Todos los mensajes de feedback usan el método `mostrar_mensaje`, con colores y duración según tipo (info, éxito, advertencia, error).
- Tooltips descriptivos y consistentes en todos los botones y acciones.
- Las tablas usan el mixin `TableResponsiveMixin` y persisten configuración de columnas y anchos por usuario.

### Integración y trazabilidad total (estilo SAP)
- Cada alta, edición, reserva, entrega, exportación, etc. se refleja en la base de datos, la UI y el log de auditoría.
- Los cambios en inventario impactan en obras, logística y pedidos; los movimientos de obras se reflejan en contabilidad y logística; los cambios de usuarios y permisos se auditan y afectan la experiencia global.
- El sistema permite navegar entre módulos y ver el impacto de cada acción en tiempo real, con feedback visual y trazabilidad completa.

### Pruebas y checklist de integración
- Todos los módulos cuentan con tests de integración que simulan operaciones y verifican reflejo en UI, DB y auditoría.
- El archivo `cosas por hacer.txt` y los docstrings de cada modelo/controlador mantienen el checklist actualizado.
- El README documenta los flujos, casos de error, feedback visual, integración y estándares SAP-like.

---

> **Este sistema busca replicar la robustez, integración y experiencia de usuario de SAP, adaptado a la realidad PyQt6 y a la gestión de inventarios, obras y logística. Cada módulo es parte de un todo integrado, auditable y visualmente moderno.**

---

## Ejemplo de ciclo completo de integración entre módulos

A continuación se describe un flujo típico de trabajo que atraviesa varios módulos, mostrando cómo cada acción impacta en el sistema y cómo se refleja en la UI, la base de datos y la auditoría, siguiendo la lógica SAP-like:

### 1. Reserva de material desde Inventario para una obra
- El usuario selecciona un material en el módulo Inventario y realiza una reserva para una obra específica.
- El sistema valida stock, descuenta la cantidad reservada y registra la reserva en la tabla `reservas_materiales`.
- Se muestra feedback visual inmediato (mensaje de éxito o advertencia) y se actualiza la tabla en la UI.
- Se registra la acción en el módulo de Auditoría (usuario, acción, cantidad, obra, fecha, IP).
- La reserva queda visible en el módulo Obras (materiales pendientes de entrega).

### 2. Programación y entrega desde Logística
- Logística visualiza las reservas pendientes asociadas a obras.
- Se programa la entrega de los materiales reservados.
- Al finalizar la entrega, se actualiza el estado de la reserva y se descuenta el stock real en Inventario.
- Se genera un acta de entrega (PDF) y se registra la acción en Auditoría.
- El estado de la obra se actualiza automáticamente si se completan todas las entregas.

### 3. Recepción de materiales por Compras
- Si el stock es insuficiente, el sistema sugiere generar un pedido de compra desde Compras.
- Al recibir el pedido, se actualiza el stock en Inventario y se notifica a Obras y Logística.
- Todo el ciclo de compra queda registrado en Auditoría.

### 4. Impacto en Contabilidad
- Los movimientos de materiales y entregas se reflejan en los costos de obra y en los reportes de Contabilidad.
- Los pagos a proveedores y recibos asociados quedan vinculados a la obra y al movimiento de materiales.
- Exportación de balances y reportes disponible.

### 5. Auditoría y trazabilidad
- Cada paso (reserva, entrega, compra, pago) queda registrado en el módulo de Auditoría.
- Se puede consultar el historial completo por usuario, obra, material o módulo.
- Los intentos fallidos (por permisos, errores, etc.) también quedan registrados y muestran feedback visual.

---

> **Este ejemplo ilustra cómo el sistema integra todos los módulos en un flujo continuo, con trazabilidad, feedback visual y robustez, asegurando que cada acción tenga impacto real y auditable en todo el sistema.**

---

## Tabla resumen de impactos cruzados entre módulos

| Módulo origen   | Acción/Evento                | Módulos impactados         | Efecto/Reflejo principal                                                                                 |
|-----------------|------------------------------|----------------------------|---------------------------------------------------------------------------------------------------------|
| Inventario      | Reserva de material          | Obras, Logística, Auditoría| Reserva registrada, stock descontado, visible en Obras y Logística, auditado                            |
| Inventario      | Ajuste/entrega de stock      | Obras, Logística, Auditoría| Stock actualizado, entregas reflejadas en Obras y Logística, auditado                                    |
| Inventario      | Baja/alta de material        | Obras, Auditoría           | Material disponible/no disponible para asignar a obras, auditado                                         |
| Obras           | Cambio de estado (Kanban)    | Logística, Contabilidad, Auditoría| Estado de obra actualizado, puede disparar entregas o pagos, auditado                           |
| Obras           | Asignación de materiales     | Inventario, Logística, Auditoría| Reserva automática en Inventario, visible en Logística, auditado                                  |
| Logística       | Programar/finalizar entrega  | Inventario, Obras, Auditoría| Stock descontado, estado de obra actualizado, acta de entrega generada, auditado                        |
| Compras         | Pedido recibido              | Inventario, Obras, Auditoría| Stock incrementado, notificación a Obras de disponibilidad, auditado                                     |
| Contabilidad    | Pago/recibo                  | Obras, Compras, Auditoría  | Estado financiero de obra/pedido actualizado, auditado                                                   |
| Usuarios        | Cambio de permisos/roles     | Todos                      | Acceso a acciones críticas, feedback visual y registro de intentos fallidos en Auditoría                 |
| Auditoría       | Registro de acción           | Todos                      | Trazabilidad y consulta de historial por usuario, módulo, acción                                         |
| Mantenimiento   | Mantenimiento programado     | Inventario, Logística, Auditoría| Estado de herramientas/vehículos actualizado, puede afectar entregas, auditado                   |
| Notificaciones  | Envío/recepción de alerta    | Todos                      | Feedback visual, registro en Auditoría                                                                   |

---

> **Esta tabla resume cómo cada módulo puede afectar a otros, asegurando integración real, feedback visual y trazabilidad total en el sistema.**

---

## Ejemplos visuales de feedback y trazabilidad en la UI

### Feedback visual inmediato en la UI

- **Acción exitosa:**
  - Mensaje en barra de estado con fondo sutil y color verde (éxito):
    - Ejemplo: `Inventario exportado correctamente a inventario.xlsx` (color: #22c55e)
  - Tooltip en el botón de acción.
  - Icono de éxito en el mensaje emergente (QMessageBox).

- **Advertencia o error:**
  - Mensaje en barra de estado con fondo sutil y color rojo o amarillo:
    - Ejemplo: `No hay stock suficiente para reservar` (color: #ef4444)
    - Ejemplo: `Ingrese un código de proveedor` (color: #fbbf24)
  - Mensaje emergente (QMessageBox) con icono de advertencia o error.

- **Permiso denegado:**
  - Mensaje en barra de estado con color rojo y texto claro: `No tiene permiso para realizar esta acción`.
  - Registro automático en Auditoría del intento fallido.

- **Visualización de usuario y rol:**
  - Label de usuario en la barra de estado con color y borde según el rol (azul para admin, amarillo para supervisor, verde para usuario).

### Ejemplo visual (captura de pantalla)

![Ejemplo feedback visual](img/Captura%20de%20pantalla%202025-04-12%20180806.png)

### Consulta de trazabilidad en Auditoría

- El módulo Auditoría permite filtrar por usuario, módulo, acción, fecha y resultado (éxito/error).
- Cada acción muestra:
  - Usuario, fecha/hora, IP, módulo, tipo de acción, detalle, resultado.
  - Ejemplo: `Usuario: admin | Módulo: Inventario | Acción: Reserva | Detalle: Reservó 10 perfiles para Obra X | Resultado: Éxito`
- Los intentos fallidos (por permisos, errores, etc.) también quedan registrados y pueden ser auditados.

---

> **Estos ejemplos visuales y de trazabilidad aseguran que el usuario siempre sepa el resultado de sus acciones y que todo sea auditable, cumpliendo el estándar SAP-like.**
