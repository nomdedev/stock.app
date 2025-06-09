import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import pkg_resources

CRITICAL_PACKAGES = {
    "PyQt6": "6.9.0",  # Cambia aquí la versión mínima crítica si es necesario
    # Agrega otros paquetes críticos si lo deseas
}

def check_and_update_critical_packages():
    updates_needed = []
    for pkg, min_version in CRITICAL_PACKAGES.items():
        try:
            installed_version = pkg_resources.get_distribution(pkg).version
            if installed_version < min_version:
                updates_needed.append(pkg)
        except Exception:
            updates_needed.append(pkg)
    if updates_needed:
        app = QApplication.instance() or QApplication(sys.argv)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Actualización crítica requerida")
        msg.setText(f"Se requiere actualizar los siguientes paquetes críticos: {', '.join(updates_needed)}\nLa aplicación se actualizará automáticamente.")
        msg.show()
        app.processEvents()
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + updates_needed)
        msg.setText("Actualización completada. Por favor, reinicie la aplicación.")
        msg.exec()
        sys.exit(0)

# Lista de paquetes críticos a chequear
CRITICAL_PACKAGES_TO_CHECK = [
    "PyQt6",
    "matplotlib",
    "numpy",
    "qrcode",
    "pytest",
    "pytest-qt"
]

class UpdateCheckThread(QThread):
    updates_found = pyqtSignal(dict)
    def run(self):
        updates = {}
        for pkg in CRITICAL_PACKAGES_TO_CHECK:
            try:
                # pip index versions <package> --json (requiere pip>=23.2)
                result = subprocess.run([
                    sys.executable, "-m", "pip", "index", "versions", pkg, "--disable-pip-version-check"
                ], capture_output=True, text=True)
                lines = result.stdout.splitlines()
                if lines:
                    # Buscar la línea con "Available versions"
                    for line in lines:
                        if "Available versions:" in line:
                            available = line.split(":",1)[1].strip().split(", ")
                            current = pkg_resources.get_distribution(pkg).version
                            if available and available[0] != current:
                                updates[pkg] = {"current": current, "latest": available[0]}
            except Exception:
                pass
        self.updates_found.emit(updates)

class StartupUpdateChecker(QWidget):
    def __init__(self, on_continue):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(400, 220)
        # El estilo visual se gestiona por QSS de theme global, no usar setStyleSheet aquí
        layout = QVBoxLayout(self)
        self.label = QLabel("Cargando y verificando actualizaciones...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.btn_update = QPushButton("Actualizar ahora")
        self.btn_skip = QPushButton("Omitir e iniciar")
        self.btn_update.hide()
        self.btn_skip.hide()
        layout.addWidget(self.btn_update)
        layout.addWidget(self.btn_skip)
        self.btn_update.clicked.connect(self.update_packages)
        self.btn_skip.clicked.connect(lambda: self.finish(on_continue))
        self.updates = {}
        self.on_continue = on_continue
        self.check_thread = UpdateCheckThread()
        self.check_thread.updates_found.connect(self.on_updates_found)
        self.check_thread.start()

    def on_updates_found(self, updates):
        if updates:
            self.updates = updates
            msg = "Se encontraron actualizaciones:\n"
            for pkg, info in updates.items():
                msg += f"- {pkg}: {info['current']} → {info['latest']}\n"
            self.label.setText(msg)
            self.btn_update.show()
            self.btn_skip.show()
        else:
            self.label.setText("Todo actualizado. Iniciando...")
            QThread.msleep(1000)
            self.finish(self.on_continue)

    def update_packages(self):
        pkgs = [f"{pkg}=={info['latest']}" for pkg, info in self.updates.items()]
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + pkgs)
            QMessageBox.information(self, "Actualización", "Paquetes actualizados correctamente. Se recomienda reiniciar la app.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al actualizar: {e}")
        self.finish(self.on_continue)

    def finish(self, on_continue):
        self.close()
        on_continue()

# Ejemplo de uso:
if __name__ == "__main__":
    check_and_update_critical_packages()
    def continuar():
        QMessageBox.information(None, "Inicio", "¡App lista para usar!")
        app.quit()
    app = QApplication(sys.argv)
    splash = StartupUpdateChecker(continuar)
    splash.show()
    sys.exit(app.exec())
