def guardar_permisos(self, id_rol, permisos):
        # Solo el admin puede modificar permisos de roles
        if not self.usuario_actual or self.usuario_actual.id_rol != 1:
            raise PermissionError("Solo el usuario admin puede modificar permisos de roles.")
        # ...código existente...
