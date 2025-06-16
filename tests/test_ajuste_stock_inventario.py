import pytest
import pyodbc
import os
from dotenv import load_dotenv

"""
Test de ajuste de stock y registro de movimientos en inventario.

DIFERENCIACIÓN CLAVE ENTRE PERFILES Y OTROS PRODUCTOS:
- En el sistema existen dos grandes tipos de productos:
  1. **Perfiles** (PVC o aluminio):
     - Se almacenan en la tabla `inventario_perfiles`.
     - Los movimientos de stock se registran en la tabla `movimientos_stock`, usando la columna `id_perfil` como referencia.
  2. **Otros productos** (herrajes, insumos, etc.):
     - Se almacenan en la tabla `inventario_items`.
     - Los movimientos de stock se deben registrar en una tabla específica (por ejemplo, `movimientos_stock_items`), usando la columna `id_item` como referencia.

IMPORTANTE:
- Los tests deben reflejar esta lógica: si el test es para un perfil, debe operar sobre `inventario_perfiles` y `movimientos_stock` (`id_perfil`).
- Si el test es para un producto genérico, debe operar sobre `inventario_items` y la tabla de movimientos correspondiente (`id_item`).
- Si en el futuro se agregan más tipos de productos, se debe documentar y testear su lógica de stock y movimientos.

Objetivo del test:
- Verificar que al ajustar el stock de un ítem o perfil, el valor se actualiza correctamente en la base de datos.
- Registrar el movimiento en la tabla de movimientos correspondiente.
- Probar tanto sumas como restas de stock.
- Edge cases: stock negativo, ajuste cero, usuario inexistente.

Pasos:
1. Conectar a la base de datos usando los datos del .env.
2. Crear las tablas necesarias si no existen.
3. Insertar ítems/perfiles de prueba si no existen.
4. Obtener el stock actual antes del ajuste.
5. Realizar el ajuste de stock y registrar el movimiento.
6. Verificar que el stock se ajustó correctamente.
7. Verificar que el movimiento fue registrado.
8. (Edge case sugerido) Intentar ajuste que deje el stock negativo y verificar el comportamiento.
"""

load_dotenv()

DB = 'inventario'

# La siguiente función de test verifica solo la lógica de ajuste de stock y registro de movimientos
# mediante conexión directa a la base de datos. No prueba lógica de negocio de la aplicación ni API.
@pytest.mark.parametrize("tipo, item_id, ajuste, usuario", [
    ("perfil", 1, 5, 'admin'),   # Suma 5 al stock del perfil 1
    ("item", 2, -3, 'admin'),   # Resta 3 al stock del item 2
    ("perfil", 1, -20, 'admin'), # Edge case: stock negativo en perfil
    ("item", 2, 0, 'admin'),   # Edge case: ajuste cero en item
    ("perfil", 1, 2, 'usuario_inexistente'), # Edge case: usuario no válido en perfil
])
def test_ajuste_stock_y_movimiento(tipo, item_id, ajuste, usuario):
    """
    Ajusta el stock de un perfil o item y registra el movimiento en la tabla correspondiente.
    - Si tipo == 'perfil': opera sobre inventario_perfiles y movimientos_stock (id_perfil)
    - Si tipo == 'item': opera sobre inventario_items y movimientos_stock_items (id_item)
    """
    driver = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.environ.get("DB_SERVER")
    database = os.environ.get("DB_DEFAULT_DATABASE", "inventario")
    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")
    timeout = os.environ.get("DB_TIMEOUT", "5")
    assert server and username and password, "Faltan variables de entorno para la conexión a la base de datos"
    conn_str = (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Timeout={timeout};"
    )
    try:
        conn = pyodbc.connect(conn_str)
    except pyodbc.InterfaceError as e:
        raise RuntimeError(f"Error de conexión a la base de datos: {e}. Verifica las variables de entorno y los datos de conexión.") from e
    cursor = conn.cursor()
    # Crear tablas si no existen
    if tipo == "perfil":
        cursor.execute("""
            IF OBJECT_ID('inventario_perfiles', 'U') IS NULL
            CREATE TABLE inventario_perfiles (
                id INT PRIMARY KEY,
                stock_actual INT NOT NULL
            )
        """)
        cursor.execute("""
            IF OBJECT_ID('movimientos_stock', 'U') IS NULL
            CREATE TABLE movimientos_stock (
                id INT IDENTITY(1,1) PRIMARY KEY,
                id_perfil INT NOT NULL,
                fecha DATETIME NOT NULL,
                tipo_movimiento NVARCHAR(50) NOT NULL,
                cantidad DECIMAL(18,2) NOT NULL,
                usuario NVARCHAR(200) NOT NULL,
                referencia NVARCHAR(510),
                detalle NVARCHAR(510)
            )
        """)
        # Insertar perfil de prueba si no existe
        cursor.execute("IF NOT EXISTS (SELECT 1 FROM inventario_perfiles WHERE id = ?) INSERT INTO inventario_perfiles (id, stock_actual) VALUES (?, 10)", (item_id, item_id))
        conn.commit()
        # Obtener stock actual antes
        cursor.execute("SELECT stock_actual FROM inventario_perfiles WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        stock_antes = row[0] if row else 0
        # Realizar ajuste
        nuevo_stock = stock_antes + ajuste
        cursor.execute("UPDATE inventario_perfiles SET stock_actual = ? WHERE id = ?", (nuevo_stock, item_id))
        # Registrar movimiento
        cursor.execute("""
            INSERT INTO movimientos_stock (id_perfil, fecha, tipo_movimiento, cantidad, usuario, referencia, detalle)
            VALUES (?, GETDATE(), ?, ?, ?, ?, ?)
        """, (item_id, 'ajuste', ajuste, usuario, f"Ajuste de test: {ajuste}", None))
        conn.commit()
        # Verificar stock final
        cursor.execute("SELECT stock_actual FROM inventario_perfiles WHERE id = ?", (item_id,))
        result = cursor.fetchone()
        assert result is not None, f"El perfil {item_id} no existe tras el ajuste."
        stock_despues = result[0]
        assert stock_despues == nuevo_stock, f"El stock final ({stock_despues}) no coincide con el esperado ({nuevo_stock})"
        # Verificar movimiento registrado
        cursor.execute("SELECT TOP 1 cantidad, usuario FROM movimientos_stock WHERE id_perfil = ? ORDER BY id DESC", (item_id,))
        mov = cursor.fetchone()
        assert mov and float(mov[0]) == float(ajuste) and mov[1] == usuario, "El movimiento no fue registrado correctamente"
    else:  # tipo == "item"
        cursor.execute("""
            IF OBJECT_ID('inventario_items', 'U') IS NULL
            CREATE TABLE inventario_items (
                id INT PRIMARY KEY,
                stock_actual INT NOT NULL
            )
        """)
        cursor.execute("""
            IF OBJECT_ID('movimientos_stock_items', 'U') IS NULL
            CREATE TABLE movimientos_stock_items (
                id INT IDENTITY(1,1) PRIMARY KEY,
                id_item INT NOT NULL,
                fecha DATETIME NOT NULL,
                tipo_movimiento NVARCHAR(50) NOT NULL,
                cantidad DECIMAL(18,2) NOT NULL,
                usuario NVARCHAR(200) NOT NULL,
                referencia NVARCHAR(510),
                detalle NVARCHAR(510)
            )
        """)
        # Insertar item de prueba si no existe
        cursor.execute("IF NOT EXISTS (SELECT 1 FROM inventario_items WHERE id = ?) INSERT INTO inventario_items (id, stock_actual) VALUES (?, 10)", (item_id, item_id))
        conn.commit()
        # Obtener stock actual antes
        cursor.execute("SELECT stock_actual FROM inventario_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        stock_antes = row[0] if row else 0
        # Realizar ajuste
        nuevo_stock = stock_antes + ajuste
        cursor.execute("UPDATE inventario_items SET stock_actual = ? WHERE id = ?", (nuevo_stock, item_id))
        # Registrar movimiento
        cursor.execute("""
            INSERT INTO movimientos_stock_items (id_item, fecha, tipo_movimiento, cantidad, usuario, referencia, detalle)
            VALUES (?, GETDATE(), ?, ?, ?, ?, ?)
        """, (item_id, 'ajuste', ajuste, usuario, f"Ajuste de test: {ajuste}", None))
        conn.commit()
        # Verificar stock final
        cursor.execute("SELECT stock_actual FROM inventario_items WHERE id = ?", (item_id,))
        result = cursor.fetchone()
        assert result is not None, f"El item {item_id} no existe tras el ajuste."
        stock_despues = result[0]
        assert stock_despues == nuevo_stock, f"El stock final ({stock_despues}) no coincide con el esperado ({nuevo_stock})"
        # Verificar movimiento registrado
        cursor.execute("SELECT TOP 1 cantidad, usuario FROM movimientos_stock_items WHERE id_item = ? ORDER BY id DESC", (item_id,))
        mov = cursor.fetchone()
        assert mov and float(mov[0]) == float(ajuste) and mov[1] == usuario, "El movimiento no fue registrado correctamente"
    # Edge cases y cierre
    if ajuste < 0 and abs(ajuste) > stock_antes:
        print(f"Advertencia: El ajuste deja el stock negativo para {tipo} {item_id}")
    if usuario == 'usuario_inexistente':
        print("Advertencia: El usuario no existe en la base de datos (simulado)")
    if ajuste == 0:
        print("Advertencia: El ajuste es cero, no debería modificar el stock")
    conn.close()
