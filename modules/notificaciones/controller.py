from datetime import datetime

class NotificacionesController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_agregar.clicked.connect(self.agregar_notificacion)

    def agregar_notificacion(self):
        mensaje = self.view.mensaje_input.text()
        fecha = self.view.fecha_input.text()
        tipo = self.view.tipo_input.text()

        if mensaje and fecha and tipo:
            self.model.agregar_notificacion((mensaje, fecha, tipo))
            self.view.label.setText("Notificación agregada exitosamente.")
        else:
            self.view.label.setText("Por favor, complete todos los campos.")

    def enviar_notificacion_automatica(self, mensaje, tipo):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.model.agregar_notificacion((mensaje, fecha, tipo))
        self.view.label.setText(f"Notificación automática enviada: {mensaje}")
