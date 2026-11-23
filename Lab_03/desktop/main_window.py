from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
)

from config import MODELS
from desktop.worker import PredictWorker
from ml.predictor import Predictor
from services.prediction_service import PredictionService


class WindowLoader(QUiLoader):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def createWidget(self, class_name, parent=None, name=""):
        if parent is None and class_name == "QMainWindow":
            self.window.setObjectName(name)
            return self.window
        return super().createWidget(class_name, parent, name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загружаем форму, сохранённую в Qt Designer
        ui_path = Path(__file__).with_name("credit_window.ui")
        loader = WindowLoader(self)
        loader.load(str(ui_path))

        self.model_box = self.findChild(QComboBox, "comboBox")
        self.feature_input = self.findChild(QLineEdit, "lineEdit")
        self.predict_button = self.findChild(QPushButton, "pushButton")
        self.clear_button = self.findChild(QPushButton, "pushButton_2")
        self.result_label = self.findChild(QLabel, "label_4")
        self.result_placeholder = self.result_label.text()
        self.probability = self.findChild(QProgressBar, "progressBar")
        self.probability.reset()

        self.predictors = {name: Predictor(path) for name, path in MODELS.items()}
        self.service = PredictionService(self.predictors[self.model_box.currentText()])
        self.worker = None

        self.predict_button.clicked.connect(self.on_predict_clicked)
        self.clear_button.clicked.connect(self.on_clear_clicked)
        self.feature_input.returnPressed.connect(self.on_predict_clicked)
        self.feature_input.textEdited.connect(self.reset_result)
        self.model_box.currentIndexChanged.connect(self.on_model_changed)

    @Slot()
    def on_predict_clicked(self):
        if self.worker is not None:
            return

        self.set_busy(True)
        self.result_label.setText("Вычисление…")
        self.probability.reset()

        self.worker = PredictWorker(self.service, self.feature_input.text(), self)
        self.worker.finished_ok.connect(self.on_success)
        self.worker.failed.connect(self.on_error)
        self.worker.probability_ready.connect(self.on_probability)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    @Slot()
    def on_clear_clicked(self):
        self.feature_input.clear()
        self.feature_input.setFocus()
        self.reset_result()

    @Slot(int)
    def on_model_changed(self, index):
        self.service.predictor = self.predictors[self.model_box.itemText(index)]
        self.reset_result()

    @Slot()
    def reset_result(self):
        self.result_label.setText(self.result_placeholder)
        self.probability.reset()

    def set_busy(self, busy):
        self.feature_input.setReadOnly(busy)
        self.predict_button.setEnabled(not busy)
        self.clear_button.setEnabled(not busy)
        self.model_box.setEnabled(not busy)

    @Slot(str)
    def on_success(self, text):
        self.result_label.setText(text)

    @Slot(str)
    def on_error(self, text):
        self.result_label.setText(f"Ошибка: {text}")

    @Slot(float)
    def on_probability(self, probability):
        self.probability.setValue(round(probability * 100))

    @Slot()
    def on_worker_finished(self):
        self.worker.deleteLater()
        self.worker = None
        self.set_busy(False)

    def closeEvent(self, event):
        # Даём потоку закончить работу перед закрытием окна
        if self.worker is not None:
            event.ignore()
            return
        super().closeEvent(event)
