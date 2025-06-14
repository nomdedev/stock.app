# Instrucciones para inicializar todas las bases de datos de la app

## 1. Crear las bases de datos
Ejecuta el script:

```
scripts/db/00_create_databases.sql
```

Esto creará las bases:
- users
- inventario
- auditoria

## 2. Crear las tablas en cada base
Conéctate a cada base y ejecuta el script correspondiente:

- **users**: `users.sql`
- **inventario**: `inventario.sql`
- **auditoria**: `auditoria.sql`

## 3. Insertar datos de ejemplo
Ejecuta el script:

```
scripts/db/insert_ejemplos_obras_flujo_completo.sql
```

Esto poblará las tablas principales con datos de ejemplo para pruebas y flujo completo.

---

**Notas:**
- Todos los scripts son idempotentes: puedes ejecutarlos varias veces sin error.
- Si necesitas limpiar la base, simplemente vuelve a ejecutar los scripts de estructura.
- Si agregas nuevas tablas, crea un script separado y agrégalo aquí.
