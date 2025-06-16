import subprocess
import sys

def install_dependencies():
    print("Actualizando herramientas de construcción...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel"])

    print("Instalando dependencias desde requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Error durante la instalación: {e}")

    print("Instalando pillow desde binarios precompilados...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "--only-binary=:all:"])
    except subprocess.CalledProcessError as e:
        print(f"Error durante la instalación de pillow: {e}")

if __name__ == "__main__":
    install_dependencies()
