from PySide6.QtCore import QThread, Signal


class PredictWorker(QThread):
    finished_ok = Signal(str)
    failed = Signal(str)
    probability_ready = Signal(float)

    def __init__(self, service, text, parent=None):
        super().__init__(parent)
        self.service = service
        self.text = text

    def run(self):
        # Здесь выполняется расчёт в отдельном потоке
        try:
            result = self.service.run(self.text, self.probability_ready.emit)
        except Exception as error:
            self.failed.emit(str(error))
        else:
            self.finished_ok.emit(result)
