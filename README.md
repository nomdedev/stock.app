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
                if not usuario or not usuario_model.tiene_permiso(usuario, self.modulo, accion):
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
                if not usuario or not usuario_model.tiene_permiso(usuario, self.modulo, accion):
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