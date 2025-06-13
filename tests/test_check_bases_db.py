import pytest
import pyodbc

# Configuración de conexión general (ajustar según entorno real)
CONN_STR = "DRIVER={SQL Server};SERVER=localhost;Trusted_Connection=yes;"

# Bases de datos que deben existir
BASES_REQUERIDAS = {'inventario', 'users', 'auditoria'}

def obtener_bases_de_datos():
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.databases")
    bases = set(row[0] for row in cursor.fetchall())
    conn.close()
    return bases

def test_bases_de_datos_existentes():
    bases = obtener_bases_de_datos()
    faltantes = BASES_REQUERIDAS - bases
    extras = bases - BASES_REQUERIDAS
    print(f"Bases de datos encontradas: {bases}")
    if faltantes:
        print(f"Faltan bases requeridas: {faltantes}")
    if extras:
        print(f"Bases de datos adicionales detectadas: {extras}")
    assert not faltantes, f"Faltan bases requeridas: {faltantes}"

# El resto del test de tablas y columnas debe adaptarse para usar solo estas bases
# ...existing code...
