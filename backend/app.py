from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import pickle
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]}})

OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Classificador de Objetos Estelares",
        "version": "1.0.0",
        "description": (
            "API para classificar objetos celestes (Estrela, Galáxia ou Quasar) "
            "com base em medidas fotométricas e espectroscópicas do levantamento SDSS."
        ),
    },
    "paths": {
        "/predict": {
            "post": {
                "summary": "Classifica um objeto celeste",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "alpha": {
                                        "type": "number",
                                        "minimum": 0.0,
                                        "maximum": 360.0,
                                        "description": "Ascensão Reta em graus (0–360)",
                                    },
                                    "delta": {
                                        "type": "number",
                                        "minimum": -90.0,
                                        "maximum": 90.0,
                                        "description": "Declinação em graus (−90–90)",
                                    },
                                    "u": {
                                        "type": "number",
                                        "minimum": -10.0,
                                        "maximum": 35.0,
                                        "description": "Magnitude na banda U (ultravioleta)",
                                    },
                                    "g": {
                                        "type": "number",
                                        "minimum": -10.0,
                                        "maximum": 35.0,
                                        "description": "Magnitude na banda G (verde)",
                                    },
                                    "r": {
                                        "type": "number",
                                        "minimum": -10.0,
                                        "maximum": 35.0,
                                        "description": "Magnitude na banda R (vermelho)",
                                    },
                                    "i": {
                                        "type": "number",
                                        "minimum": -10.0,
                                        "maximum": 35.0,
                                        "description": "Magnitude na banda I (infravermelho próximo)",
                                    },
                                    "z": {
                                        "type": "number",
                                        "minimum": -10.0,
                                        "maximum": 35.0,
                                        "description": "Magnitude na banda Z (infravermelho)",
                                    },
                                    "redshift": {
                                        "type": "number",
                                        "minimum": -0.05,
                                        "maximum": 10.0,
                                        "description": "Desvio para o vermelho espectroscópico",
                                    },
                                },
                                "required": [
                                    "alpha", "delta", "u", "g", "r", "i", "z", "redshift"
                                ],
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Classificação realizada com sucesso",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "prediction": {
                                            "type": "string",
                                            "enum": ["STAR", "GALAXY", "QSO"],
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Requisição inválida",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"error": {"type": "string"}},
                                }
                            }
                        },
                    },
                    "500": {
                        "description": "Erro interno no servidor",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"error": {"type": "string"}},
                                }
                            }
                        },
                    },
                },
            }
        }
    },
}

with open(BASE_DIR / "modelo.pkl", "rb") as f:
    modelo = pickle.load(f)


@app.route("/")
def home():
    return redirect("/docs")


@app.route("/openapi.json")
def openapi_spec():
    return jsonify(OPENAPI_SPEC)


@app.route("/docs")
def swagger_ui():
    return (
        "<!doctype html>\n"
        "<html lang=\"pt-BR\">\n"
        "  <head>\n"
        "    <meta charset=\"utf-8\" />\n"
        "    <title>Swagger UI - Classificador Estelar</title>\n"
        "    <link rel=\"stylesheet\" "
        "href=\"https://unpkg.com/swagger-ui-dist/swagger-ui.css\" />\n"
        "    <style>body { margin:0; padding:0; }</style>\n"
        "  </head>\n"
        "  <body>\n"
        "    <div id=\"swagger-ui\"></div>\n"
        "    <script "
        "src=\"https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js\"></script>\n"
        "    <script "
        "src=\"https://unpkg.com/swagger-ui-dist/swagger-ui-standalone-preset.js\"></script>\n"
        "    <script>\n"
        "      window.onload = function() {\n"
        "        SwaggerUIBundle({\n"
        "          url: '/openapi.json',\n"
        "          dom_id: '#swagger-ui',\n"
        "          presets: [\n"
        "            SwaggerUIBundle.presets.apis,\n"
        "            SwaggerUIStandalonePreset\n"
        "          ],\n"
        "          layout: 'StandaloneLayout'\n"
        "        });\n"
        "      };\n"
        "    </script>\n"
        "  </body>\n"
        "</html>\n"
    )


@app.route("/predict", methods=["POST"])
def predict():
    try:
        if not request.is_json:
            return jsonify({"error": "Requisição deve conter JSON"}), 400

        data = request.get_json()
        if data is None:
            return jsonify({"error": "JSON vazio recebido"}), 400

        required_fields = ["alpha", "delta", "u", "g", "r", "i", "z", "redshift"]
        missing_fields = [
            f for f in required_fields if f not in data or data[f] is None
        ]
        if missing_fields:
            missing = ", ".join(missing_fields)
            return (
                jsonify({"error": f"Campos obrigatórios faltando: {missing}"}),
                400,
            )

        validations = {
            "alpha":    {"min": 0.0,   "max": 360.0},
            "delta":    {"min": -90.0, "max": 90.0},
            "u":        {"min": -10.0, "max": 35.0},
            "g":        {"min": -10.0, "max": 35.0},
            "r":        {"min": -10.0, "max": 35.0},
            "i":        {"min": -10.0, "max": 35.0},
            "z":        {"min": -10.0, "max": 35.0},
            "redshift": {"min": -0.05, "max": 10.0},
        }

        for field, limits in validations.items():
            try:
                value = float(data[field])
                if value < limits["min"] or value > limits["max"]:
                    return (
                        jsonify({
                            "error": (
                                f"{field} deve estar entre "
                                f"{limits['min']} e {limits['max']}"
                            )
                        }),
                        400,
                    )
            except (ValueError, TypeError):
                return (
                    jsonify({"error": f"{field} deve ser um número válido"}),
                    400,
                )

        df = pd.DataFrame([{
            "alpha":    float(data["alpha"]),
            "delta":    float(data["delta"]),
            "u":        float(data["u"]),
            "g":        float(data["g"]),
            "r":        float(data["r"]),
            "i":        float(data["i"]),
            "z":        float(data["z"]),
            "redshift": float(data["redshift"]),
        }])

        prediction = modelo.predict(df)
        return jsonify({"prediction": prediction[0]}), 200

    except KeyError:
        return jsonify({"error": "Campo esperado não encontrado"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Erro ao processar predição"}), 500


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Rota não encontrada"}), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify({"error": "Método HTTP não permitido"}), 405


if __name__ == "__main__":
    app.run(debug=False)
