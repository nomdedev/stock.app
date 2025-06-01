import os
import sys
import pandas as pd
import numpy as np
import unicodedata
import shutil
import logging
from datetime import datetime
from dotenv import load_dotenv
from core.database import InventarioDatabaseConnection

# --- INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS CRÍTICAS (WHEELS) ---
def instalar_dependencias_criticas():
    """
    Instala automáticamente pandas y pyodbc usando wheels precompilados si la instalación normal falla.
    Esto evita errores de compilación en Windows y asegura que la app pueda iniciar en cualquier entorno.
    """
    import urllib.request
    import subprocess
    import platform
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"  # Ej: 311 para Python 3.11
    arch = platform.architecture()[0]
    py_tag = f"cp{py_version}"
    win_tag = "win_amd64" if arch == "64bit" else "win32"
    wheels = {
        "pandas": f"pandas-2.2.2-{py_tag}-{py_tag}-{win_tag}.whl",
        "pyodbc": f"pyodbc-5.0.1-{py_tag}-{py_tag}-{win_tag}.whl"
    }
    url_base = "https://download.lfd.uci.edu/pythonlibs/archive/"
    def instalar_wheel(paquete, wheel_file):
        url = url_base + wheel_file
        local_path = os.path.join(os.getcwd(), wheel_file)
        try:
            print(f"Descargando e instalando wheel para {paquete}...")
            urllib.request.urlretrieve(url, local_path)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", local_path])
            os.remove(local_path)
            print(f"✅ {paquete} instalado desde wheel.")
            return True
        except Exception as e:
            print(f"❌ Error instalando {paquete} desde wheel: {e}")
            return False
    def instalar_dependencia(paquete, version):
        try:
            if version:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", f"{paquete}=={version}", "--prefer-binary"])
            else:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", paquete, "--prefer-binary"])
            print(f"✅ {paquete} instalado normalmente.")
            return True
        except Exception:
            if paquete in wheels:
                return instalar_wheel(paquete, wheels[paquete])
            return False
    requeridos = [("pandas", "2.2.2"), ("pyodbc", "5.0.1")]
    for paquete, version in requeridos:
        instalar_dependencia(paquete, version)
    # Instalar el resto de requirements.txt
    try:
        print("Instalando el resto de dependencias desde requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--prefer-binary", "-r", "requirements.txt"])
        print("✅ Todas las dependencias instaladas correctamente.")
    except Exception as e:
        print(f"❌ Error instalando requirements.txt: {e}")
        print("Por favor, revisa los logs y ejecuta manualmente si es necesario.")

# Ejecutar instalación automática antes de cualquier importación pesada
def _verificar_e_instalar_dependencias():
    try:
        import pandas
        import pyodbc
    except ImportError:
        print("Instalando dependencias críticas automáticamente...")
        instalar_dependencias_criticas()

_verificar_e_instalar_dependencias()

# Cargar variables de entorno desde .env si existe
load_dotenv()

# --- CONFIGURACIÓN SEGURA ---
def get_db_connection():
    return InventarioDatabaseConnection()

TABLA_SQL = 'inventario_perfiles'
COLUMNS = [
    'codigo', 'descripcion', 'tipo', 'tipo_material', 'acabado', 'longitud',
    'stock', 'pedidos', 'ubicacion', 'proveedor', 'observaciones', 'activo'
]

# --- LOGGING PARA AUDITORÍA ---
logger = logging.getLogger("importacion_inventario")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/importacion_inventario.log", encoding="utf-8")
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

# --- EXCEPCIÓN PERSONALIZADA ---
class PermisoDenegadoError(Exception):
    pass

# --- VALIDACIÓN DE SEGURIDAD ---
def validar_configuracion_db():
    try:
        db = get_db_connection()
        db.conectar()
        db.cerrar_conexion()
    except Exception as e:
        print(f"\n❌ Error de conexión a la base de datos: {e}")
        print("Revisa la configuración centralizada en core/database.py y asegúrate de que los datos sean correctos.")
        sys.exit(1)

# --- FUNCIONES DE LIMPIEZA Y NORMALIZACIÓN ---
def limpiar_texto(texto):
    if pd.isnull(texto):
        return ''
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    texto = texto.replace('"', '').replace("'", '').strip()
    return texto

def limpiar_codigo(codigo):
    if pd.isnull(codigo):
        return ''
    codigo = str(codigo).replace(',', '').replace('..', '.').replace('-', '').replace('_', '')
    codigo = ''.join([c for c in codigo if c.isdigit() or c == '.'])
    codigo = codigo.strip('.')
    while '..' in codigo:
        codigo = codigo.replace('..', '.')
    return codigo

def limpiar_longitud(longitud):
    if pd.isnull(longitud):
        return ''
    longitud = str(longitud).upper().replace('M', '').replace(' ', '').replace(',', '.')
    longitud = ''.join([c for c in longitud if c.isdigit() or c == '.'])
    try:
        return str(float(longitud))
    except Exception:
        return ''

def agregar_columnas_faltantes(df):
    for col in COLUMNS:
        if col not in df.columns:
            if col == 'activo':
                df[col] = 1
            elif col == 'proveedor':
                df[col] = 'REHAU'
            else:
                df[col] = ''
    return df[COLUMNS]

def desglose_descripcion(df):
    # Ejemplo simple: puedes mejorar la lógica según tus necesidades
    if 'descripcion' in df.columns:
        df['tipo'] = df['descripcion'].str.split().str[0].fillna('')
        df['longitud'] = df['descripcion'].str.extract(r'(\d{1,2}[\.,]\d+)').fillna('')
        df['acabado'] = df['descripcion'].str.extract(r'Bco|Mar|Ant|Rob|Nog|Win|Nut|Hab|B\.Brow|Qua|Sheff|Tit|Negro|Turn|Mon', expand=False).fillna('')
    return df

def limpiar_dataframe(df):
    for col in df.columns:
        if col in ['codigo']:
            df[col] = df[col].apply(limpiar_codigo)
        elif col in ['descripcion', 'tipo', 'tipo_material', 'acabado', 'ubicacion', 'proveedor', 'observaciones']:
            df[col] = df[col].apply(limpiar_texto)
        elif col in ['stock', 'pedidos', 'longitud']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def backup_tabla_sql():
    from core.database import InventarioDatabaseConnection
    import pyodbc
    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_table = f"{TABLA_SQL}_backup_{fecha}"
    backup_dir = os.path.join('inventario', 'backups_sql')
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"{backup_table}.sql")
    db = InventarioDatabaseConnection()
    try:
        db.conectar()
        # Crear tabla backup
        db.ejecutar_query(f"SELECT * INTO {backup_table} FROM {TABLA_SQL}")
        # Exportar datos a archivo SQL (solo datos, formato INSERT)
        conn = db.connection
        if conn is None:
            raise RuntimeError("No se pudo obtener la conexión a la base de datos para el backup.")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {backup_table}")
        columns = [column[0] for column in cursor.description]
        with open(backup_file, 'w', encoding='utf-8') as f:
            for row in cursor.fetchall():
                values = []
                for v in row:
                    if v is None:
                        values.append('NULL')
                    elif isinstance(v, (int, float)):
                        values.append(str(v))
                    else:
                        # Solución robusta: usar format() en vez de f-string para evitar problemas de comillas
                        values.append("'{}'".format(str(v).replace("'", "''")))
                sql = f"INSERT INTO {backup_table} ({','.join(columns)}) VALUES ({','.join(values)});\n"
                f.write(sql)
        print(f"Backup de la tabla realizado en: {backup_file}")
    finally:
        db.cerrar_conexion()

def importar_a_sql(df):
    db = get_db_connection()
    try:
        db.conectar()
        db.ejecutar_query(f"DELETE FROM {TABLA_SQL}")
        for _, row in df.iterrows():
            valores = [row[col] for col in COLUMNS]
            placeholders = ','.join(['?'] * len(COLUMNS))
            sql = f"INSERT INTO {TABLA_SQL} ({','.join(COLUMNS)}) VALUES ({placeholders})"
            try:
                db.ejecutar_query(sql, valores)
            except Exception as e:
                print(f"Error al insertar fila: {e} | Valores: {valores}")
        print("Importación completada. Los datos están en la base de datos.")
    finally:
        db.cerrar_conexion()

# --- FLUJO PRINCIPAL DE IMPORTACIÓN (MODULAR Y UI-FRIENDLY) ---
def importar_inventario_desde_archivo(archivo_path, usuario_actual, confirmar_importacion_callback=None):
    """
    Importa inventario desde un archivo CSV/Excel a la base de datos, siguiendo el flujo seguro y centralizado.
    Solo permite ejecución si el usuario es admin.
    Devuelve un dict con el resultado y mensajes para la UI.
    """
    resultado = {"exito": False, "mensajes": [], "advertencias": [], "errores": []}
    try:
        # 1. Validar permisos
        if not usuario_actual or not getattr(usuario_actual, "es_admin", False):
            logger.warning(f"Intento de importación sin permisos por usuario: {usuario_actual}")
            raise PermisoDenegadoError("Solo el usuario admin puede importar el inventario.")
        # 2. Validar archivo
        if not os.path.exists(archivo_path):
            raise FileNotFoundError(f"Archivo no encontrado: {archivo_path}")
        ext = os.path.splitext(archivo_path)[1].lower()
        if ext in ['.xls', '.xlsx']:
            df = pd.read_excel(archivo_path)
        else:
            try:
                df = pd.read_csv(archivo_path, sep=';', encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(archivo_path, sep=';', encoding='latin1')
        # 3. Renombrar encabezados comunes
        mapeo = {
            'C�digo': 'codigo', 'Código': 'codigo', 'codigo': 'codigo',
            'Descripci�n': 'descripcion', 'Descripción': 'descripcion', 'descripcion': 'descripcion',
            'STOCK': 'stock', 'stock': 'stock', 'PEDIDOS': 'pedidos', 'pedidos': 'pedidos'
        }
        df = df.rename(columns=mapeo)
        # 4. Limpiar y normalizar
        df = limpiar_dataframe(df)
        df = agregar_columnas_faltantes(df)
        df = desglose_descripcion(df)
        # 5. Validar duplicados
        duplicados = df[df.duplicated('codigo', keep=False)]
        if not duplicados.empty:
            advertencia = f"Duplicados detectados en 'codigo': {duplicados['codigo'].tolist()}"
            resultado["advertencias"].append(advertencia)
            df = df.drop_duplicates('codigo', keep='first')
        # 6. Guardar archivo limpio
        limpio_path = os.path.join('inventario', 'inventario_perfiles_final_limpio.csv')
        df.to_csv(limpio_path, sep=';', index=False, encoding='utf-8')
        resultado["mensajes"].append(f"Archivo limpio generado: {limpio_path}")
        resultado["mensajes"].append(f"Total filas listas para importar: {len(df)}")
        # 7. Confirmar importación (callback UI o automático)
        if confirmar_importacion_callback:
            if not confirmar_importacion_callback(df, resultado):
                resultado["mensajes"].append("Importación cancelada por el usuario.")
                return resultado
        # 8. Backup antes de importar
        try:
            backup_tabla_sql()
            resultado["mensajes"].append("Backup de la tabla realizado correctamente.")
        except Exception as e:
            logger.error(f"Error en backup: {e}")
            resultado["advertencias"].append(f"No se pudo realizar backup: {e}")
        # 9. Importar a SQL
        try:
            importar_a_sql(df)
            resultado["exito"] = True
            resultado["mensajes"].append(f"Inventario importado correctamente ({len(df)} filas).")
            logger.info(f"Inventario importado por {usuario_actual}. Filas: {len(df)}")
        except Exception as e:
            logger.error(f"Error al importar inventario: {e}")
            resultado["errores"].append(f"Error al importar inventario: {e}")
    except PermisoDenegadoError as e:
        resultado["errores"].append(str(e))
    except Exception as e:
        logger.error(f"Error general en importación: {e}")
        resultado["errores"].append(f"Error general: {e}")
    return resultado

# --- INTEGRACIÓN CLI PARA TESTEO MANUAL ---
if __name__ == '__main__':
    print("\n--- IMPORTADOR DE INVENTARIO (solo admin) ---")
    class UsuarioDummy:
        es_admin = True
        def __str__(self):
            return "admin (dummy)"
    usuario_actual = UsuarioDummy()
    archivo = input("\nArrastra aquí el archivo CSV o Excel de inventario a procesar: ").strip('"')
    def confirmar(df, resultado):
        print(f"\nColumnas detectadas: {list(df.columns)}")
        if resultado["advertencias"]:
            print("\n⚠️  Advertencias:")
            for adv in resultado["advertencias"]:
                print(f"- {adv}")
        print(f"\nTotal filas listas para importar: {len(df)}")
        resp = input("\n¿Deseas importar estos datos a la base de datos? (s/n): ").strip().lower()
        return resp == 's'
    resultado = importar_inventario_desde_archivo(archivo, usuario_actual, confirmar_importacion_callback=confirmar)
    if resultado["exito"]:
        print("\n✅ Importación completada con éxito.")
    else:
        print("\n❌ La importación no se realizó.")
    for m in resultado["mensajes"]:
        print(m)
    for a in resultado["advertencias"]:
        print(f"Advertencia: {a}")
    for e in resultado["errores"]:
        print(f"Error: {e}")
