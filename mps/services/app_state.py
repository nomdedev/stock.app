from mps.controllers.auditoria_controller import AuditoriaController

class AppState:
    db_online = False
    conexiones = {}
    observadores = []  # Lista de observadores registrados

    @staticmethod
    def set_db_status(base, status: bool, usuario=None):
        """Actualiza el estado de conexión de una base específica."""
        previo_estado = AppState.conexiones.get(base, False)
        AppState.conexiones[base] = status
        AppState.db_online = any(AppState.conexiones.values())
        AppState.notificar_estado_actualizado(base, status)
        if status and not previo_estado and usuario:
            AuditoriaController.registrar_reconexion(base, usuario)
        if base == "auditorias" and status and not previo_estado:
            AuditoriaController.sincronizar_auditorias_pendientes()

    @staticmethod
    def notificar_estado_actualizado(base, status):
        """Notifica a todos los observadores sobre el cambio de estado."""
        for observador in AppState.observadores:
            observador(base, status)

    @staticmethod
    def registrar_observador_conexion(func):
        """Registra una función como observador de cambios en el estado de conexión."""
        if func not in AppState.observadores:
            AppState.observadores.append(func)

    @staticmethod
    def is_connected(base):
        """Devuelve True/False según el estado actual de la base."""
        return AppState.conexiones.get(base, False)

    @staticmethod
    def reset():
        """Limpia todas las conexiones y marca db_online=False."""
        AppState.conexiones.clear()
        AppState.db_online = False
