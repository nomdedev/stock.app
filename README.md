# --- DEPENDENCIAS Y REQUISITOS DEL PROYECTO ---

## Instalación rápida del entorno

Puedes instalar todas las dependencias automáticamente usando los scripts incluidos en la carpeta `scripts`:

- **Windows:**
  ```powershell
  .\scripts\install.bat
  ```
- **Linux/Mac:**
  ```bash
  bash ./scripts/install.sh
  ```

Esto instalará todas las librerías necesarias usando el archivo `requirements.txt` y el flag `--user` para evitar problemas de permisos.

Si prefieres hacerlo manualmente:
```powershell
pip install --user -r requirements.txt
```

---

## Instalación automática de dependencias (sin intervención manual)

> **¡NUEVO!** El sistema instala automáticamente todas las dependencias críticas (incluyendo pandas y pyodbc) usando binarios precompilados (wheels) si la instalación normal falla. Esto evita errores de compilación en Windows y permite que cualquier usuario pueda iniciar la app sin conocimientos técnicos.

### ¿Cómo funciona?

- Al iniciar la app o ejecutar cualquier script principal, el sistema:
  1. Verifica si `pandas` y `pyodbc` están instalados.
  2. Si falta alguno, descarga automáticamente el archivo `.whl` correcto desde la web de Gohlke según tu versión de Python y Windows.
  3. Instala el wheel y luego instala el resto de dependencias de `requirements.txt`.
  4. Si ocurre un error, lo muestra en pantalla y te indica cómo solucionarlo.

### ¿Qué debe hacer el usuario?

- **Nada especial.** Solo ejecuta la app normalmente (`python main.py` o desde el acceso directo). El sistema se encarga de todo.
- Si ves un mensaje de error, sigue las instrucciones en pantalla o consulta al soporte.

### ¿Por qué es importante?

- Muchos usuarios de Windows no tienen compiladores instalados y no pueden instalar pandas o pyodbc desde código fuente.
- Con este sistema, la instalación es automática y robusta, incluso en equipos sin herramientas de desarrollo.

---

## Resumen del flujo automático

1. El usuario ejecuta la app o el script principal.
2. El sistema verifica e instala dependencias críticas automáticamente.
3. Si todo está correcto, la app inicia y funciona normalmente.
4. Si hay un error, se muestra un mensaje claro y se detiene la ejecución.

---

## ¿Qué hacer si falla la instalación automática?

- Verifica que tienes conexión a internet.
- Intenta ejecutar manualmente:
  ```powershell
  python scripts/auto_install_wheels.py
  ```
- Si el error persiste, descarga los wheels manualmente desde https://www.lfd.uci.edu/~gohlke/pythonlibs/ y ejecuta:
  ```powershell
  pip install --user C:\ruta\a\pandas‑2.2.2‑cp311‑cp311‑win_amd64.whl
  pip install --user C:\ruta\a\pyodbc‑5.0.1‑cp311‑cp311‑win_amd64.whl
  ```
- Luego vuelve a ejecutar:
  ```powershell
  pip install --user --prefer-binary -r requirements.txt
  ```

---

## Seguridad y robustez

- Este sistema está pensado para usuarios sin conocimientos técnicos.
- No requiere privilegios de administrador (usa `--user`).
- Si tienes problemas, consulta al soporte o revisa los logs generados.

---

## Instalación de dependencias y problemas comunes en Windows

> **IMPORTANTE:** Para minimizar problemas de instalación en Windows (especialmente errores de compilación de paquetes como `pyodbc` o `pandas`), el archivo `requirements.txt` ha sido optimizado para usar versiones que cuentan con instaladores binarios (wheels) para la mayoría de versiones de Python y Windows.

- Si al instalar dependencias ves errores relacionados con compilación ("error: Microsoft Visual C++..." o "Unable to find vcvarsall.bat"), prueba lo siguiente:
  1. Asegúrate de estar usando una versión de Python soportada (recomendado: 3.10, 3.11 o 3.12 de 64 bits).
  2. Usa el archivo `requirements.txt` incluido, que ya sugiere versiones compatibles.
  3. Si falla la instalación de algún paquete (por ejemplo, `pyodbc` o `pandas`), prueba la versión alternativa sugerida en el comentario del archivo `requirements.txt`.
  4. Si el error persiste, instala manualmente el paquete wheel desde https://www.lfd.uci.edu/~gohlke/pythonlibs/ (descarga el archivo `.whl` correspondiente a tu versión de Python y Windows y ejecuta: `pip install <archivo.whl>`).
  5. Solo como último recurso, instala las [Build Tools de Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (no es necesario en la mayoría de los casos si usas las versiones recomendadas).

- Si usas un entorno virtual (recomendado), activa el entorno antes de instalar dependencias.
- Si distribuyes la app a usuarios finales, considera usar un empaquetador como PyInstaller para evitar que tengan que instalar Python y dependencias manualmente.

### Ejemplo de instalación manual de un wheel descargado:

```powershell
pip install C:\ruta\a\pyodbc‑5.0.1‑cp311‑cp311‑win_amd64.whl
```

---

## Dependencias principales

| Paquete           | Versión recomendada |
|-------------------|--------------------|
| PyQt6             | 6.9.0              |
| PyQt6-Qt6         | 6.9.0              |
| PyQt6-sip         | 13.10.0            |
| pyodbc            | 5.2.0              |
| reportlab         | 4.4.1              |
| qrcode            | 7.4.2              |
| pandas            | 2.2.2              |
| matplotlib        | 3.8.4              |
| pytest            | 8.2.0              |
| pillow            | 10.3.0             |
| python-dateutil   | 2.9.0              |
| pytz              | 2024.1             |
| tzdata            | 2024.1             |
| openpyxl          | 3.1.2              |
| colorama          | 0.4.6              |
| ttkthemes         | 3.2.2              |

### Actualización automática

La aplicación verifica e instala/actualiza automáticamente todas las dependencias al iniciar, usando el script en `main.py`. Si falta alguna o hay una versión incorrecta, se instalará la versión recomendada y se reiniciará la app.

- Si tienes problemas de permisos, el script usará automáticamente el flag `--user`.
- Si agregas nuevas dependencias, recuerda actualizar este archivo y el `requirements.txt`.

---

Última actualización: 19 de mayo de 2025

# GUÍA VISUAL Y ESTÁNDARES DE ESTILO (PALETA PASTEL AZUL-CREMA, CONTRASTE Y SOMBRAS)


> **Tabla de contenido**
>
> 1. [Guía visual y estándares de estilo](#guía-visual-y-estándares-de-estilo-paleta-pastel-azul-crema-contraste-y-sombras)
> 2. [Principios y parámetros de diseño UI/UX](#principios-y-parámetros-de-diseño-uiux-para-toda-la-app)
> 3. [Instrucciones de instalación y configuración](#instrucciones-de-instalación-y-configuración)
> 4. [Variables globales y configuración](#configuración-de-variables-globales)
> 5. [Estructura y orden de tablas de base de datos](#estructura-y-orden-de-columnas-requeridas-para-tablas-principales)
> 6. [Patrones obligatorios de tablas y responsive](#patrón-universal-de-tablas-responsive-qtablewidget)
> 7. [Integración UI + Base de Datos y flujos](#integración-ui--base-de-datos-verificación-automática)
> 8. [Gestión de permisos y aprobaciones](#gestión-de-permisos-visibilidad-de-módulos-y-aprobaciones-admin-supervisor-usuario)
> 9. [Errores comunes y soluciones robustas](#errores-comunes-detectados-y-soluciones-aplicadas-en-vistas-principales-2025-05)
> 10. [Configuración y seguridad de la conexión a la base de datos](#configuración-y-seguridad-de-la-conexión-a-la-base-de-datos)
> 11. [Flujo de testeo automático: importación y visualización de inventario](#flujo-de-testeo-automático-importación-y-visualización-de-inventario)
> 12. [Importación de inventario desde CSV (solo admin)](#importación-de-inventario-desde-csv-solo-admin)
> 13. [Abreviaturas de colores PVC](#abreviaturas-de-colores-pvc-inventario-rehau)
> 14. [Seguridad y manejo de datos sensibles](#seguridad-y-manejo-de-datos-sensibles)

---

## Guía visual y estándares de estilo (paleta pastel azul-crema, contraste y sombras)

La aplicación utiliza una paleta pastel moderna basada en azules y cremas, con alto contraste y detalles de sombra para lograr una experiencia visual clara, profesional y agradable. Todos los módulos y widgets deben seguir estos lineamientos visuales y de estilo.

### Paleta de colores principal

- **Fondo general:** `#fff9f3` (crema pastel muy claro)
- **Azul pastel principal:** `#2563eb` (para texto, íconos y botones principales)
- **Celeste pastel:** `#e3f6fd` (fondos de botones y headers)
- **Lila pastel:** `#f3eaff` (hover de botones)
- **Rosa pastel:** `#ffe5e5` (selección y feedback)
- **Verde pastel:** `#d1f7e7` (estado online, éxito)
- **Rojo pastel:** `#ffe5e5` (errores, offline)
- **Gris pastel:** `#e3e3e3` (bordes, líneas de tabla)

### Contraste y accesibilidad

- El texto y los íconos siempre usan azul pastel `#2563eb` sobre fondo claro para máximo contraste.
- Los mensajes de error usan rojo pastel `#ef4444` sobre fondo claro.
- Los botones principales tienen fondo celeste pastel y texto azul pastel.
- Los diálogos y widgets tienen bordes redondeados y sombra sutil para destacar sobre el fondo.

### Botones modernos y sombras

- Todos los botones usan bordes redondeados de 8px, sombra sutil y colores pastel.
- El helper `estilizar_boton_icono` aplica tamaño, color y sombra uniforme a los botones con ícono.
- Ejemplo visual de botón principal:

```css
QPushButton {
    background-color: #e3f6fd;
    color: #2563eb;
    border: 1px solid #e3e3e3;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
    min-width: 80px;
    min-height: 28px;
    box-shadow: 0 2px 8px rgba(37,99,235,0.08); /* sombra sutil */
}
QPushButton:hover {
    background-color: #f3eaff;
}
QPushButton:pressed {
    background-color: #ffe5e5;
}
```

### Ejemplo de helper para botones con ícono (Python)

```python
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QSize

def estilizar_boton_icono(boton: QPushButton, tam_icono: int = 20, tam_boton: int = 32):
    boton.setIconSize(QSize(tam_icono, tam_icono))
    boton.setFixedSize(tam_boton, tam_boton)
    boton.setStyleSheet(
        """
        QPushButton {
            background-color: #e3f6fd;
            color: #2563eb;
            border-radius: 8px;
            border: 1.5px solid #e3e3e3;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(37,99,235,0.08);
        }
        QPushButton:hover {
            background-color: #f3eaff;
        }
        QPushButton:pressed {
            background-color: #ffe5e5;
        }
        """
    )
```

### Ejemplo visual de tabla y headers

```css
QTableWidget {
    background-color: #fff9f3;
    color: #2563eb;
    gridline-color: #e3e3e3;
    border: 1px solid #f6faff;
}
QTableWidget QHeaderView::section {
    background-color: #e3f6fd;
    color: #2563eb;
    font-weight: bold;
    border-radius: 8px;
    padding: 8px;
    border: 1px solid #e3e3e3;
}
```

### Sombra y profundidad

- Los widgets principales y diálogos usan sombra sutil para dar profundidad y separar visualmente del fondo.
- Ejemplo de sombra en QSS:

```css
QWidget, QDialog, QFrame, QPushButton, QTableWidget, QLabel {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(37,99,235,0.08);
}
```

---

## Estándar obligatorio para botones de acción

- Todos los botones principales y secundarios deben ser solo ícono, sin texto visible.
- El ícono debe ser representativo de la acción (ejemplo: tilde para aceptar/guardar, cruz para cancelar/cerrar, disquete para guardar, PDF para exportar, etc.).
- Usar siempre el helper estilizar_boton_icono para tamaño, color y sombra uniforme.
- El ícono debe estar en la carpeta img/ en formato SVG, fondo transparente, mínimo 20x20px.
- Si no existe el ícono, debe crearse y documentarse en checklist_botones_iconos.txt.
- Ejemplo de implementación:

```python
btn_aceptar = QPushButton()
btn_aceptar.setIcon(QIcon("img/finish-check.svg"))
btn_aceptar.setToolTip("Aceptar")
estilizar_boton_icono(btn_aceptar)
```

- No se permite texto en los botones de acción principales ni secundarios.
- Documentar cualquier excepción justificada en checklist_botones_iconos.txt y en el código.

---

## PRINCIPIOS Y PARÁMETROS DE DISEÑO UI/UX PARA TODA LA APP

Estos lineamientos deben aplicarse SIEMPRE al crear cualquier ventana, diálogo, botón, label, input, tabla, etc.
Si se requiere una excepción, debe justificarse y documentarse.

1. Padding y márgenes:
   - Padding mínimo en diálogos y widgets: 20px vertical, 24px horizontal.
   - Márgenes entre elementos: mínimo 16px.
   - Los cuadros de diálogo deben estar perfectamente centrados y con el mismo espacio a ambos lados.
2. Bordes y esquinas:
   - Bordes redondeados: 8-12px en todos los diálogos, botones y campos de entrada.
3. Tipografía:
   - Fuente: Segoe UI, Roboto, o similar sans-serif.
   - Tamaño base: 11px para mensajes secundarios, 13px para principales, 14px para títulos.
   - Peso: 500-600 para títulos y botones, 400-500 para textos normales.
   - Color de texto: #1e293b para texto principal, #ef4444 para errores, #2563eb para info, #22c55e para éxito, #fbbf24 para advertencia.
   - El texto debe estar centrado vertical y horizontalmente en diálogos y botones.
4. Botones:
   - Ancho mínimo: 80px, alto mínimo: 28px.
   - Padding horizontal: 16px.
   - Bordes redondeados: 8px.
   - Color de fondo: #2563eb para acción principal, #f1f5f9 para secundarios.
   - Color de texto: blanco en botones primarios, #1e293b en secundarios.
   - Espaciado entre botones: 16px.
5. Colores y fondo:
   - Fondo general: #f1f5f9.
   - Los diálogos de error usan #ef4444 para el texto y fondo claro.
   - Los mensajes de éxito usan #22c55e, advertencia #fbbf24, info #2563eb.
6. Íconos:
   - Siempre SVG o PNG de alta resolución.
   - Alineados con el texto y con padding de al menos 8px respecto al texto.
7. Tablas y formularios:
   - Espaciado entre filas: mínimo 8px.
   - Padding en celdas: 12px.
   - Bordes redondeados en headers y celdas: 8px.
   - No saturar de información, usar scroll y paginación si es necesario.
8. Feedback visual:
   - Mensajes breves, claros y con color adecuado.
   - Siempre usar QMessageBox o widgets personalizados con los estilos definidos.
   - El feedback debe ser inmediato tras la acción del usuario.
9. Accesibilidad:
   - Contraste alto entre texto y fondo.
   - No usar solo color para indicar estado (agregar íconos o texto).
   - Tamaños de fuente nunca menores a 10px.
10. Código:
    - Centralizar estilos en QSS global o helpers.
    - No hardcodear estilos en cada widget, salvo casos justificados.
    - Reutilizar componentes visuales y helpers para mantener coherencia.
    - Documentar cualquier excepción a estas reglas.

---

Estos principios son OBLIGATORIOS para todo el desarrollo de la app. Si se requiere una excepción, debe estar documentada en el código y en este archivo.

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

### Notas

- Asegúrate de que el servidor SQL permita conexiones remotas.
- Si cambias el puerto predeterminado (1433), incluye el puerto en `DB_SERVER`, por ejemplo: "192.168.1.100,1434".
- No compartas este archivo públicamente, ya que contiene información sensible.

### Configuración Inicial

- Crear un usuario administrador desde el módulo de usuarios.
- Configurar los parámetros iniciales en el módulo de configuración.

### Notas sobre la Conexión a la Base de Datos

El sistema ahora utiliza `pyodbc` para conectarse a SQL Server. Asegúrate de que el controlador ODBC esté instalado y configurado correctamente.

---

## Configuración y Seguridad de la Conexión a la Base de Datos

### Seguridad y buenas prácticas
- **Nunca expongas usuario, contraseña ni IP en el código fuente de los módulos.**
- Todos los datos sensibles de conexión se encuentran en `core/config.py` y solo deben modificarse allí.
- El string de conexión se construye siempre usando la función `get_connection_string(driver, database)` de `core/database.py`.
- No se deben hardcodear strings de conexión ni credenciales en scripts, módulos ni notebooks.
- El archivo `core/config.py` **no debe subirse al repositorio**. Usa `config.example.py` para compartir ejemplos.

### Conexión multi-PC y configuración visual
- El sistema permite conectarse desde varias computadoras a la PC/servidor donde están las bases de datos.
- Desde el módulo de Configuración, pestaña "Base de Datos", puedes:
  - Ver y editar la IP/servidor, usuario, contraseña y base de datos.
  - Probar la conexión antes de guardar los cambios.
  - Guardar la configuración en la base de datos para que persista entre sesiones.
  - Ver un tutorial visual que explica:
    - Cómo encontrar la IP del servidor (ejemplo: ejecutar `ipconfig` en la PC del servidor).
    - Qué poner en cada campo según el caso (red local, remoto, instancia local, etc.).
    - Qué hacer si falla la conexión (verificar firewall, usuario, contraseña, permisos de SQL Server, etc.).

### Ejemplo de flujo para el usuario
1. Ir a Configuración > Base de Datos.
2. Cambiar la IP/servidor si es necesario (por ejemplo, la IP de la PC donde está SQL Server).
3. Ingresar usuario y contraseña de SQL Server.
4. Seleccionar la base de datos a la que se quiere conectar (por ejemplo, `inventario`, `usuarios`, etc.).
5. Probar la conexión con el botón correspondiente.
6. Si la conexión es exitosa, guardar los cambios. La configuración quedará guardada y se usará en los próximos inicios.

### Notas técnicas
- El sistema utiliza una única conexión persistente por base de datos, inyectada en los modelos.
- Si la conexión falla, la app muestra un aviso y permite navegación básica en modo offline.
- Todas las acciones relevantes quedan registradas en auditoría.
- Los tests de conexión y guardado de configuración están cubiertos en los tests automáticos.

---

## Ejemplo: obtener la IP local de la PC para conexión multi-PC

Puedes obtener la IP de la PC/servidor ejecutando en la terminal de Windows:

```powershell
ipconfig
```

O bien, usando Python:

```python
import socket
print(socket.gethostbyname(socket.gethostname()))
```

Esto mostrará la IP local, por ejemplo: `192.168.88.205`. Usa esa IP en el campo `DB_SERVER` de la configuración.

---

## Ejemplo de prueba real de conexión y consulta a la base de datos

Puedes probar la conexión y consultar datos reales ejecutando el siguiente script (ajusta los parámetros si es necesario):

```python
import pyodbc

server = "192.168.88.205"  # IP de tu servidor SQL
username = "sa"
password = "mps.1887"
database = "inventario"
driver = "ODBC Driver 17 for SQL Server"

try:
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    with pyodbc.connect(connection_string, timeout=5) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 5 * FROM inventario_perfiles")
        rows = cursor.fetchall()
        print("Datos obtenidos de inventario_perfiles:")
        for row in rows:
            print(row)
except Exception as e:
    print(f"Error al consultar la base de datos: {e}")
```

Si la conexión es exitosa, verás los primeros registros de la tabla `inventario_perfiles`.

---

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

## Instrucciones para aplicar el script de estructura de tablas

Para garantizar que todas las tablas críticas del sistema tengan la estructura, el orden y los campos correctos, utiliza el script unificado `scripts/estructura_tablas_mps.sql`.

### ¿Qué hace este script?

- Elimina (si existen) y crea desde cero todas las tablas principales de inventario, usuarios, obras, auditoría, permisos y solicitudes de aprobación, con el orden y tipos de columnas requeridos por el sistema y los tests.
- Es compatible con SQL Server (puedes adaptarlo fácilmente para PostgreSQL cambiando los tipos y funciones de autoincremento).

### ¿Cómo aplicarlo?

1. **Haz un respaldo de tus datos actuales** si tienes información importante en las tablas.
2. Abre SQL Server Management Studio (SSMS) o tu herramienta de administración de base de datos.
3. Abre el archivo `scripts/estructura_tablas_mps.sql`.
4. Ejecuta el script en cada base de datos correspondiente:
   - Para la base de datos de inventario.
   - Para la base de datos de usuarios.
   - Para la base de datos de auditoría.
   - (Y cualquier otra base relevante que uses en tu sistema).
5. Verifica que las tablas se hayan creado correctamente y que el orden de columnas coincida con lo documentado.

### Notas importantes

- El script elimina las tablas si existen, por lo que **borra todos los datos previos**. Úsalo solo en entornos de desarrollo o tras hacer un backup.
- Si necesitas migrar datos legacy, primero exporta la información, luego impórtala respetando el nuevo orden de columnas.
- Si usas PostgreSQL, reemplaza `IDENTITY(1,1)` por `SERIAL` o `GENERATED ALWAYS AS IDENTITY`, y ajusta los tipos de fecha/hora.

---

## Seguridad y configuración de la base de datos

- La app utiliza una única fuente de configuración para la conexión a la base de datos, centralizada en `core/database.py` y/o `core/config.py`.
- No es necesario crear ni mantener un archivo `.env` para la conexión si ya existe la configuración centralizada.
- Todos los scripts y módulos deben reutilizar la clase `InventarioDatabaseConnection` (o la correspondiente) para acceder a la base de datos, evitando duplicidad y errores de seguridad.
- Si cambias la configuración de la base, hazlo solo en el archivo centralizado y no en cada script.
- El script de importación de inventario (`procesar_e_importar_inventario.py`) ya utiliza esta conexión centralizada y no requiere variables de entorno ni archivos de configuración adicionales.

---

## Flujo seguro de importación de inventario

1. El usuario arrastra el archivo CSV o Excel.
2. El script limpia, normaliza y valida los datos (incluyendo duplicados y formato de columnas).
3. Se genera un backup SQL de la tabla antes de modificar datos.
4. Solo si el usuario confirma, se realiza la importación.
5. Todos los errores y advertencias se muestran antes de modificar la base.

---

## Eliminación de scripts innecesarios

- Solo se mantiene el script principal `procesar_e_importar_inventario.py` en la carpeta `scripts`.
- Todos los scripts auxiliares de limpieza, importación y validación han sido eliminados para evitar confusión y mejorar la seguridad.

---

## Flujo de testeo automático: importación y visualización de inventario

Para asegurar la robustez y trazabilidad del proceso de importación de datos de inventario desde archivos CSV a la base de datos SQL Server, el sistema cuenta con tests automáticos que validan tanto la importación como la visualización de los datos en la aplicación.

### Objetivo
- Garantizar que la importación de inventario desde CSV a la tabla `inventario_perfiles` se realiza correctamente, sin errores y con los datos completos.
- Verificar que los datos importados pueden ser consultados y visualizados correctamente desde la aplicación.
- Detectar rápidamente cualquier cambio en el formato del CSV, en la estructura de la tabla o en la lógica de importación que pueda afectar la robustez del sistema.

### Ejecución de los tests automáticos

1. **Ubicación de los tests:**
   - Los tests se encuentran en la carpeta `tests/`.
   - Los principales son:
     - `tests/test_importar_inventario_csv.py`: Valida la importación desde CSV.
     - `tests/test_query_inventario_perfiles.py`: Verifica la consulta y visualización de los datos importados.

2. **Comando para ejecutar todos los tests:**
   ```bash
   pytest tests/
   ```
   O bien, para ejecutar solo el test de importación:
   ```bash
   pytest tests/test_importar_inventario_csv.py
   ```

3. **Salida esperada:**
   - Todos los tests deben pasar (`PASSED`).
   - Ejemplo de salida:
     ```
     ============================= test session starts =============================
     collected 3 items

     tests/test_importar_inventario_csv.py ...                             [100%]

     ========================== 3 passed in 2.10s ================================
     ```
   - Si algún test falla, se mostrará el motivo y la línea exacta del error.

### Buenas prácticas y recomendaciones
- Antes de importar un nuevo archivo CSV, ejecutar los tests para validar que el formato es compatible y que la importación será exitosa.
- Si se modifica la estructura de la tabla `inventario_perfiles` o el script de importación, actualizar y volver a ejecutar los tests.
- Mantener los tests actualizados ante cualquier cambio en el flujo de importación o visualización.
- Documentar en los tests cualquier supuesto sobre el formato del CSV o la estructura de la base de datos.

### Estándar de robustez esperado
- El proceso de importación debe:
  - Detectar y reportar errores de formato o columnas faltantes en el CSV.
  - Validar que los campos clave no sean nulos tras la importación.
  - Garantizar que la tabla contiene registros después de la importación.
  - Permitir la consulta y visualización inmediata de los datos importados.
- Los tests automáticos deben ejecutarse sin intervención manual y pasar en todos los entornos compatibles.

---

## Importación de inventario desde CSV (solo admin)

- Solo el usuario admin puede cargar el inventario desde el archivo `inventario/inventario_perfiles_final.csv`.
- El botón de importación está en la pestaña de configuración.
- El sistema valida el rol y muestra un mensaje de éxito o error.
- El proceso borra la tabla y carga todos los registros del CSV a SQL Server.
- Si ocurre un error, se muestra el detalle en pantalla.

### Requisitos
- El archivo debe estar generado y actualizado.
- La estructura de la tabla `inventario_perfiles` debe coincidir con las columnas del CSV.

### Ejemplo de feedback
- "Inventario cargado correctamente (2549 filas)."
- "Solo el usuario admin puede importar el inventario."
- "Error al cargar inventario: ..."

---

## Abreviaturas de colores PVC (Inventario REHAU)

| Abreviatura | Color real      |
|-------------|----------------|
| Rob         | Roble          |
| Nog         | Nogal          |
| Win         | Winchester     |
| Nut         | Nutmeg         |
| Hab         | Habano         |
| B.Smoke     | Black Smoke    |
| B.Brow      | Black Brown    |
| Qua         | Quartz         |
| Sheff       | Sheffield      |
| Tit         | Titanium       |
| N.M         | Negro M        |
| Ant L       | Ant L          |
| Ant M       | Ant M          |
| Turn        | Turner         |
| Mon         | Monument       |
| Bco         | Blanco         |

> Estas abreviaturas se usan para desglosar y mapear los colores de los perfiles PVC en la base de datos proveniente del proveedor REHAU. Es fundamental respetar este mapeo en el módulo de inventario para asegurar la correcta identificación y visualización de los productos.

---

## Seguridad y manejo de datos sensibles

### Prácticas seguras en la app

- **Nunca expongas credenciales ni datos sensibles en el código fuente.**
- La configuración de la base de datos (host, usuario, contraseña, nombre de base, driver) se gestiona mediante variables de entorno y el paquete `python-dotenv`.
- El archivo `.env` debe estar en la raíz del proyecto y nunca subirse a repositorios públicos. Usa el archivo `.env.example` como plantilla.
- El script principal lee automáticamente las variables de entorno y no funcionará si faltan datos críticos.
- Si compartes el proyecto, elimina o ignora cualquier archivo `.env` real.

### Ejemplo de archivo `.env` (no subir a git):

```
DB_SERVER=192.168.88.205
DB_DATABASE=inventario
DB_USERNAME=sa
DB_PASSWORD=mps.1887
DB_DRIVER=ODBC Driver 17 for SQL Server
```

### Cómo se usa en el código

```python
from dotenv import load_dotenv
import os
load_dotenv()
DB_CONFIG = {
    'server': os.getenv('DB_SERVER', ''),
    'database': os.getenv('DB_DATABASE', ''),
    'username': os.getenv('DB_USERNAME', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'driver': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
}
```

- Si alguna variable falta, el script lo notificará y no se conectará a la base de datos.
- El backup de la base de datos se guarda en la carpeta `inventario/backups_sql` antes de cualquier importación masiva.

---

## Flujo seguro de importación de inventario

1. El usuario arrastra el archivo CSV o Excel.
2. El script limpia, normaliza y valida los datos (incluyendo duplicados y formato de columnas).
3. Se genera un backup SQL de la tabla antes de modificar datos.
4. Solo si el usuario confirma, se realiza la importación.
5. Todos los errores y advertencias se muestran antes de modificar la base.

---

## Eliminación de scripts innecesarios

- Solo se mantiene el script principal `procesar_e_importar_inventario.py` en la carpeta `scripts`.
- Todos los scripts auxiliares de limpieza, importación y validación han sido eliminados para evitar confusión y mejorar la seguridad.

---
