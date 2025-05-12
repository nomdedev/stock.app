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
````
