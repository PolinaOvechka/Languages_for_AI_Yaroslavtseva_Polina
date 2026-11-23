import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from config import DATA_PATH, MODEL_DIR, MODELS


def main():
    data = np.loadtxt(DATA_PATH, delimiter=",", skiprows=1)

    # В последнем столбце записан класс, остальные столбцы это признаки
    X = data[:, :-1]
    y = data[:, -1].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    classifiers = {
        "Логистическая регрессия": LogisticRegression(),
        "MLP": MLPClassifier(
            hidden_layer_sizes=(64, 32), max_iter=3000, random_state=42
        ),
    }

    MODEL_DIR.mkdir(exist_ok=True)
    for name, classifier in classifiers.items():
        # Масштабирование настраивается только по обучающей выборке
        model = make_pipeline(StandardScaler(), classifier)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        print(f"{name}: accuracy = {accuracy_score(y_test, predictions):.4f}, "
              f"F1 = {f1_score(y_test, predictions):.4f}")
        joblib.dump(model, MODELS[name], compress=3)


if __name__ == "__main__":
    main()
