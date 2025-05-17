import datetime

class CronogramaController:
    def __init__(self, view, model=None):
        self.view = view
        self.model = model
        self.load_data()

    def load_data(self):
        try:
            if self.model:
                datos = self.model.obtener_datos_obras()
                obras = []
                for d in datos:
                    obra = dict(zip(self.model.obtener_headers_obras(), d))
                    obras.append(obra)
                self.view.set_obras(obras)
            # Si no hay modelo, no hace nada (la vista puede recibir set_obras desde afuera)
        except Exception as e:
            self.view.mostrar_error(f"Error al cargar datos del cronograma: {e}")

    def refrescar(self):
        """Permite refrescar los datos desde la vista."""
        self.load_data()

    def actualizar_obra(self, obra_id, nuevos_datos):
        """Actualiza una obra y recarga la vista."""
        try:
            if self.model:
                self.model.actualizar_obra(obra_id, nuevos_datos)
                self.load_data()
        except Exception as e:
            self.view.mostrar_error(f"Error al actualizar la obra: {e}")

    # Puedes agregar aquí otros métodos según necesidades futuras del módulo cronograma.