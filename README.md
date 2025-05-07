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

### Notas Importantes
1. **Nombres de Tablas**: Solo se deben usar los nombres de tablas existentes. No se deben crear tablas con nombres diferentes sin previa consulta y aprobación.
2. **Creación de Nuevas Tablas**: Si se necesita crear una nueva tabla, consulta primero y espera la aprobación antes de proceder.
3. **Consistencia**: Asegúrate de que las consultas y operaciones en la base de datos utilicen los nombres exactos de las tablas listadas aquí.

---

Si necesitas agregar más información o realizar cambios en las bases de datos, por favor consulta con el equipo antes de proceder.

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

### Cambios Recientes

#### Integración de Módulos
- **Vidrios** ahora está integrado como una pestaña dentro del módulo **Inventario**.
- El módulo **Materiales** ha sido eliminado y su funcionalidad está integrada en el módulo **Herrajes**.

#### Actualización de Funcionalidades
- El módulo **Inventario** ahora incluye pestañas adicionales para gestionar vidrios, permitiendo una administración centralizada.
- El módulo **Compras** permite gestionar pedidos directamente desde una pestaña dedicada, mejorando la organización y el flujo de trabajo.

#### Mejoras en la Interfaz
- Se han ajustado los botones para mostrar íconos en lugar de texto, utilizando imágenes de la carpeta `img`.
- Se han añadido estilos consistentes para los botones y pestañas, siguiendo el esquema de colores definido en el modo oscuro.

### Notas Adicionales
- Asegúrate de que las imágenes necesarias para los íconos estén disponibles en la carpeta `img`.
- Verifica que las nuevas pestañas en los módulos **Inventario** y **Compras** funcionen correctamente tras la integración.

### Estilo de Botones
Por defecto, todos los botones deben tener un tamaño estándar de 100x25 px para mantener la consistencia visual en la aplicación. Este tamaño se aplica automáticamente a menos que se especifique lo contrario.

🧩 Módulo 1: Inventario General
🗄 Base de datos: mpsInventario

🧱 Tablas involucradas
inventario_items
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
codigo	VARCHAR(20)	Código interno único (formato: 123456.789)
nombre	VARCHAR(100)	Descripción del material
tipo_material	VARCHAR(50)	PVC, aluminio, accesorio, insumo, repuesto
unidad	VARCHAR(20)	Unidad de medida (m, unidad, kg, etc.)
stock_actual	DECIMAL	Cantidad actual en stock
stock_minimo	DECIMAL	Stock mínimo recomendado
ubicacion	TEXT	Ubicación física del ítem
descripcion	TEXT	Observaciones o detalles técnicos
qr_code	TEXT	Código QR generado automáticamente
imagen_referencia	TEXT	URL o ruta a la imagen del producto
movimientos_stock
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_item	INT (FK)	Relación con inventario_items.id
fecha	TIMESTAMP	Fecha y hora del movimiento
tipo_movimiento	VARCHAR(20)	ingreso, egreso, ajuste, corrección, reserva
cantidad	DECIMAL	Cantidad movida
realizado_por	INT (FK)	Usuario que realizó el movimiento
observaciones	TEXT	Motivo o detalle
referencia	TEXT	Referencia a obra, pedido u otro módulo
reservas_stock
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_item	INT (FK)	Relación con inventario_items.id
fecha_reserva	TIMESTAMP	Fecha de la reserva
cantidad_reservada	DECIMAL	Cantidad apartada
referencia_obra	INT (FK)	Obra relacionada (si aplica)
estado	VARCHAR(20)	activa, utilizada, cancelada
🔗 Relaciones
Un ítem de inventario puede tener muchos movimientos y muchas reservas (1:N)

Cada movimiento está vinculado a un usuario y puede estar relacionado con una obra, mantenimiento o pedido

Las reservas se vinculan con obras y se reflejan en el cronograma y producción

El QR permite identificar el ítem desde cualquier módulo mediante escaneo

🖥 Pantallas del módulo
1. Vista general del inventario
Tabla con filtros por tipo, ubicación, stock mínimo

Color en rojo si está por debajo del stock mínimo

Botones: "Ver movimientos", "Nuevo ítem", "Reservar", "Ajustar stock"

2. Ficha del ítem
Imagen, nombre, código, QR visible

Historial completo de movimientos

Stock actual y reservado

Ubicación y descripción

3. Movimiento manual
Tipo de movimiento

Cantidad

Usuario

Observaciones

Botón “Guardar movimiento”

4. Reservas
Lista de materiales reservados

Obra relacionada

Fecha, estado y cantidad

Posibilidad de cancelar o transformar en entrega

🔐 Permisos por rol
Rol	Ver	Editar	Reservar	Ajustar stock
Admin	✅	✅	✅	✅
Compras	✅	❌	✅	❌
Producción	✅	✅	✅	✅
Logística	✅	❌	✅	❌
Auditor	✅	❌	❌	❌
⚙ Funcionalidades especiales
Generación automática de QR para impresión y escaneo

Alerta visual si el stock cae por debajo del mínimo

Exportación de inventario a Excel y PDF

Modo lectura para auditoría

Posibilidad de integrarse con pedidos y cronograma de obras

Operación offline con sincronización posterior

🧩 Módulo 2: Producción y Fabricación
🗄 Base de datos: mpsProduccion

🧱 Tablas involucradas
aberturas
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_obra	INT (FK)	Relación con obras.id
codigo	VARCHAR(100)	Código interno de la abertura
tipo_abertura	VARCHAR(50)	Puerta, ventana, paño fijo, etc.
descripcion	TEXT	Detalles técnicos
estado_general	VARCHAR(50)	Diseño, corte, armado, burletes, vidrio, finalizado
fecha_inicio	DATE	Fecha de inicio de fabricación
fecha_entrega_estimada	DATE	Fecha de entrega prevista
etapas_fabricacion
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_abertura	INT (FK)	Relación con aberturas.id
etapa	VARCHAR(50)	corte, armado, burletes, vidrio, etc.
fecha_inicio	DATE	Fecha real de inicio
fecha_fin	DATE	Fecha real de finalización
realizado_por	INT (FK)	Usuario responsable
estado	VARCHAR(30)	pendiente, en proceso, finalizada
tiempo_estimado	INTERVAL	Duración esperada
tiempo_real	INTERVAL	Duración real
observaciones	TEXT	Detalles o problemas
🔗 Relaciones
Una obra puede tener múltiples aberturas (1:N)

Cada abertura puede tener múltiples etapas de fabricación (1:N)

Cada etapa se puede vincular con un usuario responsable y se registra su duración

La combinación de etapas define el estado general de la abertura y se actualiza automáticamente

Las etapas completadas se integran con el cronograma de obra y con logística

🖥 Pantallas del módulo
1. Vista Kanban de producción
Columnas: Corte, Soldadura, Armado, Burletes, Vidrio

Tarjetas por abertura con ícono, estado, obra y responsable

Arrastrar tarjeta para cambiar de etapa

Colores según prioridad o atraso

2. Lista de aberturas
Tabla con filtros por obra, estado, tipo

Botones: “Ver detalles”, “Editar etapas”, “Asignar responsable”

3. Ficha de abertura
Código, obra, tipo, estado actual

Cronograma de etapas

Historial de observaciones y tiempos

Botón para finalizar etapa o reprogramar

4. Registro de etapa
Selección de etapa

Fecha inicio y fin

Tiempo estimado y real

Observaciones y responsable

5. Dashboard de fabricación
Gráficos de productividad por etapa o usuario

Aberturas activas vs finalizadas

Alertas por retrasos

Eficiencia general por semana/mes

🔐 Permisos por rol
Rol	Ver	Editar	Finalizar etapa	Reprogramar
Admin	✅	✅	✅	✅
Producción	✅	✅	✅	✅
Logística	✅	❌	❌	❌
Auditor	✅	❌	❌	❌
⚙ Funcionalidades especiales
Visualización estilo Kanban

Cálculo automático de eficiencia por etapa

Panel por usuario con rendimiento individual

Alerta si se superó el tiempo estimado

Reportes PDF y exportación de etapas

Posibilidad de integración con mantenimiento si depende de herramientas específicas

🧩 Módulo 3: Logística
🗄 Base de datos: mpsLogistica

🧱 Tablas involucradas
entregas_obras
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_obra	INT (FK)	Obra asociada a la entrega
fecha_programada	DATE	Fecha prevista para la entrega
fecha_realizada	DATE	Fecha efectiva de entrega
estado	VARCHAR(30)	pendiente, en ruta, entregado, reprogramado
vehiculo_asignado	INT (FK)	Vehículo utilizado (relación con módulo de vehículos)
chofer_asignado	INT (FK)	Usuario responsable
observaciones	TEXT	Detalles logísticos
firma_receptor	TEXT	Firma digital o imagen del receptor
checklist_entrega
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_entrega	INT (FK)	Relación con entregas_obras.id
item	TEXT	Ítem verificado
estado_item	VARCHAR(20)	ok, dañado, faltante
observaciones	TEXT	Comentarios adicionales
🔗 Relaciones
Cada obra puede tener múltiples entregas.

Cada entrega tiene un vehículo y un chofer asignado.

Las entregas pueden tener múltiples ítems verificados mediante checklist.

La firma del receptor queda asociada al acta de entrega y puede imprimirse/exportarse.

Se puede acceder a las entregas desde el cronograma de la obra.

🖥 Pantallas del módulo
1. Cronograma de entregas
Vista calendario semanal/mensual

Color por estado de entrega

Filtros por vehículo, chofer, estado

2. Ficha de entrega
Datos de la obra, vehículo y chofer

Checklist editable

Firma del receptor en pantalla táctil o desde archivo

Observaciones y estado

3. Checklist previo
Listado de ítems por entrega

Posibilidad de marcar como dañado/faltante

Campo de texto por cada ítem

4. Seguimiento logístico
Tarjetas por entrega

Estado: pendiente → en ruta → entregado

Ubicación estimada (futura integración con GPS)

5. Historial de entregas
Tabla de entregas por obra

Estado, fecha, chofer y observaciones

Acceso a PDF generado del acta

🔐 Permisos por rol
Rol	Ver	Editar	Firmar	Reprogramar
Admin	✅	✅	✅	✅
Logística	✅	✅	✅	✅
Producción	✅	❌	❌	❌
Auditor	✅	❌	❌	❌
⚙ Funcionalidades especiales
Firma digital del receptor integrada en pantalla o desde imagen

Exportación del acta de entrega en PDF con checklist

Alertas por entregas vencidas o sin chofer asignado

Posibilidad de cancelar, reprogramar o reasignar chofer

Generación automática de hoja de ruta por vehículo

Integración con cronograma de obra y módulo de vehículos

🧩 Módulo 4: Obras y Cronograma
🗄 Base de datos: mpsObras

🧱 Tablas involucradas
obras
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único de la obra
nombre_cliente	VARCHAR(100)	Nombre del cliente
apellido_cliente	VARCHAR(100)	Apellido del cliente
telefono	VARCHAR(50)	Teléfono de contacto
email	VARCHAR(100)	Email del cliente
direccion	TEXT	Dirección donde se realizará la obra
fecha_creacion	TIMESTAMP	Fecha de alta de la obra
estado_general	VARCHAR(50)	planificación, en producción, entregada, etc.
observaciones	TEXT	Comentarios generales
cronograma_obras
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_obra	INT (FK)	Relación con obras.id
etapa	VARCHAR(50)	medición, fabricación, colocación, finalización
fecha_programada	DATE	Fecha prevista para la etapa
fecha_realizada	DATE	Fecha real (si ya se ejecutó)
observaciones	TEXT	Comentarios
responsable	INT (FK)	Usuario encargado
estado	VARCHAR(30)	pendiente, realizada, reprogramada
materiales_por_obra
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_obra	INT (FK)	Obra a la que se asigna el material
id_item	INT (FK)	Material del inventario
cantidad_necesaria	DECIMAL	Cantidad requerida para la obra
cantidad_reservada	DECIMAL	Cantidad ya apartada
estado	VARCHAR(30)	pendiente, reservado, entregado
🔗 Relaciones
Una obra tiene múltiples etapas en cronograma_obras.

Cada etapa puede tener un responsable, estado, observaciones y fechas programadas.

Los materiales asignados se vinculan con inventario_items y afectan stock.

Las fechas programadas son clave para los módulos de producción y logística.

Estado general de la obra se actualiza según las etapas completadas.

🖥 Pantallas del módulo
1. Listado de obras
Tabla con nombre del cliente, dirección, estado general

Filtros por estado, fecha de creación, usuario asignado

Botón para ver cronograma, editar datos, asignar materiales

2. Ficha completa de obra
Datos completos del cliente y obra

Cronograma con etapas y fechas

Botón para agregar o reprogramar etapas

Sección de materiales requeridos

3. Editor de cronograma
Selector de etapa

Fecha programada y fecha realizada

Estado (pendiente, realizada, reprogramada)

Observaciones y responsable

4. Asignación de materiales
Selección desde inventario

Cantidad necesaria vs reservada

Reserva automática de ítems

Estado del material (pendiente, entregado)

5. Agenda general de obras
Vista calendario con etapas por día/obra

Filtros por tipo de etapa

Integración con entregas y producción

🔐 Permisos por rol
Rol	Ver	Editar	Asignar materiales	Reprogramar etapas
Admin	✅	✅	✅	✅
Producción	✅	✅	✅	✅
Logística	✅	❌	❌	❌
Compras	✅	❌	❌	❌
Auditor	✅	❌	❌	❌
⚙ Funcionalidades especiales
Avance automático de estado de obra según etapas completadas

Alerta si no hay fecha cargada para una etapa importante

QR por obra para escaneo desde papel o tablet

Exportación del cronograma en Excel o PDF

Vinculación directa con producción, inventario y logística

Vista de resumen por cliente o por mes

🧩 Módulo 5: Pedidos y Compras
🗄 Base de datos: mpsCompras

🧱 Tablas involucradas
pedidos_compra
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
fecha_creacion	TIMESTAMP	Fecha del pedido
solicitado_por	INT (FK)	Usuario que solicita el pedido
estado	VARCHAR(30)	pendiente, aprobado, rechazado, en curso, finalizado
observaciones	TEXT	Motivo o necesidad
prioridad	VARCHAR(20)	baja, media, alta
detalle_pedido
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_pedido	INT (FK)	Relación con pedidos_compra.id
id_item	INT (FK)	Relación con inventario_items.id
cantidad_solicitada	DECIMAL	Cantidad requerida
unidad	VARCHAR(20)	Unidad de medida
justificacion	TEXT	Explicación técnica
presupuestos
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_pedido	INT (FK)	Pedido al que pertenece
proveedor	VARCHAR(100)	Nombre del proveedor
fecha_recepcion	DATE	Fecha de recepción del presupuesto
archivo_adjunto	TEXT	Ruta o nombre del archivo subido
comentarios	TEXT	Comentarios o condiciones
precio_total	DECIMAL	Precio ofertado total
seleccionado	BOOLEAN	Si fue elegido para la compra
🔗 Relaciones
Cada pedido puede tener múltiples ítems detallados

Un pedido puede tener varios presupuestos adjuntos

Uno de los presupuestos puede ser marcado como “seleccionado”

Los pedidos aprobados generan un movimiento de ingreso al stock

🖥 Pantallas del módulo
1. Lista de pedidos
Tabla con filtros por estado, prioridad, fecha, usuario solicitante

Botones: “Ver detalles”, “Aprobar”, “Rechazar”, “Cargar presupuesto”

2. Formulario nuevo pedido
Selector de ítems desde inventario

Campo de cantidad, unidad y justificación

Posibilidad de agregar múltiples ítems

3. Carga de presupuestos
Selector del proveedor

Campo de precio total y comentarios

Botón para subir archivo adjunto (PDF, imagen, etc.)

Checkbox para marcar como “seleccionado”

4. Comparador de presupuestos
Vista comparativa de precios por ítem y proveedor

Historial de compras previas al proveedor

Sugerencia de proveedor más habitual o conveniente

5. Seguimiento del pedido
Línea de estado: solicitado → aprobado → en curso → finalizado

Observaciones del estado actual

Historial de acciones tomadas

🔐 Permisos por rol
Rol	Ver	Editar	Aprobar	Cargar presupuesto
Admin	✅	✅	✅	✅
Compras	✅	✅	✅	✅
Producción	✅	✅	❌	❌
Auditor	✅	❌	❌	❌
⚙ Funcionalidades especiales
Comparador inteligente de presupuestos

Historial por proveedor y análisis de compras pasadas

Generación de PDF del pedido con los presupuestos adjuntos

Firma digital para aprobación formal

Integración con inventario para convertir pedido en ingreso automático

Exportación de reportes de compras por período

🧩 Módulo 6: Usuarios y Permisos
🗄 Base de datos: mpsUsuarios

🧱 Tablas involucradas
usuarios
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
nombre	VARCHAR(100)	Nombre del usuario
apellido	VARCHAR(100)	Apellido del usuario
email	VARCHAR(100)	Correo electrónico
usuario	VARCHAR(50)	Nombre de usuario para login
password_hash	TEXT	Contraseña encriptada
rol	VARCHAR(50)	admin, compras, producción, logística, etc.
estado	VARCHAR(20)	activo, suspendido
fecha_creacion	TIMESTAMP	Fecha de alta
ultima_conexion	TIMESTAMP	Último acceso registrado
roles_permisos
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
rol	VARCHAR(50)	Rol asignado (debe coincidir con usuarios.rol)
modulo	VARCHAR(50)	Nombre del módulo (inventario, logística, etc.)
permiso_ver	BOOLEAN	Puede ver el módulo
permiso_editar	BOOLEAN	Puede editar
permiso_aprobar	BOOLEAN	Puede aprobar acciones
permiso_eliminar	BOOLEAN	Puede eliminar datos
logs_usuarios
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
usuario_id	INT (FK)	Usuario que realizó la acción
accion	TEXT	Descripción del evento (inició sesión, editó...)
modulo	VARCHAR(50)	Módulo donde ocurrió la acción
fecha_hora	TIMESTAMP	Fecha y hora del evento
detalle	TEXT	Más información del evento
ip_origen	VARCHAR(100)	Dirección IP del usuario
🔗 Relaciones
Un usuario pertenece a un rol, que define sus permisos mediante roles_permisos.

Las acciones importantes quedan registradas en logs_usuarios para trazabilidad.

Al modificar usuarios o roles, se actualiza automáticamente su acceso al sistema.

🖥 Pantallas del módulo
1. Gestión de usuarios
Tabla con nombre, rol, estado, última conexión

Filtros por estado, rol, nombre

Botones: Crear, Editar, Suspender, Resetear contraseña

2. Formulario de nuevo usuario
Campos: nombre, apellido, email, usuario, rol

Opción de generar contraseña temporal o manual

Activar/desactivar acceso

3. Gestión de roles y permisos
Tabla con checkboxes por módulo y permiso

Posibilidad de crear nuevos roles personalizados

Clonar permisos desde otro rol

4. Auditoría de usuarios
Lista de acciones recientes por usuario

Filtro por módulo, tipo de acción o IP

Botón para exportar logs

5. Panel de actividad
Último login por usuario

Alertas si hay múltiples accesos fallidos

Actividad de la última semana

🔐 Permisos por rol
Rol	Ver usuarios	Editar	Gestionar roles	Ver logs
Admin	✅	✅	✅	✅
Auditor	✅	❌	❌	✅
Otros	❌	❌	❌	❌
⚙ Funcionalidades especiales
Control de permisos por acción (ver, editar, aprobar, eliminar)

Suspensión temporal de cuentas

Registro detallado de cada acción importante (con IP y módulo)

Soporte para múltiples roles y configuraciones

Integración con auditoría general del sistema

🧩 Módulo 7: Auditoría y Logs
🗄 Base de datos: mpsAuditoria

🧱 Tablas involucradas
auditorias_sistema
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
fecha_hora	TIMESTAMP	Momento en que ocurrió el evento
usuario_id	INT (FK)	Usuario que realizó la acción
modulo_afectado	VARCHAR(50)	Módulo donde se realizó la acción
tipo_evento	VARCHAR(30)	inserción, modificación, eliminación, acceso
detalle	TEXT	Descripción detallada del evento
ip_origen	VARCHAR(50)	IP desde la que se ejecutó
device_info	TEXT	Información del dispositivo
origen_evento	VARCHAR(30)	web, escritorio, API
errores_sistema
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
fecha_hora	TIMESTAMP	Momento del error
usuario_id	INT (nullable)	Usuario (si aplica)
modulo	VARCHAR(50)	Módulo afectado
descripcion_error	TEXT	Mensaje de error
stack_trace	TEXT	Detalles técnicos del error
ip_origen	VARCHAR(50)	Dirección IP
origen_evento	VARCHAR(30)	web, escritorio, API
🔗 Relaciones
Cada acción del sistema que afecte datos o acceso se registra en auditorias_sistema

Todos los errores son almacenados en errores_sistema, incluso si no hay usuario logueado

Ambas tablas se consultan desde el panel de auditoría por administradores o usuarios con rol auditor

🖥 Pantallas del módulo
1. Panel de auditoría general
Tabla con logs por módulo, usuario, tipo de acción

Filtros por fecha, módulo, IP, tipo de evento

Botón para exportar a Excel o PDF

2. Visor de errores técnicos
Lista de errores recientes

Visualización del stack trace

Filtros por módulo o usuario

Recuento de errores frecuentes

3. Detalle de evento
Muestra el evento exacto, con hora, usuario, IP y dispositivo

Muestra los campos modificados si aplica (antes y después)

4. Dashboard de auditoría
Cantidad de acciones por módulo

Actividad por usuario

Alertas si hay muchos errores en un mismo módulo

🔐 Permisos por rol
Rol	Ver auditoría	Ver errores	Exportar
Admin	✅	✅	✅
Auditor	✅	✅	✅
Otros	❌	❌	❌
⚙ Funcionalidades especiales
Registro automático de acciones por módulo y usuario

Logs compatibles con normas ISO (9001, 14001, etc.)

Identificación de accesos sospechosos por IP o dispositivo

Registro del origen del evento (web, escritorio, API)

Herramienta clave para control interno y revisiones externas

🧩 Módulo 8: Mantenimiento de Herramientas y Vehículos
🗄 Base de datos: mpsMantenimiento

🧱 Tablas involucradas
herramientas
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
nombre	VARCHAR(100)	Nombre de la herramienta
descripcion	TEXT	Uso, características técnicas
codigo_interno	VARCHAR(50)	Código único o QR
ubicacion	TEXT	Lugar físico donde se encuentra
estado	VARCHAR(30)	activa, en mantenimiento, fuera de uso
imagen	TEXT	Imagen de referencia
vehiculos
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
patente	VARCHAR(20)	Matrícula del vehículo
marca	VARCHAR(50)	Marca
modelo	VARCHAR(50)	Modelo
estado_operativo	VARCHAR(30)	activo, en taller, fuera de servicio
ubicacion_actual	TEXT	Dónde se encuentra actualmente
mantenimientos
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
tipo_objeto	VARCHAR(20)	herramienta, vehículo
id_objeto	INT	ID de la herramienta o vehículo
tipo_mantenimiento	VARCHAR(50)	preventivo, correctivo, calibración
fecha_realizacion	DATE	Fecha en que se realizó
realizado_por	INT (FK)	Usuario que realizó el mantenimiento
observaciones	TEXT	Comentarios, tareas realizadas
firma_digital	TEXT	Firma digital del responsable (hash o imagen)
checklists_mantenimiento
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_mantenimiento	INT (FK)	Relación con mantenimientos.id
item	TEXT	Ítem del checklist (ej. limpiar filtro)
estado	VARCHAR(20)	ok, pendiente, no aplica
observaciones	TEXT	Detalle adicional si aplica
repuestos_usados
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
id_mantenimiento	INT (FK)	Relación con mantenimientos.id
id_item	INT (FK)	Relación con inventario_items.id
cantidad_utilizada	DECIMAL	Cuánto se usó del stock
tareas_recurrentes
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
tipo_objeto	VARCHAR(20)	herramienta, vehículo
id_objeto	INT	ID de la herramienta o vehículo
descripcion	TEXT	Qué se debe hacer
frecuencia_dias	INT	Cada cuántos días se repite
proxima_fecha	DATE	Próxima fecha estimada
responsable	INT (FK)	Usuario asignado
🔗 Relaciones
Un mantenimiento puede incluir múltiples ítems de checklist y repuestos

Las tareas recurrentes generan mantenimientos programados

Los mantenimientos afectan al estado de herramientas y vehículos

Todo mantenimiento queda registrado con firma digital del responsable

🖥 Pantallas del módulo
1. Lista de herramientas y vehículos
Filtros por estado, ubicación

Búsqueda por nombre, código o QR

Botones: Ver ficha, Iniciar mantenimiento, Ver historial

2. Ficha técnica
Imagen, datos generales, código QR

Historial de mantenimientos anteriores

Tareas recurrentes programadas

3. Registro de mantenimiento
Selección del tipo de mantenimiento

Carga de checklist

Firma digital del responsable

Carga de repuestos usados (desde inventario)

4. Mantenimientos recurrentes
Lista de tareas por vencer

Posibilidad de generar mantenimiento con un clic

Alerta automática si se pasó la fecha

5. Historial general
Filtros por objeto, fecha, tipo

Exportación a Excel o PDF

Ver detalle de cada mantenimiento

🔐 Permisos por rol
Rol	Ver	Registrar	Programar tareas	Ver historial
Admin	✅	✅	✅	✅
Mantenimiento	✅	✅	✅	✅
Producción	✅	❌	❌	✅
Auditor	✅	❌	❌	✅
⚙ Funcionalidades especiales
Escaneo QR para acceder directamente a ficha de herramienta

Firma digital del técnico

Checklist por tipo de tarea

Registro de repuestos utilizados con impacto en inventario

Agenda de tareas recurrentes con notificación automática

Exportación y trazabilidad completa por norma ISO e IRAM

🧩 Módulo 9: Contabilidad y Recibos
🗄 Base de datos: mpsContabilidad

🧱 Tablas involucradas
recibos
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único del recibo
fecha_emision	DATE	Fecha del recibo
obra_id	INT (FK)	Obra a la que se vincula el recibo
monto_total	DECIMAL	Monto total
concepto	TEXT	Motivo o descripción general del cobro
destinatario	TEXT	Persona a la que se le extiende
firma_digital	TEXT	Firma digital del emisor (hash o imagen)
usuario_emisor	INT (FK)	Usuario que generó el recibo
estado	VARCHAR(30)	emitido, anulado
archivo_pdf	TEXT	Ruta o nombre del archivo PDF generado
movimientos_contables
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
fecha	DATE	Fecha del movimiento
tipo_movimiento	VARCHAR(20)	ingreso, egreso
monto	DECIMAL	Monto del movimiento
concepto	TEXT	Motivo general
referencia_recibo	INT (FK)	Relación con recibos.id si aplica
observaciones	TEXT	Comentarios adicionales
🔗 Relaciones
Cada recibo puede generar un movimiento contable (ingreso)

También se pueden registrar egresos con vinculación libre a otros conceptos

Los movimientos contables permiten generar balances por período, obra, o tipo

La firma digital garantiza la trazabilidad del documento

El archivo PDF puede guardarse localmente o compartirse por mail desde el sistema

🖥 Pantallas del módulo
1. Lista de recibos
Tabla con filtros por obra, estado, usuario emisor, fecha

Acciones: ver recibo, generar PDF, anular

2. Formulario de nuevo recibo
Selección de obra

Ingreso de monto, concepto, destinatario

Firma digital del usuario logueado

Botón para generar recibo + PDF automáticamente

3. Registro de movimientos contables
Lista por fecha, tipo, concepto

Vinculación con recibos si aplica

Posibilidad de cargar egresos manualmente

Filtros por tipo, período, obra

4. Balance contable
Gráficos y métricas: total ingresos, total egresos, saldo neto

Filtros por obra, usuario, rango de fechas

Botón para exportar el balance a PDF o Excel

5. Visualizador de PDF
Vista directa del recibo generado

Firma y datos incluidos

Botón para imprimir o reenviar por correo

🔐 Permisos por rol
Rol	Ver	Crear recibo	Anular	Ver balance
Admin	✅	✅	✅	✅
Administración	✅	✅	✅	✅
Producción	❌	❌	❌	❌
Auditor	✅	❌	❌	✅
⚙ Funcionalidades especiales
Firma digital integrada y verificable

Generación automática de recibos en PDF

Registro contable centralizado

Exportación de balances y movimientos

Anulación con motivo registrado

Compatibilidad con normas contables internas

Notificaciones automáticas en caso de movimientos elevados

🧩 Módulo 10: Configuración del Sistema
🗄 Base de datos: mpsConfig

🧱 Tablas involucradas
configuracion_sistema
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
clave	VARCHAR(100)	Nombre del parámetro (ej: modo_offline, base_predeterminada)
valor	TEXT	Valor actual del parámetro
descripcion	TEXT	Explicación o ayuda para el uso del parámetro
ultima_modificacion	TIMESTAMP	Fecha de la última actualización
modificado_por	INT (FK)	Usuario que modificó el valor
apariencia_usuario
Campo	Tipo	Descripción
id	SERIAL (PK)	Identificador único
usuario_id	INT (FK)	Usuario correspondiente
modo_color	VARCHAR(20)	claro, oscuro, automático
idioma_preferido	VARCHAR(10)	es, en, etc.
mostrar_notificaciones	BOOLEAN	Si desea ver notificaciones
tamaño_fuente	VARCHAR(10)	pequeño, normal, grande
🔗 Relaciones
configuracion_sistema se usa para definir parámetros globales accesibles por todos los módulos.

apariencia_usuario permite que cada usuario tenga su experiencia personalizada (idioma, tema, etc.).

Las configuraciones pueden editarse desde el instalador o desde el módulo visual de ajustes.

🖥 Pantallas del módulo
1. Panel de configuración global
Lista de parámetros del sistema

Edición de valores y descripciones

Registro visible de última modificación

Botón para restablecer a valores por defecto

2. Preferencias de usuario
Cambiar idioma y modo (claro/oscuro)

Activar o desactivar notificaciones

Ajustar tamaño de fuente

3. Configuración de conexión y entorno
Campos para definir conexión a bases de datos

Nombre de empresa, sede, ubicación

Selección de base por defecto (multiempresa)

4. Soporte modo offline
Activar funcionamiento sin conexión

Muestra alerta de “modo desconectado”

Botón para reconectar y sincronizar

🔐 Permisos por rol
Rol	Ver global	Editar global	Preferencias personales
Admin	✅	✅	✅
Auditor	✅	❌	✅
Usuario común	❌	❌	✅
⚙ Funcionalidades especiales
Multiempresa y multisede configurable

Idioma de la app según preferencia del usuario

Tema visual claro/oscuro personalizado

Registro de cambios en configuración global

Configuración desde el instalador inicial o desde el sistema

Sincronización manual con servidores externos

Preparado para funcionamiento offline (por interrupción de red o uso local)

## Modo Oscuro

### Tipología de Colores
El diseño de la interfaz en modo oscuro sigue una combinación de colores oscuros, azules y blancos para garantizar una experiencia visual agradable y profesional. A continuación, se detallan los colores utilizados:

- **Fondo Principal**: Negro puro (`#000000`)
- **Texto Principal**: Blanco puro (`#FFFFFF`)
- **Botones Primarios**: Azul (`#2563eb`)
- **Botones Primarios Hover**: Azul más oscuro (`#1e40af`)
- **Botones Primarios Presionados**: Azul aún más oscuro (`#1e3a8a`)
- **Bordes y Separadores**: Gris oscuro (`#2d2d2d`)
- **Texto Secundario**: Gris claro (`#d1d5db`)

### Ejemplo de Aplicación
- **Fondo de la Interfaz**: Negro puro (`#000000`)
- **Botones**:
  - Color de fondo: Azul (`#2563eb`)
  - Color de texto: Blanco puro (`#FFFFFF`)
  - Hover: Azul más oscuro (`#1e40af`)
  - Presionado: Azul aún más oscuro (`#1e3a8a`)
- **Texto**:
  - Principal: Blanco puro (`#FFFFFF`)
  - Secundario: Gris claro (`#d1d5db`)

### Implementación
Para implementar este esquema de colores en la interfaz, se recomienda utilizar un archivo de estilo (QSS) con las siguientes reglas:

```css
QWidget {
    background-color: #000000; /* Fondo negro */
    color: #FFFFFF; /* Texto blanco */
}

QPushButton {
    background-color: #2563eb; /* Azul */
    color: #FFFFFF; /* Texto blanco */
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1e40af; /* Azul más oscuro */
}

QPushButton:pressed {
    background-color: #1e3a8a; /* Azul aún más oscuro */
}

QLabel {
    color: #d1d5db; /* Texto gris claro */
}

QFrame {
    border: 1px solid #2d2d2d; /* Bordes gris oscuro */
}
```

### Ejemplo Visual
El diseño sigue un estilo similar al mostrado en la imagen de referencia, con un fondo negro, texto blanco y botones azules con efectos de hover y presionado.