# Errores frecuentes, advertencias y buenas prácticas en login, tests y seguridad

## 1. Ejecución de tests y estructura de imports

- **Error:** `ModuleNotFoundError: No module named 'modules'`

- **Causa:** Ejecutar un test directamente con `python tests/test_login.py` en vez de usar el flag `-m`.

- **Solución:** Ejecutar siempre los tests con:

  ```sh
  python -m tests.test_login
  ```

  Esto asegura que Python trate `tests` como un paquete y resuelva correctamente los imports relativos.

## 2. Tablas auxiliares de permisos

- **Error:** `El nombre de objeto 'permisos_modulos' no es válido.`

- **Causa:** Falta la tabla auxiliar de permisos en la base de datos.

- **Solución:** Documentar y crear siempre la tabla `permisos_modulos` junto con la tabla `usuarios` en instalaciones nuevas. Incluir el SQL de creación en la documentación.

  ```sql
  CREATE TABLE permisos_modulos (
      id INT IDENTITY(1,1) PRIMARY KEY,
      id_usuario INT NOT NULL,
      modulo NVARCHAR(64) NOT NULL,
      puede_ver BIT NOT NULL DEFAULT 0,
      puede_modificar BIT NOT NULL DEFAULT 0,
      puede_aprobar BIT NOT NULL DEFAULT 0,
      creado_por INT,
      fecha_creacion DATETIME DEFAULT GETDATE()
  );
  ```

## 3. Tests de login fallan con NoneType

- **Error:** `El objeto de tipo "None" no se puede suscribir`

- **Causa:** El usuario no se autenticó y el test intenta acceder a campos de un objeto `None`.

- **Solución:** Siempre usar `assertIsNotNone(user, mensaje)` antes de acceder a los campos del usuario en los tests.

## 4. Inicialización de QApplication en tests PyQt

- **Error:** `QApplication instance already exists` o errores de entorno gráfico.

- **Solución:** En los tests, usar:

  ```python
  app = QApplication.instance() or QApplication(sys.argv)
  ```

  antes de crear cualquier widget.

## 5. Creación de tablas en tests automáticos

- **Recomendación:** En el método `setUp` de los tests, crear las tablas auxiliares necesarias si no existen, para que los tests sean robustos y no dependan del estado previo de la base de datos.

## 6. Consistencia de claves en diccionarios de usuario

- **Error:** `KeyError: 'username'`

- **Causa:** El modelo devuelve la clave `'usuario'`, pero el código espera `'username'`.

- **Solución:** Unificar siempre el uso de claves (`usuario` o `username`) en todo el proyecto y documentar la convención.

## 7. Advertencia de box-shadow en QSS

- **Error:** `Unknown property box-shadow` o warning similar en consola.

- **Causa:** Qt no soporta la propiedad CSS `box-shadow` en QSS.

- **Solución:** Eliminar cualquier referencia a `box-shadow` en los archivos QSS. Usar `QGraphicsDropShadowEffect` en Python para sombras visuales.

## 8. Seguridad: información confidencial y control de código

- **Nunca subir a GitHub:**

  - Archivos de tests automáticos que incluyan usuarios, contraseñas, o lógica de autenticación.
  - Archivos de configuración con credenciales, rutas de base de datos, o claves API.
  - Dumps de base de datos o archivos con datos reales de usuarios.

- **Recomendación:**

  - Agregar los archivos de tests y configuración sensible a `.gitignore`.
  - Documentar en el README y en este archivo que los tests de login y archivos de configuración nunca deben subirse a repositorios públicos.

## 9. Otras buenas prácticas y advertencias

- Centralizar estilos visuales en QSS global o helpers, nunca hardcodear en cada widget.
- Documentar cualquier excepción visual o lógica en los archivos de estándares (`docs/estandares_visuales.md`, `docs/estandares_seguridad.md`).
- Usar helpers para feedback visual y accesibilidad en todos los módulos.
- Validar siempre el feedback visual y de error en producción y documentar cualquier excepción.

---

**Actualizado:** 25/05/2025
