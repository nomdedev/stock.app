# Documentación y estándares del proyecto

Este proyecto utiliza una estructura de documentación modular. Todos los estándares y guías obligatorias están en la carpeta `docs/`.

## Índice de estándares y guías

- [Estándares visuales](docs/estandares_visuales.md) *(actualizado: headers de tablas fondo #f8fafc, radio 4px, fuente 10px, sin negrita)*
- [Estándares de logging y feedback visual](docs/estandares_logging.md)
- [Estándares de seguridad y manejo de datos sensibles](docs/estandares_seguridad.md)
- [Estándares de feedback visual y procedimientos de carga](docs/estandares_feedback.md)
- [Estándares de auditoría y registro de acciones](docs/estandares_auditoria.md)

Lee y respeta cada estándar antes de modificar o agregar código. Cualquier excepción debe estar documentada en el archivo correspondiente y en el código.

---

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

- Si el error persiste, descarga los wheels manualmente desde <https://www.lfd.uci.edu/~gohlke/pythonlibs/> y ejecuta:

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
  4. Si el error persiste, instala manualmente el paquete wheel desde <https://www.lfd.uci.edu/~gohlke/pythonlibs/> (descarga el archivo `.whl` correspondiente a tu versión de Python y Windows y ejecuta: `pip install <archivo.whl>`).
  5. Solo como último recurso, instala las [Build Tools de Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (no es necesario en la mayoría de los casos si usas las versiones recomendadas).

- Si usas un entorno virtual (recomendado), activa el entorno antes de instalar dependencias.
- Si distribuyes la app a usuarios finales, considera usar un empaquetador como PyInstaller para evitar que tengan que instalar Python y dependencias manualmente.

### Ejemplo de instalación manual de un wheel descargado

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
> 15. [Estándar visual y técnico para pestañas de configuración](#estándar-visual-y-técnico-para-pestañas-de-configuración-qtabwidget)
> 16. [Sidebar: estándar visual obligatorio](#sidebar-estándar-visual-obligatorio)

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
    /* box-shadow eliminado por incompatibilidad QSS */
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

## Sidebar: estándar visual obligatorio

> El sidebar debe cumplir SIEMPRE con los siguientes parámetros estéticos (no modificables):
>
> - Fondo blanco.
> - Botones con bordes redondeados de 8px y borde gris pastel (#e3e3e3) por defecto.
> - El botón activo tiene borde azul (#2563eb) en todo el contorno y el borde izquierdo más grueso, pero fondo blanco.
> - El texto del botón activo es azul (#2563eb), el resto gris oscuro (#1f2937).
> - El tamaño de fuente de los botones es 12px, nunca mayor.
> - El padding horizontal es 10px, el ancho mínimo 120px y máximo 160px, altura mínima 32px.
> - No usar transiciones ni efectos no soportados por QSS.
> - El hover solo cambia el fondo a gris claro (#f3f4f6), nunca azul.
> - Estos parámetros son OBLIGATORIOS y deben respetarse en todos los módulos y temas.

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

> ⚠️ **IMPORTANTE:**
>
> **Estos parámetros estéticos y de diseño son OBLIGATORIOS y NO pueden ser modificados ni ignorados bajo ninguna circunstancia.**
> Si se requiere una excepción, debe estar justificada y documentada aquí y en el código correspondiente.
>
> **Este bloque debe ser respetado SIEMPRE en toda la app.**

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

---

## Estándar visual y técnico para pestañas de configuración (QTabWidget)

> **Este estándar debe aplicarse a todas las pestañas de configuración y cualquier sección nueva que se agregue en el futuro.**

### Paleta de colores y estilo

- Fondo general: `#fff9f3` (crema pastel muy claro)
- Azul pastel principal: `#2563eb` (texto, íconos, botones principales)
- Celeste pastel: `#e3f6fd` (fondos de botones, headers, pestañas activas)
- Gris pastel: `#e3e3e3` (bordes, líneas de tabla)
- Verde pastel: `#d1f7e7` (éxito)
- Rojo pastel: `#ffe5e5` (errores)
- Lila pastel: `#f3eaff` (hover)
- Sombra sutil: `box-shadow: 0 2px 8px rgba(37,99,235,0.08)`

### QTabWidget y QTabBar

- Bordes redondeados: 12px en el panel y 8px en las pestañas.
- Pestañas con fondo celeste pastel y texto azul pastel.
- Pestaña activa: fondo crema, borde azul pastel.
- Padding horizontal: 24px, vertical: 20px en el contenido de cada pestaña.
- Espaciado entre pestañas: 8px.

#### QSS recomendado para QTabWidget

```css
QTabWidget::pane {
    border-radius: 12px;
    background: #f1f5f9;
}
QTabBar::tab {
    min-width: 160px;
    min-height: 36px;
    font-size: 14px;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 24px;
    margin-right: 8px;
    background: #e3f6fd;
    color: #2563eb;
}
QTabBar::tab:selected {
    background: #fff9f3;
    color: #2563eb;
    border: 2px solid #2563eb;
}
```

### Layout interno de cada pestaña

- Usar siempre QVBoxLayout con `setContentsMargins(24, 20, 24, 20)` y `setSpacing(16)`.
- Título principal: QLabel, fuente 18px, bold, color azul pastel, alineado al centro.
- Labels secundarios: fuente 13px, color #1e293b, alineados al centro.
- Botones: solo ícono, fondo celeste pastel, borde 1.5px gris pastel, sombra sutil, sin texto visible, tamaño mínimo 32x32px. Usar helper `estilizar_boton_icono`.
- Tablas: headers con fondo celeste pastel, celdas con fondo crema, bordes redondeados 8px, color de texto azul pastel.
- Feedback visual: QLabel con color y emoji según tipo (éxito, error, advertencia, info), fondo claro, bordes redondeados, padding 8px 16px.
- Siempre usar `addStretch()` al final para mantener el contenido arriba y el espacio visual limpio.

#### Ejemplo de layout de una pestaña

```python
layout = QVBoxLayout(tab_widget)
layout.setContentsMargins(24, 20, 24, 20)
layout.setSpacing(16)
label_titulo = QLabel("Título de la sección")
label_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563eb;")
label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
layout.addWidget(label_titulo)
# ...otros widgets...
layout.addStretch()
```

### Feedback visual dentro de pestañas

- Usar QLabel para mensajes de feedback inmediato.
- Colores y emojis según tipo:
  - Éxito: verde pastel, "✅"
  - Error: rojo pastel, "❌"
  - Advertencia: naranja pastel, "⚠️"
  - Info: azul pastel, "ℹ️"
- Ejemplo de uso:

```python
label_feedback = QLabel()
label_feedback.setStyleSheet("font-size: 13px; padding: 8px 0;")
label_feedback.setText("<span style='color:#22c55e;'>✅ Acción realizada con éxito</span>")
```

### Tooltips y ayuda contextual

- Todos los botones y campos deben tener `setToolTip()` con una descripción clara de su función.
- Si la pestaña es compleja, agregar un ícono de ayuda ("img/info.svg") que muestre un QDialog con instrucciones.

### Excepciones visuales

- Si una pestaña requiere un diseño diferente, debe justificarse en el código y documentarse aquí.
- Ejemplo: "La pestaña X utiliza un layout especial por requerimiento de UX para ..."

---

**Este estándar debe copiarse y adaptarse en cada módulo nuevo que agregue pestañas o secciones de configuración.**

---

## Instrucciones de Instalación y Configuración

### Requisitos Previos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Librería `pyodbc` para la conexión a SQL Server.
- Controlador ODBC para SQL Server (recomendado: **ODBC Driver 17 for SQL Server**).

### Pasos para la Instalación

1. Clonar el repositorio:

   ```bash
   git clone <URL_DEL_REPOSITOR>
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
DB_PASSWORD = "<tu_contraseña>"     # Contraseña del usuario (NO usar credenciales reales en ejemplos)
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

## Configuración y seguridad de la conexión a la base de datos

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

## Bloqueo de tests automáticos de UI (PyQt)

> **Nota:** La cobertura de tests automáticos de UI (PyQt) está documentada en `docs/bloqueo_tests_ui.md`. Allí se explica el diagnóstico, las causas y los próximos pasos sugeridos para poder ejecutar tests de UI en el entorno actual. Revisar ese archivo antes de intentar ampliar o migrar la cobertura de tests visuales.

---

## Trazabilidad y logs de acciones de usuario (auditoría en terminal)

> **IMPORTANTE:**
>
> Todos los controladores principales de la app (Inventario, Obras, Pedidos, Compras, Logística, Usuarios, Auditoría, Configuración, Herrajes, Vidrios, etc.) generan logs explícitos en la terminal cada vez que se ejecuta una acción relevante (alta, baja, edición, consulta, etc.).
>
> **¿Qué significa esto?**
>
> - Cada vez que un usuario pulsa un botón o realiza una acción que modifica o consulta datos, se imprime en la terminal un log como:
>
>   ```
>   [LOG ACCIÓN] Ejecutando acción 'agregar_material' en módulo 'inventario' por usuario: juan (id=5)
>   [LOG ACCIÓN] Acción 'agregar_material' en módulo 'inventario' finalizada con éxito.
>   ```
>
>   o, si ocurre un error:
>
>   ```
>   [LOG ACCIÓN] Error en acción 'agregar_material' en módulo 'inventario': <detalle del error>
>   ```
>
> - Esto permite saber exactamente qué se está ejecutando, en qué orden y con qué usuario, facilitando la depuración y la auditoría.
> - Puedes analizar la secuencia de acciones y detectar si el flujo es correcto o si hay errores de lógica o permisos.
>
> **¿Dónde ver estos logs?**
>
> - Simplemente abre la terminal donde ejecutas la app. Todos los logs de acciones aparecerán ahí, junto con los logs de arranque y dependencias.
>
> - Si necesitas guardar estos logs para análisis posterior, puedes redirigir la salida de la terminal a un archivo:
>
>   ```powershell
>   python main.py > logs/acciones.log 2>&1
>   ```
>
> - Consulta también los estándares de logging en `docs/estandares_logging.md`.

---

## Sombra visual (depth/shadow) en widgets y botones

**Qt NO soporta la propiedad `box-shadow` en QSS.**

- Para lograr el efecto de sombra visual (depth) en widgets, tarjetas, botones, diálogos, etc., se debe usar SIEMPRE `QGraphicsDropShadowEffect` desde Python.
- No usar ni dejar referencias a `box-shadow` en QSS, ya que genera warnings y no tiene efecto.
- Ejemplo recomendado para aplicar sombra a un widget o botón:

```python
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

sombra = QGraphicsDropShadowEffect(widget)
sombra.setBlurRadius(16)  # Ajustar según necesidad visual
sombra.setColor(QColor(37, 99, 235, 60))  # Color pastel azul, alpha bajo
sombra.setOffset(0, 4)  # Desplazamiento vertical
widget.setGraphicsEffect(sombra)
```

- Para tarjetas, usar un blur mayor (ej: 24-32), para botones uno menor (ej: 8-16).
- Documentar en el código cualquier excepción justificada.
- Si se requiere sombra en varios widgets, crear un helper reutilizable.

**Regla:**
> Siempre usar QGraphicsDropShadowEffect para sombras visuales en la app. Nunca usar box-shadow en QSS.

---

## Permisos, roles y feedback visual

- El usuario admin (id_rol=1) tiene acceso total a todos los módulos y puede modificar roles/permisos.
- Solo el admin puede modificar roles y permisos. Ningún otro usuario puede editar al admin ni modificar el rol admin.
- Si un usuario no tiene acceso a ningún módulo, la UI muestra un mensaje visual claro y solo permite acceso a Configuración.
- La lógica de visibilidad de módulos y pestañas es robusta y segura: nunca se muestran ni permiten accesos no autorizados.
- El backend valida siempre los permisos, incluso si la UI los oculta.
- Usar siempre el QSS global de `themes/light.qss`. Prohibido aplicar estilos embebidos salvo excepción documentada.
- Los mensajes de error, advertencia y éxito deben ser claros, accesibles y visibles en la UI.
- Si ocurre un error de permisos, se muestra mensaje visual inmediato y se registra en auditoría.
- No debe haber advertencias QSS ni bloqueos visuales tras login. Si ocurre, documentar la causa y solución.

### Ejemplo de mensaje visual si no hay módulos permitidos

> "No tienes acceso a ningún módulo. Contacta al administrador para revisar tus permisos."

### Recomendaciones para desarrolladores

- Antes de modificar la gestión de permisos, ejecuta el script `scripts/bootstrap_roles_permisos.sql` en la base de datos `users` para asegurar que el admin tiene permisos totales.
- Documenta cualquier excepción visual o de permisos en este archivo y en el código afectado.
- Consulta siempre los estándares de seguridad y feedback visual en `docs/estandares_seguridad.md` y `docs/estandares_feedback.md`.

---

# GESTIÓN DE USUARIOS Y PERMISOS POR USUARIO (MAYO 2025)

Desde mayo 2025, la gestión de usuarios y la pestaña de permisos por usuario se encuentran en el módulo Usuarios, no en Configuración.

### Gestión de usuarios (Usuarios > Usuarios)

- Visualización de usuarios en tabla, con búsqueda y acciones (agregar, exportar).
- Feedback visual inmediato y accesible.

### Permisos por usuario (Usuarios > Permisos por usuario)

- Selección de usuario mediante combo.
- Tabla de módulos con checkboxes (ver, modificar, aprobar) y botón para guardar permisos.
- Solo admin puede modificar roles/permisos.

### Estándares visuales

- Headers de todas las tablas: fondo #f8fafc (muy claro), radio 4px, fuente 10px, sin negrita.
- Uso exclusivo de QSS global (themes/light.qss).

### Referencias cruzadas

- Ver también: docs/estandares_visuales.md, docs/estandares_feedback.md, docs/estandares_auditoria.md.

---

## Recursos y temas visuales

- Los archivos QSS de temas deben estar en `resources/qss/`.
- Los íconos deben estar en `resources/icons/`.
- Los scripts de base de datos deben estar en `scripts/db/`.
- Los archivos PDF y Excel de auditoría/documentación deben estar en `docs/auditoria/`.
- Si existen archivos QSS en `themes/`, deben eliminarse si ya están en `resources/qss/` y no son requeridos por compatibilidad.
- El código debe apuntar a las rutas de recursos centralizadas.

Ejemplo de carga de tema:
```python
qss_path = os.path.join('resources', 'qss', 'theme_light.qss')
```

---

## Convención de tests: unitarios vs integración

- **Tests unitarios**: No dependen de base de datos real ni servicios externos. Usan mocks y stubs. Se ubican en las subcarpetas de `tests/` por módulo (ej: `tests/obras/`, `tests/inventario/`, etc.).
- **Tests de integración**: Verifican la interacción real con la base de datos u otros servicios. Se ubican en archivos con sufijo `_integracion.py` o en subcarpetas específicas. Solo deben ejecutarse en entornos preparados.
- Los tests que requieren concurrencia, transacciones reales o validación de integridad (ej: optimistic lock) deben migrarse a integración y no ejecutarse como unitarios.
- Para agregar un nuevo test:
  1. Si es unitario, usa mocks y colócalo en la subcarpeta del módulo.
  2. Si requiere base real, colócalo en un archivo `*_integracion.py` y documenta los prerequisitos.
- Ejecuta todos los tests unitarios con:
  ```powershell
  pytest tests/ --maxfail=5 --disable-warnings -v
  ```
- Ejecuta solo los de integración cuando el entorno esté preparado:
  ```powershell
  pytest tests/obras/test_obras_optimistic_lock_integracion.py
  ```

---

## Configuración y seguridad

- Todas las variables sensibles y de entorno deben definirse en un archivo `.env` (no versionado).
- Ejemplo de archivo: `.env.example2` (renómbralo a `.env` y completa los valores).
- El archivo `core/config.py` carga automáticamente las variables usando `python-dotenv`.
- Nunca subas `.env` real ni credenciales al repositorio.
- Si agregas una nueva variable de configuración, documenta su propósito en `.env.example2` y en este README.

---

## Configuración y seguridad de variables de entorno (.env)

La aplicación utiliza un archivo `.env` para gestionar todas las variables sensibles y de entorno. Nunca subas tus credenciales reales al repositorio.

- Usa el archivo `.env.example` como plantilla: cópialo y renómbralo a `.env` en la raíz del proyecto.
- Completa los valores según tu entorno (servidor, usuario, contraseña, etc.).
- Todas las variables requeridas están documentadas en `.env.example` y son leídas automáticamente por la app.
- El archivo `.env` debe estar en `.gitignore` y nunca debe compartirse ni subirse a ningún repositorio.
- Si necesitas compartir la configuración, usa solo `.env.example` (sin datos reales).

### Variables principales

- `DB_SERVER`, `DB_USERNAME`, `DB_PASSWORD`, `DB_PORT`, `DB_DEFAULT_DATABASE`, etc.
- Consulta y edita el archivo `.env.example` para ver todas las variables soportadas.

### Seguridad

- Nunca dejes credenciales hard-coded en el código fuente ni en notebooks.
- Si encuentras datos sensibles en el código, reemplázalos por variables de entorno y actualiza `.env.example`.
- El sistema carga automáticamente las variables usando `python-dotenv`.

---

## Organización de tests y fixtures

- Los tests están organizados en subcarpetas por módulo dentro de `tests/` (ej: `tests/obras/`, `tests/inventario/`, etc.).
- Los datos de prueba reutilizables (fixtures) se encuentran en `tests/fixtures/`.
- Cada módulo puede tener su propio README en la subcarpeta de tests para explicar casos especiales.
- Los tests unitarios usan mocks y datos de fixtures; los de integración pueden requerir base real y deben estar claramente separados.
- Consulta y edita `tests/fixtures/README.md` para ver la convención de fixtures y cómo usarlos en los tests.

---

## Estilos visuales y QSS

- Todos los estilos visuales de la app están centralizados en dos archivos QSS:
  - `resources/qss/theme_light.qss`
  - `resources/qss/theme_dark.qss`
- **No se permite** el uso de `setStyleSheet` embebido en widgets/componentes, excepto para aplicar el theme global o personalizar dialogs (ejemplo: QMessageBox, QDialog), debidamente documentado.
- Si encuentras un uso de `setStyleSheet` fuera de estos casos, repórtalo y migra el estilo al QSS global.
- Consulta `docs/estandares_visuales.md` para detalles y excepciones documentadas.

---
