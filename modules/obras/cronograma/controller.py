import datetime

class CronogramaController:
    def __init__(self, view, model=None):
        self.view = view
        self.model = model
        self.load_data()

    def load_data(self):
        # Simulación de datos si no hay modelo/DB
        obras = [
            {
                'id': 1,
                'nombre': 'Edificio Central',
                'cliente': 'Constructora Sur',
                'estado': 'Medición',
                'fecha': datetime.date(2025, 5, 1),
                'fecha_entrega': datetime.date(2025, 7, 30),
            },
            {
                'id': 2,
                'nombre': 'Torre Norte',
                'cliente': 'Río S.A.',
                'estado': 'Fabricación',
                'fecha': datetime.date(2025, 4, 10),
                'fecha_entrega': datetime.date(2025, 6, 10),
            },
            {
                'id': 3,
                'nombre': 'Residencial Sur',
                'cliente': 'Delta S.R.L.',
                'estado': 'Entrega',
                'fecha': datetime.date(2025, 3, 15),
                'fecha_entrega': datetime.date(2025, 5, 1),
            },
        ]
        self.view.set_obras(obras)
