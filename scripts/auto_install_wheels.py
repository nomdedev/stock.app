import sys
import os
import platform
import subprocess
import urllib.request
import glob

# --- DETECTAR VERSIÓN DE PYTHON Y ARQUITECTURA ---
py_version = f"{sys.version_info.major}{sys.version_info.minor}"  # Ej: 311 para Python 3.11
arch = platform.architecture()[0]
py_tag = f"cp{py_version}"  # Ej: cp311
win_tag = "win_amd64" if arch == "64bit" else "win32"

# --- PAQUETES CRÍTICOS A INSTALAR DESDE WHEEL SI FALLA LA INSTALACIÓN NORMAL ---
wheels = {
    "pandas": f"pandas-2.2.2-{py_tag}-{py_tag}-{win_tag}.whl",
    "pyodbc": f"pyodbc-5.0.1-{py_tag}-{py_tag}-{win_tag}.whl"
}

# --- URL BASE DE WHEELS DE GOHLKE ---
url_base = "https://download.lfd.uci.edu/pythonlibs/archive/"

# --- DESCARGAR E INSTALAR WHEELS SI NO ESTÁN INSTALADOS ---
def instalar_wheel(paquete, wheel_file):
    print(f"Descargando e instalando wheel para {paquete}...")
    url = url_base + wheel_file
    local_path = os.path.join(os.getcwd(), wheel_file)
    try:
        urllib.request.urlretrieve(url, local_path)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", local_path])
        print(f"✅ {paquete} instalado desde wheel.")
        os.remove(local_path)
    except Exception as e:
        print(f"❌ Error instalando {paquete} desde wheel: {e}")
        return False
    return True

# --- INTENTAR INSTALACIÓN NORMAL, SI FALLA USAR WHEEL ---
def instalar_dependencia(paquete, version):
    try:
        if version:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", f"{paquete}=={version}", "--prefer-binary"])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", paquete, "--prefer-binary"])
        print(f"✅ {paquete} instalado normalmente.")
        return True
    except Exception:
        # Intentar con wheel si está en la lista
        if paquete in wheels:
            return instalar_wheel(paquete, wheels[paquete])
        return False

# --- INSTALAR PAQUETES CRÍTICOS ---
requeridos = [
    ("pandas", "2.2.2"), ("pyodbc", "5.0.1")
]
for paquete, version in requeridos:
    instalar_dependencia(paquete, version)

# --- INSTALAR EL RESTO DE REQUIREMENTS.TXT ---
print("Instalando el resto de dependencias desde requirements.txt...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--prefer-binary", "-r", "requirements.txt"])
    print("✅ Todas las dependencias instaladas correctamente.")
except Exception as e:
    print(f"❌ Error instalando requirements.txt: {e}")
    print("Por favor, revisa los logs y ejecuta manualmente si es necesario.")

print("Listo. Puedes iniciar la aplicación normalmente.")
