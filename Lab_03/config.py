from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "credit.csv"
MODEL_DIR = ROOT / "models"

MODELS = {
    "Логистическая регрессия": MODEL_DIR / "logistic.joblib",
    "MLP": MODEL_DIR / "mlp.joblib",
}

