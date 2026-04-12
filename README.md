# Classificação de Objetos Estelares — SDSS17

```
  ╔═══════════════════════════════════════════╗
  ║                                           ║
  ║    🔭  CLASSIFICADOR DE OBJETOS           ║
  ║        ESTELARES  · SDSS17                ║
  ║                                           ║
  ║    ⭐ ESTRELA  🌌 GALÁXIA  ✨ QUASAR      ║
  ║                                           ║
  ╚═══════════════════════════════════════════╝
```

MVP da sprint de Qualidade de Software, Segurança e Sistemas Inteligentes da pós-graduação em Engenharia de Software da PUC-Rio. O projeto utiliza modelos de machine learning para classificar objetos celestes em **Estrela (STAR)**, **Galáxia (GALAXY)** ou **Quasar (QSO)**, com base em dados fotométricos e espectrais do levantamento Sloan Digital Sky Survey (SDSS17).

## Links

- [Notebook no Google Colab](https://colab.research.google.com/github/almeidamx/start-classification/blob/main/notebook.ipynb)
- [Dataset — Stellar Classification Dataset SDSS17 (Kaggle)](https://www.kaggle.com/datasets/fedesoriano/stellar-classification-dataset-sdss17)

## Tecnologias

- **Machine Learning:** Python, Scikit-Learn, Pandas, NumPy, Matplotlib, Seaborn
- **Backend:** Flask, Flask-CORS
- **Frontend:** HTML, CSS, JavaScript
- **Testes:** PyTest

## Estrutura do projeto

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

## Como executar

### Pré-requisito: gerar o modelo

Antes de rodar o backend, é necessário ter o arquivo `modelo.pkl` na pasta `backend/`. Para isso:

1. Faça upload do `star_classification.csv` para este repositório
2. Atualize a variável `DATASET_URL` no `notebook.ipynb` com a URL raw do arquivo
3. Execute o notebook no Google Colab do início ao fim
4. Na última célula, o arquivo `modelo.pkl` será baixado automaticamente
5. Copie o `modelo.pkl` para a pasta `backend/`

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

**Testes incluídos (14 no total):**

| Categoria | Teste | Threshold |
|---|---|---|
| Métricas | `test_acuracia` | Acurácia ≥ 0.95 |
| Métricas | `test_f1_macro` | F1-Score macro ≥ 0.94 |
| Métricas | `test_recall_por_classe` | Recall por classe ≥ 0.90 |
| Integridade | `test_modelo_carregamento` | Modelo carregado com `.predict` |
| Integridade | `test_pipeline_contem_scaler` | Pipeline possui `StandardScaler` |
| Integridade | `test_dataset_estrutura` | Colunas e classes corretas |
| API | `test_api_home` | Redireciona GET `/` → `/docs` |
| API | `test_api_predict_sucesso` | Payload válido → 200 + `prediction` |
| API | `test_api_predict_campo_faltando` | Campo ausente → 400 |
| API | `test_api_predict_alpha_invalido` | Alpha fora do range → 400 |
| API | `test_api_predict_delta_invalido` | Delta fora do range → 400 |
| API | `test_api_predict_redshift_invalido` | Redshift fora do range → 400 |
| API | `test_api_predict_tipo_invalido` | Tipo string → 400 |
| API | `test_api_predict_sem_json` | Sem JSON → 400 |

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

## Notebook

O arquivo `notebook.ipynb` contém todo o processo de criação do modelo:

1. Carregamento do dataset via URL raw do GitHub
2. Análise Exploratória dos Dados (EDA)
3. Seleção de features e preparação dos dados
4. Separação treino/teste com holdout estratificado (80/20)
5. Pipelines com StandardScaler + KNN, Árvore de Classificação, Naive Bayes e SVM
6. Validação cruzada (StratifiedKFold, k=10)
7. Otimização de hiperparâmetros (GridSearchCV na Árvore de Classificação)
8. Avaliação e comparação dos modelos
9. Exportação do melhor modelo como `modelo.pkl`
10. Análise de resultados e conclusão

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
