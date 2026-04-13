# Classificação de Objetos Estelares — SDSS17

MVP da sprint de Qualidade de Software, Segurança e Sistemas Inteligentes da pós-graduação em Engenharia de Software da PUC-Rio. O projeto utiliza modelos de machine learning para classificar objetos celestes em **Estrela (STAR)**, **Galáxia (GALAXY)** ou **Quasar (QSO)**, com base em dados fotométricos e espectrais do levantamento Sloan Digital Sky Survey (SDSS17).

## Links

- [Notebook no Google Colab](https://colab.research.google.com/github/almeidamx/classificadorestelar/blob/master/MVP_Qualidade_Software_Seguranca_Sistemas_Inteligentes.ipynb)
- [Video](https://youtu.be/CJ6Kn4ZvTQs)
- [Dataset — Stellar Classification Dataset SDSS17 (Kaggle)](https://www.kaggle.com/datasets/fedesoriano/stellar-classification-dataset-sdss17)

## Tecnologias

- **Machine Learning:** Python, Scikit-Learn, Pandas, NumPy, Matplotlib, Seaborn
- **Backend:** Flask, Flask-CORS
- **Frontend:** HTML, CSS, JavaScript
- **Testes:** PyTest


## Como executar

### Backend

No terminal, a partir da raiz do projeto:

```bash
cd backend
python -m venv env
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate

pip install -r requirements.txt
python app.py
```

O servidor será iniciado em `http://localhost:5000`

### Frontend

Com o backend rodando, abra um segundo terminal na pasta `frontend`:

```bash
cd frontend
python -m http.server 8000
```

Acesse `http://localhost:8000` no navegador.

> O backend restringe CORS apenas para `localhost:5000` e `localhost:8000`.

### API

- **Documentação interativa (Swagger UI):** `http://localhost:5000/docs`
- A raiz `http://localhost:5000/` redireciona automaticamente para a documentação.

**Endpoint de predição:**

- Método: `POST /predict`
- Content-Type: `application/json`

**Corpo da requisição:**

```json
{
  "alpha":    135.689157,
  "delta":    32.494632,
  "u":        23.87882,
  "g":        22.27530,
  "r":        20.39501,
  "i":        19.16573,
  "z":        18.79371,
  "redshift": 0.6347
}
```

**Campos e ranges aceitos:**

| Campo | Descrição | Tipo | Range aceito |
|---|---|---|---|
| `alpha` | Ascensão Reta | decimal | 0 – 360° |
| `delta` | Declinação | decimal | −90 – 90° |
| `u` | Magnitude banda ultravioleta | decimal | −10 – 35 |
| `g` | Magnitude banda verde | decimal | −10 – 35 |
| `r` | Magnitude banda vermelha | decimal | −10 – 35 |
| `i` | Magnitude banda infravermelho próximo | decimal | −10 – 35 |
| `z` | Magnitude banda infravermelha | decimal | −10 – 35 |
| `redshift` | Desvio espectral para o vermelho | decimal | −0.05 – 10 |

**Resposta de sucesso (200):**

```json
{ "prediction": "GALAXY" }
```

Valores possíveis: `"STAR"`, `"GALAXY"`, `"QSO"`

**Respostas de erro:**

```json
{ "error": "Campos obrigatórios faltando: redshift" }
{ "error": "alpha deve estar entre 0.0 e 360.0" }
{ "error": "redshift deve ser um número válido" }
{ "error": "Requisição deve conter JSON" }
```

### Testes

Na raiz do projeto, com o ambiente virtual ativado:

```bash
# Windows:
backend\env\Scripts\activate
# macOS/Linux:
source backend/env/bin/activate

pytest backend/test_model.py -v
```

**Testes incluídos (14 no total)**

## Dataset

**Fonte:** [Stellar Classification Dataset — SDSS17](https://www.kaggle.com/datasets/fedesoriano/stellar-classification-dataset-sdss17) (Kaggle / fedesoriano)

| Atributo | Detalhe |
|---|---|
| Registros | 100.000 |
| Features usadas | 8 (alpha, delta, u, g, r, i, z, redshift) |
| Variável alvo | `class` → STAR / GALAXY / QSO |
| Valores nulos | Nenhum |
| Encoding | Nenhum — todas as features são numéricas |

O modelo final (Árvore de Classificação otimizada via GridSearchCV) atingiu **acurácia superior a 97%** no conjunto de teste holdout.

## Integração contínua

O repositório inclui um workflow GitHub Actions em `.github/workflows/python-app.yml` que executa `pytest backend/test_model.py -v` em cada push e pull request para `main`.

## Segurança

Práticas de segurança adotadas no projeto:

- **Validação de entrada no backend:** todos os campos são validados em tipo e range antes de qualquer predição — prevenção contra injeção de dados maliciosos (OWASP A03)
- **Validação redundante no frontend:** o cliente também valida os dados antes de enviar, reduzindo requisições inválidas
- **CORS restrito:** o header CORS só permite requisições de `localhost:5000` e `localhost:8000`
- **`debug=False` em produção:** o servidor Flask não expõe stack traces ao cliente
- **Sem logging de dados de entrada:** os valores recebidos na API não são registrados em logs, protegendo a privacidade dos dados observacionais
- **Pipeline embutida:** o `StandardScaler` está encapsulado dentro do `modelo.pkl`, eliminando risco de inconsistência de transformação entre treino e produção
- **Dataset de domínio público:** os dados astronômicos do SDSS são públicos e não contêm informações pessoais identificáveis (PII)

- ## Estrutura do projeto

```
├── .github/
│   └── workflows/
│       └── python-app.yml     # Workflow de CI (GitHub Actions)
├── backend/
│   ├── app.py                 # API Flask com Swagger UI embutido
│   ├── modelo.pkl             # Pipeline treinada (scaler + modelo)
│   ├── test_model.py          # Testes automatizados (PyTest)
│   └── requirements.txt       # Dependências Python com versões fixas
├── frontend/
│   ├── index.html             # Página principal
│   ├── style.css              # Tema visual espacial (dark space)
│   └── script.js              # Lógica do frontend e validação
├── notebook.ipynb             # Notebook Colab — criação do modelo
└── star_classification.csv    # Dataset (após upload no repositório)
```
