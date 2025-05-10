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

## Funcionalidad: Asociación de materiales a obras y cronograma Kanban

### Asociación de materiales a obras
- Cada obra puede tener múltiples materiales asociados.
- La relación se almacena en la tabla `materiales_por_obra`:
  - `id`: clave primaria.
  - `id_obra`: referencia a la obra.
  - `id_item`: identificador del material.
  - `cantidad_necesaria`, `cantidad_reservada`, `estado`: detalles de la asociación.
- Desde la interfaz del módulo Obras, el usuario puede asociar materiales a una obra mediante un diálogo específico.
- La visualización y edición de materiales asociados se realiza desde la misma interfaz, permitiendo agregar, modificar o quitar materiales de la obra seleccionada.

### Cronograma y tablero Kanban de obras
- En la pestaña de cronograma del módulo Obras se visualiza un tablero Kanban.
- Cada tarjeta Kanban representa una obra y muestra:
  - Nombre de la obra
  - Fecha de medición
  - Fecha de entrega (calculada por defecto a 90 días desde la medición, editable por el usuario)
- El usuario puede modificar la fecha de entrega al crear o editar una obra.
- El Kanban permite identificar visualmente las fechas clave y el estado de cada obra en el cronograma.

### Estructura y relaciones de tablas relevantes
- `obras`: almacena los datos principales de cada obra, incluyendo `nombre`, `cliente`, `estado`, `fecha` (de medición) y `fecha_entrega` (editable, por defecto 90 días después de la medición).
- `materiales_por_obra`: relación N a N entre obras y materiales.
- `cronograma_obras`: almacena etapas y fechas programadas/realizadas para cada obra (opcional para futuras ampliaciones).

#### Ejemplo de relación de datos:
- Una obra tiene una fecha de medición (`fecha`) y una fecha de entrega (`fecha_entrega`).
- Al asociar materiales, se crean registros en `materiales_por_obra` vinculados por `id_obra`.
- El Kanban se alimenta de la tabla `obras`, mostrando las fechas y permitiendo editar la fecha de entrega.

### Detalles de implementación
- Al crear una obra, el campo de fecha de entrega se inicializa automáticamente a 90 días después de la fecha de medición, pero el usuario puede modificarlo.
- La interfaz permite ver y editar los materiales asociados a cada obra.
- El cronograma Kanban se actualiza dinámicamente al modificar obras o fechas.

### SQL relevante (extracto):
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

> Para más detalles sobre la lógica y la experiencia de usuario, ver los módulos `modules/obras/view.py` y `modules/obras/controller.py`.

---

## Ejemplo completo: Alta de obra, asociación de perfiles/materiales y visualización en Kanban

A continuación se muestra un ejemplo práctico de cómo se cargan los datos en las tablas principales, se asocian materiales/perfiles a una obra y cómo se visualiza en el cronograma Kanban.

### 1. Inserción de una obra con todos los campos

```sql
INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega)
VALUES ('Edificio Central', 'Constructora Sur', 'En ejecución', '2025-05-10', '2025-08-08');
-- Suponiendo que el id generado es 1
```

### 2. Asociación de perfiles/materiales a la obra

```sql
-- Ejemplo de perfiles/materiales asociados a la obra con id=1
INSERT INTO materiales_por_obra (id_obra, id_item, cantidad_necesaria, cantidad_reservada, estado)
VALUES
  (1, 101, 50, 50, 'Reservado'),   -- Perfil U 100x50x3
  (1, 102, 30, 20, 'Parcial'),     -- Perfil C 80x40x2
  (1, 103, 100, 100, 'Reservado'); -- Tornillo autoperforante
```

### 3. Visualización de la obra en el Kanban (cronograma)

```
| Fecha de medición |==================== Barra de progreso ====================| Fecha de entrega |
2025-05-10         [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■]   2025-08-08
Obra: Edificio Central | Cliente: Constructora Sur | Estado: En ejecución
Perfiles asociados: Perfil U 100x50x3 (50), Perfil C 80x40x2 (30), Tornillo autoperforante (100)
```

- La barra muestra el avance desde la fecha de medición hasta la fecha de entrega.
- Se visualizan los perfiles/materiales asociados y su estado.
- El usuario puede editar la fecha de entrega y los materiales desde la interfaz.

### 4. Ejemplo de consulta para ver la obra y sus materiales asociados

```sql
SELECT o.id, o.nombre, o.cliente, o.estado, o.fecha, o.fecha_entrega,
       m.id_item, m.cantidad_necesaria, m.cantidad_reservada, m.estado
FROM obras o
LEFT JOIN materiales_por_obra m ON o.id = m.id_obra
WHERE o.id = 1;
```

### 5. Reflejo en la interfaz
- En la tabla de obras, se muestra la obra con su cliente, estado, fechas y un resumen de materiales asociados.
- En el Kanban, la obra aparece como una tarjeta con barra de progreso y fechas clave.
- En el diálogo de materiales, se pueden ver, editar o eliminar los perfiles/materiales asociados.

---

## Ejemplo Visual de Barra Kanban para Obras

A continuación se muestra un ejemplo visual de cómo se representa una obra en el cronograma Kanban:

```
| Fecha de medición |==================== Barra de progreso ====================| Fecha de entrega |
2025-05-01         [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■]   2025-07-30
```

- La barra muestra el avance desde la fecha de medición hasta la fecha de entrega.
- El color y el largo de la barra indican el porcentaje de tiempo transcurrido.
- El usuario puede ver rápidamente cuántos días faltan y en qué etapa está cada obra.

---

## Flujo paso a paso del proceso de Obras

A continuación se detalla el flujo completo y correcto del proceso de gestión de obras en el sistema, desde la creación hasta la visualización y edición en Kanban:

1. **Creación de una nueva obra**
   - El usuario accede al módulo Obras y presiona el botón principal (icono SVG con sombra).
   - Se abre un diálogo para ingresar los datos de la obra: nombre, cliente, estado, fecha de medición y fecha de entrega (editable, por defecto 90 días).
   - Al confirmar, se inserta el registro en la tabla `obras`.

2. **Asociación de materiales/perfiles a la obra**
   - Desde la vista de la obra, el usuario accede al diálogo de materiales asociados.
   - Selecciona materiales/perfiles, define cantidades y estado (reservado, parcial, etc.).
   - Se insertan los registros en la tabla `materiales_por_obra`.

3. **Visualización y edición de materiales asociados**
   - En la tabla de obras, cada obra muestra un resumen de materiales asociados y su estado.
   - El usuario puede ver, editar o eliminar materiales desde la interfaz.

4. **Visualización en Kanban (cronograma de obras)**
   - El usuario accede a la pestaña Kanban del módulo Obras.
   - Cada obra aparece como una tarjeta con barra de progreso, fechas de medición y entrega, y materiales asociados.
   - El usuario puede editar la fecha de entrega y arrastrar la tarjeta para cambiar de etapa (próximamente drag & drop).

5. **Auditoría y registro de acciones**
   - Todas las acciones (alta, edición, asociación de materiales, cambios de fechas) quedan registradas en la tabla de auditoría.

6. **Checklist de visualización y funcionamiento**
   - El usuario puede verificar que todos los puntos del checklist funcional y visual se cumplen para cada obra y material asociado.

> Este flujo asegura que el proceso es digital, auditable y visualmente coherente en todos los pasos, desde la creación hasta la gestión avanzada de obras.

---

## Checklist de Visualización y Funcionamiento para Tablas Principales

Para asegurar la calidad y trazabilidad, cada tabla principal del sistema debe cumplir con los siguientes requisitos:

### Requisitos para cada tabla principal (`inventario_items`, `obras`, `materiales_por_obra`, etc.)

- [ ] Visualización clara y completa de todos los registros.
- [ ] Permitir agregar, editar y eliminar registros desde la interfaz.
- [ ] Exportar los datos a Excel y PDF correctamente.
- [ ] Mostrar los datos relacionados (por ejemplo, materiales asociados a una obra) en la misma vista o mediante diálogo.
- [ ] Reflejar en tiempo real los cambios realizados (alta, baja, edición, asignación, etc.).
- [ ] Registrar en auditoría cada acción relevante sobre la tabla.
- [ ] Permitir búsqueda y filtrado eficiente de registros.
- [ ] Validar que los datos se muestran correctamente después de cada ajuste o acción.
- [ ] Visualizar el estado y fechas clave (por ejemplo, barra Kanban en obras).
- [ ] Permitir adjuntar documentos o imágenes si corresponde.

> Antes de dar por finalizada una funcionalidad, verifica que todos los puntos anteriores se cumplen para cada tabla y módulo.

---

## Cuadro visual e interactivo de estado de pedidos en Obras

A partir de la versión 1.1, la vista de detalle de obra incluye un cuadro visual interactivo que muestra el estado de los pedidos de **Materiales**, **Herrajes** y **Vidrios** asociados a la obra. Este cuadro permite:

- Ver rápidamente si cada pedido está **Cargado** o **Pendiente**.
- Si un pedido está pendiente, hacer clic para navegar al módulo correspondiente y realizar la carga.
- Si el pedido está cargado, ver el detalle desde la misma vista.

### Ejemplo visual:

```
+-------------------------------------------------------------+
| Obra: Edificio Central   Estado: En ejecución               |
|-------------------------------------------------------------|
| [Materiales]   [Herrajes]   [Vidrios]                      |
|   Pendiente      Cargado      Pendiente                     |
|   (Ir a carga)   (Ver)        (Ir a carga)                  |
+-------------------------------------------------------------+
```

### Integración técnica
- El controlador de obras expone un método para consultar el estado de los tres pedidos asociados a la obra seleccionada.
- La vista de obras muestra el cuadro visual y conecta los botones a la navegación o visualización de detalles.
- La lógica de consulta de estado se implementa en el modelo de obras, integrando los módulos de materiales, herrajes y vidrios.

### Navegación y experiencia de usuario
- El usuario puede acceder a la carga o detalle de cada pedido sin salir del contexto de la obra.
- Cada acción queda registrada en auditoría.

### Checklist de integración
- [x] Consulta de estado de pedidos desde la vista de obra
- [x] Cuadro visual interactivo en la interfaz
- [x] Navegación directa a módulos de carga o detalle
- [x] Registro en auditoría de cada acción

> Esta funcionalidad mejora la trazabilidad y la experiencia de usuario, permitiendo gestionar y visualizar el avance de los pedidos de manera centralizada y visual.

---

## Buenas Prácticas de Programación

### Evitar el uso excesivo de condicionales `if`

Para mantener el código limpio, escalable y fácil de mantener, se recomienda evitar el uso excesivo de condicionales `if`. En su lugar, considere las siguientes alternativas:

1. **Diccionarios o Mapas**:
   Use diccionarios para mapear claves a funciones o valores, eliminando la necesidad de múltiples `if`.
   ```python
   acciones = {
       "accion1": funcion1,
       "accion2": funcion2,
       "accion3": funcion3,
   }
   accion = "accion1"
   if accion in acciones:
       acciones[accion]()
   ```

2. **Patrón de Diseño Estrategia**:
   Implemente estrategias como clases o funciones y seleccione la adecuada en tiempo de ejecución.

3. **Polimorfismo**:
   Si trabaja con objetos, utilice polimorfismo para que cada clase implemente su propia lógica, eliminando la necesidad de múltiples `if`.

4. **Uso de `match` (Python 3.10 o superior)**:
   El operador `match` es una alternativa más limpia y legible a múltiples `if-elif`.
   ```python
   match accion:
       case "accion1":
           funcion1()
       case "accion2":
           funcion2()
       case _:
           print("Acción no reconocida")
   ```

5. **Refactorización**:
   Divida el código en funciones más pequeñas y específicas para reducir la complejidad.

Adoptar estas prácticas no solo mejora la calidad del código, sino que también facilita su mantenimiento y escalabilidad a largo plazo.

## Estandarización: Decorador de Permisos y Auditoría

A partir de la versión 1.0.3, todos los controladores de módulos deben usar el decorador `PermisoAuditoria` para validar permisos y registrar auditoría en cada acción relevante. Esto reemplaza el uso repetitivo de if y asegura trazabilidad y seguridad en todo el sistema.

### Ejemplo de uso:

```python
class PermisoAuditoria:
    def __init__(self, modulo):
        self.modulo = modulo
    def __call__(self, accion):
        def decorador(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                usuario_model = getattr(self, 'usuarios_model', UsuariosModel())
                auditoria_model = getattr(self, 'auditoria_model', AuditoriaModel())
                usuario = getattr(self, 'usuario_actual', None)
                if not usuario o not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(self, 'view') and hasattr(self.view, 'label'):
                        self.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                resultado = func(self, *args, **kwargs)
                auditoria_model.registrar_evento(usuario, self.modulo, accion)
                return resultado
            return wrapper
        return decorador
```

Utiliza este decorador en todos los métodos de acción de los controladores para mantener la seguridad y trazabilidad de manera uniforme y sin múltiples ifs.

## Uso obligatorio del decorador PermisoAuditoria para permisos y auditoría

A partir de la versión actual, **es obligatorio** utilizar el decorador `PermisoAuditoria` en todos los métodos de los controladores que realicen acciones sensibles (ver, editar, eliminar, aprobar, etc.) en cualquier módulo del sistema. Esto garantiza la validación centralizada de permisos y el registro de auditoría, eliminando la repetición de condicionales `if` y mejorando la trazabilidad y seguridad.

#### Ejemplo de implementación estándar:

```python
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps

class PermisoAuditoria:
    def __init__(self, modulo):
        self.modulo = modulo
    def __call__(self, accion):
        def decorador(func):
            @wraps(func)
            def wrapper(controller, *args, **kwargs):
                usuario_model = getattr(controller, 'usuarios_model', UsuariosModel())
                auditoria_model = getattr(controller, 'auditoria_model', AuditoriaModel())
                usuario = getattr(controller, 'usuario_actual', None)
                if not usuario o no usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    # Mostrar mensaje o lanzar excepción
                    return None
                resultado = func(controller, *args, **kwargs)
                auditoria_model.registrar_evento(usuario, self.modulo, accion)
                return resultado
            return wrapper
        return decorador

permiso_auditoria_modulo = PermisoAuditoria('nombre_modulo')

class EjemploController:
    def __init__(self, model, view, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = UsuariosModel()
        self.auditoria_model = AuditoriaModel()

    @permiso_auditoria_modulo('ver')
    def ver_elemento(self):
        ...

    @permiso_auditoria_modulo('editar')
    def editar_elemento(self):
        ...
```

**Notas:**
- Todos los métodos de acción en los controladores deben estar decorados con `@permiso_auditoria_modulo('accion')`.
- Los modelos `UsuariosModel` y `AuditoriaModel` deben estar instanciados en cada controlador.
- No se permite el uso de condicionales `if` repetidos para validación de permisos en los métodos.
- Este patrón es obligatorio y debe mantenerse en todo el proyecto.

## Estándar de Botones e Interfaz Visual

- Todos los módulos deben utilizar botones principales solo con iconos (sin texto), usando imágenes SVG/PNG de la carpeta `img`.
- Cada botón debe tener un tooltip descriptivo para accesibilidad y usabilidad.
- El sidebar y las acciones principales debajo de las tablas deben seguir este estándar visual.
- Los botones deben tener estilo consistente, tamaño fijo y feedback visual (hover, pressed).
- Ejemplo de implementación en una vista:

```python
boton = QPushButton()
boton.setIcon(QtGui.QIcon('img/plus_icon.svg'))
boton.setIconSize(QSize(32, 32))
boton.setToolTip('Agregar nuevo ítem')
boton.setText("")
boton.setFixedSize(48, 48)
```

## Compatibilidad entre Controlador y Vista

- Todas las vistas deben exponer las siguientes propiedades para compatibilidad con los controladores:
  - `label`: QLabel de estado
  - `buscar_input`: QLineEdit para búsquedas
  - `id_item_input`: QLineEdit para ID de ítem
- Si la vista no los usa visualmente, debe proveerlos como stubs para evitar errores de importación y conexión de señales.

## Modularidad y Consistencia

- El flujo de botones, señales y acciones debe ser modular y replicable en todos los módulos.
- La estructura de conexión de señales y métodos debe ser consistente para facilitar el mantenimiento y la escalabilidad.

### Estándar Visual y de Interacción para Módulos

- Todos los módulos principales (Inventario, Usuarios, Obras, Logística, Compras, Contabilidad, Herrajes, etc.) deben mostrar los botones de acción principales (agregar, buscar, exportar, etc.) como botones solo con icono (sin texto), usando imágenes SVG/PNG de la carpeta `img`.
- Cada botón debe tener un tooltip descriptivo y un estilo visual consistente (color, tamaño, bordes redondeados, hover y pressed).
- Los botones deben ubicarse debajo de la tabla principal del módulo, en un layout horizontal.
- Las vistas deben exponer las propiedades `label`, `buscar_input` e `id_item_input` para que los controladores puedan mostrar mensajes y realizar búsquedas de forma unificada.
- Este estándar es obligatorio para todos los módulos y debe mantenerse para asegurar una experiencia de usuario coherente y moderna.

### Ejemplo de implementación de botones con icono en una vista

```python
botones_layout = QHBoxLayout()
botones = [QPushButton(), QPushButton(), QPushButton()]
iconos = [
    ("plus_icon.svg", "Agregar nuevo elemento"),
    ("buscar.png", "Buscar elemento"),
    ("excel_icon.svg", "Exportar a Excel"),
]
for boton, (icono, tooltip) in zip(botones, iconos):
    boton.setIcon(QtGui.QIcon(f"img/{icono}"))
    boton.setIconSize(QSize(32, 32))
    boton.setToolTip(tooltip)
    boton.setText("")
    boton.setFixedSize(48, 48)
    boton.setStyleSheet("""
        QPushButton {
            background-color: #2563eb;
            border-radius: 12px;
            border: none;
        }
        QPushButton:hover {
            background-color: #1e40af;
        }
        QPushButton:pressed {
            background-color: #1e3a8a;
        }
    """)
    botones_layout.addWidget(boton)
layout.addLayout(botones_layout)
```

> Aplica este patrón en todos los módulos para mantener la coherencia visual y de interacción.

## Sidebar visual solo con íconos SVG

A partir de la versión 1.0.4, el sidebar de la aplicación muestra únicamente los íconos SVG ubicados en la carpeta `utils/`, sin nombres de módulos ni texto. Esto permite una navegación visual, minimalista y moderna, siguiendo el estándar de diseño de la app.

**Implementación:**
- El sidebar se genera automáticamente usando la siguiente lista de íconos, en el orden de los módulos principales:

```python
svg_dir = os.path.join(os.path.dirname(__file__), 'utils')
svg_icons = [
    'inventario.svg',    # Inventario
    'obras.svg',         # Obras
    'produccion.svg',    # Producción
    'logistica.svg',     # Logística
    'compras.svg',       # Compras
    'users.svg',         # Usuarios
    'auditoria.svg',     # Auditoría
    'configuracion.svg', # Configuración
    'mantenimiento.svg', # Mantenimiento
    'contabilidad.svg',  # Contabilidad
    'vidrios.svg'        # Vidrios
]
sections = [(icon.split('.')[0].capitalize(), os.path.join(svg_dir, icon)) for icon in svg_icons]
self.sidebar = Sidebar("utils", sections)
self.sidebar.pageChanged.connect(self.module_stack.setCurrentIndex)
main_layout.addWidget(self.sidebar)
```

- Cada ícono representa una sección o módulo principal, y el orden es fijo según la lista anterior.
- No se muestran nombres ni etiquetas de texto, solo los íconos.
- Para agregar o quitar módulos del sidebar, basta con agregar o eliminar el archivo SVG correspondiente en `utils/` y ajustar la lista `svg_icons`.

> El sidebar es completamente visual y se adapta automáticamente a los íconos SVG presentes en la carpeta `utils/` según el orden definido.

---

## SQL Server: Estructura y datos de ejemplo para el módulo Obras (Gantt)

Para asegurar la compatibilidad del módulo Obras (cronograma Gantt y edición de fechas), ejecuta el siguiente script en la base de datos **mps.app-inventario** de SQL Server:

```sql
-- 1. Agregar columna fecha_entrega si no existe
IF COL_LENGTH('obras', 'fecha_entrega') IS NULL
BEGIN
    ALTER TABLE obras ADD fecha_entrega DATE NULL;
END
GO

-- 2. Eliminar datos actuales (opcional, solo si quieres limpiar la tabla)
-- DELETE FROM obras;

-- 3. Insertar datos de ejemplo compatibles con el Gantt
INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES
('Edificio Central', 'Constructora Sur', 'Medición', DATEADD(DAY, -10, CAST(GETDATE() AS DATE)), DATEADD(DAY, 30, CAST(GETDATE() AS DATE))),
('Torre Norte', 'Desarrollos Río', 'Fabricación', DATEADD(DAY, -20, CAST(GETDATE() AS DATE)), DATEADD(DAY, 15, CAST(GETDATE() AS DATE))),
('Residencial Sur', 'Grupo Delta', 'Entrega', DATEADD(DAY, -40, CAST(GETDATE() AS DATE)), DATEADD(DAY, 5, CAST(GETDATE() AS DATE)));
GO
```

- Si la tabla tiene un campo IDENTITY obligatorio, omite la columna id en el insert.
- Si la tabla ya tiene datos, los inserts pueden fallar por duplicidad de nombre/cliente.
- El script también está disponible en `scripts/obras_sqlserver_ejemplo.sql`.

---