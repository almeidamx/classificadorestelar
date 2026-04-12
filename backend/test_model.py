import pickle
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from backend.app import app

BASE_DIR = Path(__file__).resolve().parent


DATASET_URL = (
    "https://raw.githubusercontent.com/almeidamx/start-classification/"
    "refs/heads/main/star_classification.csv"
)

FEATURES = ["alpha", "delta", "u", "g", "r", "i", "z", "redshift"]

COLUNAS_REMOVER = [
    "obj_ID", "run_ID", "rerun_ID", "cam_col",
    "field_ID", "spec_obj_ID", "plate", "MJD", "fiber_ID",
]

# Carregar modelo (pipeline com StandardScaler embutido)
with open(BASE_DIR / "modelo.pkl", "rb") as f:
    modelo = pickle.load(f)

# Carregar dataset e reproduzir o mesmo pré-processamento do notebook
df = pd.read_csv(DATASET_URL)
df = df.drop(columns=COLUNAS_REMOVER)

X = df[FEATURES]
y = df["class"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

y_pred = modelo.predict(X_test)


# ===========================================================================
# TESTES DE MÉTRICAS DO MODELO
# ===========================================================================

def test_acuracia():
    acc = accuracy_score(y_test, y_pred)
    assert acc >= 0.95, f"Acurácia {acc:.4f} abaixo do mínimo exigido de 0.95"


def test_f1_macro():
    f1 = f1_score(y_test, y_pred, average="macro")
    assert f1 >= 0.94, f"F1-Score macro {f1:.4f} abaixo do mínimo exigido de 0.94"


def test_recall_por_classe():
    classes = ["STAR", "GALAXY", "QSO"]
    recall = recall_score(y_test, y_pred, average=None, labels=classes)
    for i, classe in enumerate(classes):
        assert recall[i] >= 0.90, (
            f"Recall da classe '{classe}' = {recall[i]:.4f} "
            f"abaixo do mínimo exigido de 0.90"
        )


# ===========================================================================
# TESTES DE INTEGRIDADE DO MODELO
# ===========================================================================

def test_modelo_carregamento():
    assert modelo is not None, "Modelo não carregado"
    assert hasattr(modelo, "predict"), "Modelo não possui método predict"


def test_pipeline_contem_scaler():
    steps = dict(modelo.steps)
    assert "scaler" in steps, "Pipeline não contém etapa 'scaler'"
    assert isinstance(steps["scaler"], StandardScaler), (
        "Etapa 'scaler' não é um StandardScaler"
    )


def test_dataset_estrutura():
    for col in FEATURES:
        assert col in df.columns, f"Coluna '{col}' não encontrada no dataset"
    assert "class" in df.columns, "Coluna alvo 'class' não encontrada"
    assert set(y.unique()) == {"STAR", "GALAXY", "QSO"}, (
        "Classes inesperadas no dataset"
    )


# ===========================================================================
# TESTES DE API FLASK
# ===========================================================================

@pytest.fixture(name="client")
def flask_client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def _valid_payload():
    return {
        "alpha":    135.689157,
        "delta":    32.494632,
        "u":        23.87882,
        "g":        22.27530,
        "r":        20.39501,
        "i":        19.16573,
        "z":        18.79371,
        "redshift": 0.6347,
    }


def test_api_home(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/docs"


def test_api_predict_sucesso(client):
    response = client.post("/predict", json=_valid_payload())
    assert response.status_code == 200
    result = response.get_json()
    assert "prediction" in result
    assert result["prediction"] in ["STAR", "GALAXY", "QSO"]


def test_api_predict_campo_faltando(client):
    data = _valid_payload()
    del data["redshift"]
    response = client.post("/predict", json=data)
    assert response.status_code == 400
    assert "redshift" in response.get_json()["error"]


def test_api_predict_alpha_invalido(client):
    data = _valid_payload()
    data["alpha"] = 999.0
    response = client.post("/predict", json=data)
    assert response.status_code == 400
    assert "alpha" in response.get_json()["error"]


def test_api_predict_delta_invalido(client):
    data = _valid_payload()
    data["delta"] = -100.0
    response = client.post("/predict", json=data)
    assert response.status_code == 400
    assert "delta" in response.get_json()["error"]


def test_api_predict_redshift_invalido(client):
    data = _valid_payload()
    data["redshift"] = -5.0
    response = client.post("/predict", json=data)
    assert response.status_code == 400
    assert "redshift" in response.get_json()["error"]


def test_api_predict_tipo_invalido(client):
    data = _valid_payload()
    data["u"] = "vinte e três"
    response = client.post("/predict", json=data)
    assert response.status_code == 400


def test_api_predict_sem_json(client):
    response = client.post(
        "/predict", data="not json", content_type="text/plain"
    )
    assert response.status_code == 400


def test_api_predict_valores_minimos(client):
    data = {
        "alpha":    0.0,
        "delta":    -90.0,
        "u":        -10.0,
        "g":        -10.0,
        "r":        -10.0,
        "i":        -10.0,
        "z":        -10.0,
        "redshift": -0.05,
    }
    response = client.post("/predict", json=data)
    assert response.status_code == 200


def test_api_predict_valores_maximos(client):
    data = {
        "alpha":    360.0,
        "delta":    90.0,
        "u":        35.0,
        "g":        35.0,
        "r":        35.0,
        "i":        35.0,
        "z":        35.0,
        "redshift": 10.0,
    }
    response = client.post("/predict", json=data)
    assert response.status_code == 200


def test_api_rota_inexistente(client):
    response = client.get("/rota-que-nao-existe")
    assert response.status_code == 404


def test_api_metodo_invalido(client):
    response = client.get("/predict")
    assert response.status_code == 405
