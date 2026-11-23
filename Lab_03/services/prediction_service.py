from math import isfinite


class PredictionService:
    def __init__(self, predictor):
        self.predictor = predictor

    def run(self, text, on_probability=None):
        if not text.strip():
            raise ValueError("Введите признаки через запятую")

        try:
            features = [float(value.strip()) for value in text.split(",")]
        except ValueError:
            raise ValueError("Введите числа через запятую, дробную часть отделяйте точкой") from None

        if not all(isfinite(value) for value in features):
            raise ValueError("Все признаки должны быть конечными числами")

        result = self.predictor.predict(features)
        if on_probability is not None and "proba" in result:
            on_probability(result["proba"])

        if result["prediction"] == 1:
            return "Прогноз модели: дефолт"
        return "Прогноз модели: возврат кредита"
