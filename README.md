# 🏛️ JusCash - Verificador de Processos Judiciais com IA

[![Frontend Status](https://img.shields.io/badge/Frontend-Online-green)](https://juscash-vpj-ui.onrender.com)
[![API Status](https://img.shields.io/badge/API-Online-green)](https://juscash-vpj.onrender.com)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-brightgreen)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50-red)](https://streamlit.io/)

## 📋 Sobre o Projeto

**JusCash** é um sistema inteligente de análise de processos judiciais que utiliza **Inteligência Artificial** (LangChain + OpenAI) para automatizar a verificação de elegibilidade de processos para **compra de crédito**. O sistema aplica **Regras de Política** (Políticas de Crédito) em metadados judiciais, determinando se um processo deve ser:

- ✅ **Approved** (Aprovado) - Processo atende todas as políticas
- ❌ **Rejected** (Rejeitado) - Processo viola alguma política
- ⚠️ **Incomplete** (Incompleto) - Falta documentação essencial

### Características

- 🤖 **IA Integrada**: LLM (Large Language Model) com prompt engineering para análise contextual
- 📊 **Regras de Política**: Validação automática conforme políticas de crédito
- 🌐 **API REST**: Backend FastAPI com documentação Swagger automática
- 🎨 **Interface Amigável**: Frontend Streamlit com editor JSON integrado
- 🐳 **Docker Ready**: Deploy com Docker Compose local e Render em produção
- 📈 **Análise Estruturada**: JSON estruturado (schemas Pydantic) para input/output
- 🔐 **Segurança**: API Key para controle de acesso (OpenAI)

---

## 🚀 Quick Start

### Opção 1: Produção (Render - Recomendado)

Acesse diretamente:

| Serviço | URL |
|---------|-----|
| **Frontend (UI)** | https://juscash-vpj-ui.onrender.com |
| **Backend (API)** | https://juscash-vpj.onrender.com |
| **API Docs (Swagger)** | https://juscash-vpj.onrender.com/docs |

### Opção 2: Local (Docker Compose)

```bash
# Clone o repositório
git clone https://github.com/Hevenicio/juscash-analyst-case.git
cd juscash-analyst-case

# Inicie os serviços
docker-compose up

# Acesse
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

### Opção 3: Local (Desenvolvimento)

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8000

# Frontend (outro terminal)
cd frontend
pip install -r requirements.txt
streamlit run src/app.py --server.port 8501
```

---

## 📁 Estrutura do Projeto

```
juscash-analyst-case/
├── backend/                          # API FastAPI
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # Aplicação principal
│   │   ├── llm_service.py           # Integração com OpenAI/LangChain
│   │   ├── schemas.py               # Modelos Pydantic (validação)
│   │   └── security.py              # Autenticação (API Key)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                         # UI Streamlit
│   ├── src/
│   │   ├── __init__.py
│   │   ├── app.py                   # Interface principal
│   │   └── .streamlit/              # Configuração Streamlit
│   ├── requirements.txt
│   └── Dockerfile
├── tests/                            # Testes unitários
│   └── tests.py
├── Dockerfile                        # Dockerfile unificado (root)
├── requirements.txt                  # Requirements unificado
├── docker-compose.yml                # Orquestração local
├── README.md                         # Este arquivo
└── .gitignore

```

---

## 🔧 Configuração

### Variáveis de Ambiente

#### Backend (API)

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `OPENAI_API_KEY` | `sk-...` | Chave OpenAI (deixar vazio para modo simulação) |
| `LANGCHAIN_TRACING_V2` | `true` | Ativar tracing do LangChain |
| `LANGCHAIN_ENDPOINT` | `https://api.smith.langchain.com` | Endpoint do LangSmith |
| `LANGCHAIN_API_KEY` | `(vazio)` | Chave LangSmith |
| `LANGCHAIN_PROJECT` | `juscash-monitor` | Projeto LangChain |
| `PORT` | `8000` | Porta da API |
| `DEBUG` | `false` | Modo debug |

#### Frontend (UI)

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `API_URL` | `https://juscash-vpj.onrender.com` | URL da API (produção) |

---

## 📡 API Endpoints

### Base URL
```
https://juscash-vpj.onrender.com
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Resposta:**
```json
{
  "status": "ok"
}
```

#### 2. Analisar Processo
```http
POST /analyze
Content-Type: application/json
X-API-Key: (opcional)

{
  "numeroProcesso": "0004587-00.2021.4.05.8100",
  "classe": "Execução Fiscal",
  "orgaoJulgador": "Vara Federal 1",
  "ultimaDistribuicao": "2025-11-26T01:35:36.440318",
  "assunto": "Tributário",
  "segredoJustica": false,
  "justicaGratuita": true,
  "siglaTribunal": "TRF5",
  "esfera": "Federal",
  "valorCondenacao": 50000.00,
  "documentos": [],
  "movimentos": [],
  "honorarios": {}
}
```

**Resposta (Sucesso - 200):**
```json
{
  "numeroProcesso": "0004587-00.2021.4.05.8100",
  "resultado": "approved",
  "justificativa": "Processo atende todos os critérios de elegibilidade...",
  "confianca": 0.95,
  "regrasAplicadas": [
    "valor_maximo_permitido",
    "documentacao_completa"
  ]
}
```

**Resposta (Erro - 422):**
```json
{
  "detail": [
    {
      "loc": ["body", "numeroProcesso"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🎯 Como Usar

### Via Frontend (Recomendado para usuários não-técnicos)

1. Acesse: https://juscash-vpj-ui.onrender.com
2. Escolha uma das 3 abas:
   - **💻 Editor JSON**: Cole/edite JSON manualmente
   - **📝 Formulário Completo**: Preencha campos individuais
   - **📂 Upload Arquivo**: Carregue arquivo JSON
3. Clique **"Analisar JSON"** ou **"Analisar Arquivo"**
4. Veja resultado em tempo real

**Modo de Operação:**
- **Sem API Key**: Modo SIMULAÇÃO (usa regras locais)
- **Com API Key**: Modo REAL (conecta ao OpenAI)

### Via API (cURL)

```bash
# Sem API Key (Simulação)
curl -X POST https://juscash-vpj.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "numeroProcesso": "0000001-00.2025.1.00.0000",
    "classe": "Ação Ordinária",
    "esfera": "Federal",
    "valorCondenacao": 50000,
    "documentos": [],
    "movimentos": [],
    "honorarios": {}
  }'

# Com API Key (Real)
curl -X POST https://juscash-vpj.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-..." \
  -d '{...}'
```

### Via Swagger (Documentação Interativa)

```
https://juscash-vpj.onrender.com/docs
```

---

## 🧪 Testes

### Executar Testes Localmente

```bash
# Instale dependências de teste
pip install pytest httpx

# Execute os testes
pytest tests/tests.py -v

# Com cobertura
pytest tests/tests.py --cov=backend/src --cov-report=html
```

### Testes Disponíveis

```
✅ Test Health Check
✅ Test Analyze - Approved Process
✅ Test Analyze - Rejected Process
✅ Test Analyze - Incomplete Documentation
✅ Test Missing Required Fields
```

---

## 📊 Schemas de Dados

### Input: ProcessoInput

```python
{
  "numeroProcesso": str,              # Ex: "0004587-00.2021.4.05.8100"
  "classe": str,                      # Ex: "Execução Fiscal"
  "orgaoJulgador": str,               # Ex: "Vara Federal 1"
  "ultimaDistribuicao": str,          # ISO timestamp
  "assunto": str,                     # Ex: "Tributário"
  "segredoJustica": bool,
  "justicaGratuita": bool,
  "siglaTribunal": str,               # Ex: "TRF5"
  "esfera": str,                      # "Federal" | "Estadual" | "Trabalhista"
  "valorCondenacao": float,
  "documentos": list[Documento],
  "movimentos": list[Movimento],
  "honorarios": Honorarios
}
```

### Output: DecisaoJudicial

```python
{
  "numeroProcesso": str,
  "resultado": str,                   # "approved" | "rejected" | "incomplete"
  "justificativa": str,
  "confianca": float,                 # 0.0 - 1.0
  "regrasAplicadas": list[str]
}
```

---

## 🚢 Deploy

### Em Render

#### Backend

1. **Dashboard Render** → New + → Web Service
2. **Conectar** repositório `juscash-analyst-case`
3. **Configurar:**
   - Name: `juscash-api`
   - Language: `Docker`
   - Dockerfile Path: (deixe vazio)
   - Instance Type: `Free`

4. **Environment Variables:**
   ```
   OPENAI_API_KEY = (vazio para modo simulação)
   LANGCHAIN_TRACING_V2 = true
   LANGCHAIN_ENDPOINT = https://api.smith.langchain.com
   LANGCHAIN_API_KEY = (vazio)
   LANGCHAIN_PROJECT = juscash-monitor
   PYTHONPATH = /app
   DEBUG = false
   PORT = 8000
   ```

5. **Create Web Service**

#### Frontend

1. **Dashboard Render** → New + → Web Service
2. **Conectar** repositório `juscash-analyst-case`
3. **Configurar:**
   - Name: `juscash-ui`
   - Language: `Docker`
   - Dockerfile Path: `frontend/Dockerfile`
   - Instance Type: `Free`

4. **Environment Variables:**
   ```
   API_URL = https://juscash-api-XXXXX.onrender.com
   ```

5. **Create Web Service**

---

## 📝 Exemplos de Uso

### Exemplo 1: Processo Aprovado

```json
{
  "numeroProcesso": "0004587-00.2021.4.05.8100",
  "classe": "Execução Fiscal",
  "orgaoJulgador": "19ª VARA FEDERAL",
  "ultimaDistribuicao": "2021-04-05T00:00:00",
  "assunto": "Tributário",
  "segredoJustica": false,
  "justicaGratuita": false,
  "siglaTribunal": "TRF5",
  "esfera": "Federal",
  "valorCondenacao": 50000.00,
  "documentos": [
    {"id": "DOC-1", "nome": "Sentença de Mérito"},
    {"id": "DOC-2", "nome": "Certidão de Trânsito em Julgado"}
  ],
  "movimentos": [],
  "honorarios": {"contratuais": 6000, "periciais": 1200}
}
```

**Resultado:**
```json
{
  "resultado": "approved",
  "justificativa": "Processo atende todos os critérios...",
  "confianca": 0.98
}
```

### Exemplo 2: Processo Rejeitado

```json
{
  "numeroProcesso": "0000001-00.2025.1.00.0000",
  "classe": "Ação Ordinária",
  "valorCondenacao": 500.00,  // Valor muito baixo
  "documentos": [],  // Sem documentação
  ...
}
```

**Resultado:**
```json
{
  "resultado": "rejected",
  "justificativa": "Valor da condenação abaixo do mínimo permitido...",
  "confianca": 0.92
}
```

---

## 🛠️ Troubleshooting

### Problema: "Backend indisponível"

**Solução:** Verificar se `API_URL` está configurada corretamente no Render

```bash
# Frontend Environment Variables
API_URL = https://juscash-vpj.onrender.com
```

### Problema: Erro 404 na raiz da API

**Solução:** Normal! A API não tem rota raiz. Use os endpoints corretos:

```
✅ GET /health
✅ POST /analyze
✅ GET /docs (Swagger)
```

### Problema: "erro ao conectar OpenAI"

**Solução:** Verificar se `OPENAI_API_KEY` é válida:

```bash
# Testar localmente
export OPENAI_API_KEY=sk-...
python -c "import openai; print('OK')"
```

---

## 📚 Documentação Técnica

### LangChain + OpenAI

O sistema utiliza **LangChain** para orquestração de prompts com **GPT-4/3.5**:

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
prompt = ChatPromptTemplate.from_template("Analise o processo: {processo}")
```

### Regras de Política

Validações automáticas implementadas:

1. **Valor Mínimo**: R$ 10.000,00
2. **Documentação Completa**: Sentença + Certidão de Trânsito
3. **Segredo de Justiça**: Não permitido
4. **Esfera Válida**: Federal ou Estadual

---

## 🤝 Contribuindo

1. Faça um Fork
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📞 Suporte

| Canal | Contato |
|-------|---------|
| **LinkedIn** | https://www.linkedin.com/in/hevenicio |
| **API Docs** | https://juscash-vpj.onrender.com/docs |

---

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja `LICENSE` para detalhes.

---

## 🎉 Créditos

- **Framework**: FastAPI + Streamlit
- **IA**: OpenAI GPT-3.5/4 + LangChain
- **Deploy**: Render
- **Container**: Docker

---

## 📈 Status do Projeto

| Componente | Status | Última Atualização |
|-----------|--------|-------------------|
| Backend API | ✅ Online | 2025-11-26 |
| Frontend UI | ✅ Online | 2025-11-26 |
| Testes | ✅ 5/5 Passando | 2025-11-26 |
| Cobertura | ✅ ~85% | 2025-11-26 |

---

**Desenvolvido com ❤️ para análise automatizada de processos judiciais**
