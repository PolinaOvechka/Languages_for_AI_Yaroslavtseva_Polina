import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from desktop.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
    except FileNotFoundError:
        QMessageBox.critical(None, "Ошибка запуска", "Запустите train_models.py для создания файлов моделей")
        return 1

    window.show()
    return app.exec()
