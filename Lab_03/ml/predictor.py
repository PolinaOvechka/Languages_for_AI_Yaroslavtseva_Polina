import joblib
import numpy as np


class Predictor:
    def __init__(self, path):
        self.model = joblib.load(path)

    def predict(self, features):
        expected = self.model.n_features_in_
        if len(features) != expected:
            raise ValueError(f"Нужно ввести {expected} признаков, введено {len(features)}")

        sample = np.array([features], dtype=float)
        prediction = self.model.predict(sample)[0]
        result = {"prediction": prediction.item()}

        # Берём вероятность того класса, который выбрала модель
        if hasattr(self.model, "predict_proba"):
            class_index = list(self.model.classes_).index(prediction)
            result["proba"] = float(self.model.predict_proba(sample)[0, class_index])

        return result
