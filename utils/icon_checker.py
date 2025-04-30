import os

def verificar_iconos():
    # Lista de íconos esperados
    iconos_esperados = {
        'dashboard', 'inventario', 'obras', 'produccion', 'logistica',
        'pedidos', 'usuarios', 'auditoria', 'configuracion', 'menu_white', 'sync'
    }

    # Ruta de la carpeta de íconos
    carpeta_iconos = os.path.join(os.path.dirname(__file__), '..', 'icons')
    
    # Listar archivos en la carpeta
    archivos_en_carpeta = {os.path.splitext(archivo)[0] for archivo in os.listdir(carpeta_iconos) if archivo.endswith('.svg')}

    # Verificar íconos presentes, faltantes y extra
    iconos_presentes = iconos_esperados & archivos_en_carpeta
    iconos_faltantes = iconos_esperados - archivos_en_carpeta
    iconos_extra = archivos_en_carpeta - iconos_esperados

    # Mostrar resultados
    print("Íconos presentes:")
    for icono in sorted(iconos_presentes):
        print(f"  - {icono}")

    print("\nÍconos faltantes:")
    for icono in sorted(iconos_faltantes):
        print(f"  - {icono}")

    print("\nÍconos extra no utilizados:")
    for icono in sorted(iconos_extra):
        print(f"  - {icono}")

if __name__ == "__main__":
    verificar_iconos()
