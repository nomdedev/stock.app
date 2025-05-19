import importlib

def test_dependencias():
    deps = [
        "PyQt6", "pyodbc", "reportlab", "qrcode", "pandas", "matplotlib", "pytest",
        "pillow", "python_dateutil", "pytz", "tzdata", "openpyxl", "colorama", "ttkthemes"
    ]
    faltantes = []
    for dep in deps:
        try:
            importlib.import_module(dep.replace('-', '_'))
        except ImportError:
            faltantes.append(dep)
    if faltantes:
        print(f"❌ Faltan dependencias: {', '.join(faltantes)}")
        return False
    print("✅ Todas las dependencias críticas y de desarrollo están instaladas correctamente.")
    return True

if __name__ == "__main__":
    test_dependencias()
