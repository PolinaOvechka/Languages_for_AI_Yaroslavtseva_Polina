import sys
from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMessageBox

from concrete_model import FEATURES, load_data, predict_strength, train_model


def main():
    # обработка нажатий и действий в окне
    app = QApplication(sys.argv)

    ui_path = Path(__file__).with_name("concrete_window.ui")
    loader = QUiLoader()
    try:
        window = loader.load(str(ui_path))
    except RuntimeError as error:
        print(f"Не удалось открыть форму {ui_path.name}", file=sys.stderr)
        print(error, file=sys.stderr)
        return 1

    # Обучаем модель один раз при запуске окна
    try:
        data = load_data()
        model = train_model(data)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        QMessageBox.critical(window, "Ошибка обучения", "Проверьте файл concrete_strength.csv")
        return 1

    fields = {name: getattr(window, name) for name in FEATURES}
    output = window.predictionOutput
    locale = window.locale()

    # Подсказки берём из тех же данных, на которых обучили модель
    dose_ranges = {}
    for name, field in fields.items():
        if name == "age":
            continue
        low = float(data[name].min())
        high = float(data[name].max())
        dose_ranges[name] = (low, high)
        low_text = locale.toString(low, "f", 2)
        high_text = locale.toString(high, "f", 2)
        hint = f"{field.accessibleName()}, от {low_text} до {high_text}{field.suffix()} в обучающих данных"
        field.setToolTip(hint)
        field.lineEdit().setToolTip(hint)
        getattr(window, name + "Label").setToolTip(hint)

    def calculate():
        # Собираем значения из формы по именам полей
        recipe = {name: field.value() for name, field in fields.items()}
        if not any(recipe[name] for name in dose_ranges):
            QMessageBox.warning(window, "Проверьте ввод", "Введите дозировки компонентов смеси")
            return

        try:
            strength = predict_strength(model, recipe)
        except ValueError as error:
            QMessageBox.warning(window, "Проверьте ввод", str(error))
            return

        output.setText(locale.toString(strength, "f", 2))
        outside = [
            fields[name].toolTip()
            for name, (low, high) in dose_ranges.items()
            if not low <= recipe[name] <= high
        ]
        if outside:
            QMessageBox.warning(
                window,
                "Дозировки вне диапазона",
                "Точность прогноза для таких дозировок может быть ниже\n\n" + "\n".join(outside),
            )

    # При изменении состава убираем предыдущий прогноз
    for field in fields.values():
        field.valueChanged.connect(output.clear)

    window.calculateButton.clicked.connect(calculate)

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
