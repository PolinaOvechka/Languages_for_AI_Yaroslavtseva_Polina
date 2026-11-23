"""Обучение модели и прогноз прочности бетона"""

from math import isfinite
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor


DATA_FILE = Path(__file__).with_name("concrete_strength.csv")
FEATURES = [
    "cement", "slag", "fly_ash", "water", "superplasticizer",
    "coarse_aggregate", "fine_aggregate", "age",
]


def load_data():
    """Читает данные и удаляет полные дубликаты"""
    return pd.read_csv(DATA_FILE).drop_duplicates()


def train_model(data=None):
    """Обучает случайный лес на данных"""
    if data is None:
        data = load_data()

    # Используем настройки случайного леса из ноутбука
    model = RandomForestRegressor(n_estimators=150, min_samples_leaf=2, random_state=42)
    model.fit(data[FEATURES], data["strength_mpa"])
    return model


def predict_strength(model, recipe):
    """Принимает словарь с дозировками и возрастом и возвращает прогноз в МПа"""
    values = {}
    for name in FEATURES:
        if name not in recipe:
            raise ValueError(f"Нет значения для поля «{name}»")

        try:
            number = float(recipe[name])
        except (TypeError, ValueError, OverflowError):
            raise ValueError(f"В поле «{name}» должно быть число") from None

        if not isfinite(number) or number < 0:
            raise ValueError(f"В поле «{name}» нужно указать конечное число от нуля")
        values[name] = number

    age = values["age"]
    if age < 1 or not age.is_integer():
        raise ValueError("Возраст бетона должен быть целым числом от 1 дня")

    # Передаём значения модели в том же порядке, что при обучении
    row = pd.DataFrame([values], columns=FEATURES)
    return float(model.predict(row)[0])
