class BaseController:
    """
    Clase base para controladores de módulo. Maneja la asignación de modelo y vista.
    """
    def __init__(self, model, view):
        self.model = model
        self.view = view
        # Se desconecta la llamada automática a setup_view_signals
        # para evitar que se ejecute antes de asignar la vista en Initializer
        # if hasattr(self, 'setup_view_signals'):
        #     self.setup_view_signals()