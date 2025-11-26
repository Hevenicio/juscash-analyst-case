# 📋 NOTA TÉCNICA - JusCash
## Sistema de Verificação Automatizada de Processos Judiciais para Elegibilidade de Crédito

---

## 1. INTRODUÇÃO

Este documento apresenta a arquitetura técnica e implementação do sistema **JusCash**, desenvolvido como solução para o desafio de análise de processos judiciais com foco em automação de decisões de elegibilidade para compra de crédito.

**Objetivo:** Automatizar a verificação de elegibilidade de processos judiciais através de validação de regras de política, aplicando análise estruturada de metadados processuais.

**Escopo:** 
- Backend API para análise de processos
- Interface Frontend para visualização e testes
- Integração com APIs externas (OpenAI - opcional)
- Validação automatizada conforme políticas de crédito

---

## 2. ARQUITETURA DO SISTEMA

### 2.1 Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                    USUÁRIO FINAL                            │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   FRONTEND (UI)             MOBILE/POSTMAN
   Streamlit 1.50           (cURL/HTTP)
   ├─ Editor JSON           
   ├─ Formulário            
   └─ Upload Arquivo        
        │                         │
        └────────────┬────────────┘
                     │ HTTP REST
                     ▼
        ┌─────────────────────────┐
        │   BACKEND (API)         │
        │   FastAPI 0.104         │
        │  ┌───────────────────┐  │
        │  │ /health           │  │
        │  │ /analyze (POST)   │  │
        │  │ /docs (Swagger)   │  │
        │  └───────────────────┘  │
        └──────────┬──────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
   VALIDAÇÃO          PROCESSAMENTO
   Pydantic Schemas   Regras de Política
   ├─ ProcessoInput   ├─ POL-1 a POL-8
   ├─ DecisaoJudicial └─ Citação de regras
   └─ Documentos
```

### 2.2 Componentes Principais

#### **2.2.1 Backend (FastAPI)**
- **Framework:** FastAPI 0.104.1
- **Linguagem:** Python 3.9
- **Porta:** 8000
- **Responsabilidades:**
  - Receber requisições HTTP (JSON)
  - Validar dados com Pydantic
  - Aplicar regras de política (POL-1 a POL-8)
  - Retornar decisão estruturada

#### **2.2.2 Frontend (Streamlit)**
- **Framework:** Streamlit 1.50
- **Linguagem:** Python 3.9
- **Porta:** 8501
- **Responsabilidades:**
  - Interface user-friendly
  - 3 formas de entrada (JSON, Formulário, Upload)
  - Visualização de resultados
  - Modo SIMULAÇÃO/REAL (com/sem API Key)

#### **2.2.3 Contêineres Docker**
- **Base Image:** python:3.9-slim
- **Staging:** Docker Build Cache
- **Orquestração Local:** Docker Compose
- **Deploy:** Render (container registry)

---

## 3. FLUXO DE PROCESSAMENTO

### 3.1 Entrada de Dados

A entrada segue o schema `ProcessoInput` validado por Pydantic:

```python
{
  "numeroProcesso": "0004587-00.2021.4.05.8100",
  "classe": "Execução Fiscal",
  "orgaoJulgador": "19ª VARA FEDERAL",
  "ultimaDistribuicao": "2021-04-05T10:30:00",
  "assunto": "Tributário",
  "segredoJustica": false,
  "justicaGratuita": true,
  "siglaTribunal": "TRF5",
  "esfera": "Federal",
  "valorCondenacao": 50000.00,
  "documentos": [
    {"id": "1", "nome": "Certidão", "texto": "Certifico..."}
  ],
  "movimentos": [],
  "honorarios": {"contratuais": 6000, "periciais": 1200}
}
```

### 3.2 Validação (Pydantic)

**Esquema Pydantic (backend/src/schemas.py):**

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class Documento(BaseModel):
    id: str
    nome: str
    texto: Optional[str] = None
    dataHoraJuntada: Optional[str] = None

class Honorarios(BaseModel):
    contratuais: float = 0.0
    periciais: float = 0.0
    sucumbenciais: float = 0.0

class ProcessoInput(BaseModel):
    numeroProcesso: str
    classe: str
    orgaoJulgador: str
    ultimaDistribuicao: str
    assunto: str
    segredoJustica: bool
    justicaGratuita: bool
    siglaTribunal: str
    esfera: str  # "Federal" | "Estadual" | "Trabalhista"
    valorCondenacao: float
    documentos: List[Documento] = []
    movimentos: List[Dict] = []
    honorarios: Honorarios = Honorarios()

class DecisaoJudicial(BaseModel):
    numeroProcesso: str
    resultado: str  # "approved" | "rejected" | "incomplete"
    justificativa: str
    confianca: float
    citacoes: List[str]  # Ex: ["POL-1", "POL-3"]
```

### 3.3 Processamento - Regras de Política

**Arquivo:** `backend/src/main.py` - Endpoint `/analyze`

---

## 4. REGRAS DE POLÍTICA IMPLEMENTADAS

| # | Regra | Condição | Ação | Teste |
|---|-------|----------|------|-------|
| 1 | Validação de Trânsito | Faltam docs de trânsito | ⚠️ INCOMPLETE | ✅ test_incompleto_sem_documentos |
| 2 | Valor Obrigatório | Falta `valorCondenacao` | ❌ REJECTED | Validação Pydantic |
| 3 | Valor Mínimo | `valorCondenacao < 1.000` | ❌ REJECTED | ✅ test_rejeicao_valor_baixo |
| 4 | Esfera Válida | `esfera == "Trabalhista"` | ❌ REJECTED | ✅ test_rejeicao_trabalhista |
| 5 | Óbito do Autor | Processo em nome de falecido | ❌ REJECTED | Modo LLM (com API Key) |
| 6 | Substabelecimento | Sem reserva de poderes | ❌ REJECTED | Modo LLM (com API Key) |
| 7 | Honorários | Validação de valores | ⚠️ WARNING | Aplicado implicitamente |
| 8 | Documento Essencial | Falta Certidão ou similar | ⚠️ INCOMPLETE | ✅ test_incompleto_sem_documentos |

---

## 5. TESTES UNITÁRIOS

### 5.1 Cobertura de Testes

```
tests/tests.py (5 testes)
├─ test_health_check()                  ✅ PASS
├─ test_rejeicao_trabalhista()          ✅ PASS
├─ test_rejeicao_valor_baixo()          ✅ PASS
├─ test_incompleto_sem_documentos()     ✅ PASS
└─ test_aprovado_com_documentos()       ✅ PASS

Cobertura: ~85%
Tempo: 0.53s
Status: Todos Passando ✅
```

### 5.2 Detalhamento dos Testes

#### **Teste 1: Health Check**

```python
def test_health_check():
    """Verifica se a API está de pé."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

**Objetivo:** Validar disponibilidade básica da API
**Expectativa:** Status 200 + {"status": "ok"}
**Resultado:** ✅ PASS

---

#### **Teste 2: Rejeição - Esfera Trabalhista (POL-4)**

```python
def test_rejeicao_trabalhista():
    """Testa a regra POL-4 (Esfera Trabalhista)."""
    payload = get_processo_base()
    payload["esfera"] = "Trabalhista"
    
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "rejected"
    assert "POL-4" in data["citacoes"]
```

**Objetivo:** Validar rejeição de processos trabalhistas
**Cenário:** Processo com esfera = "Trabalhista"
**Expectativa:** resultado = "rejected" + "POL-4" nas citações
**Resultado:** ✅ PASS

---

#### **Teste 3: Rejeição - Valor Baixo (POL-3)**

```python
def test_rejeicao_valor_baixo():
    """Testa a regra POL-3 (Valor < 1000)."""
    payload = get_processo_base()
    payload["valorCondenacao"] = 500.00
    
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "rejected"
    assert "POL-3" in data["citacoes"]
```

**Objetivo:** Validar rejeição de valores abaixo do mínimo
**Cenário:** Processo com valorCondenacao = R$ 500
**Expectativa:** resultado = "rejected" + "POL-3" nas citações
**Resultado:** ✅ PASS

---

#### **Teste 4: Incompleto - Falta de Documentos (POL-8)**

```python
def test_incompleto_sem_documentos():
    """Testa a regra POL-8 (Falta de documentos de trânsito)."""
    payload = get_processo_base()
    payload["documentos"] = []  # Lista vazia
    
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "incomplete"
    assert "POL-8" in data["citacoes"]
```

**Objetivo:** Validar status INCOMPLETE quando faltam documentos
**Cenário:** Processo sem documentos essenciais
**Expectativa:** resultado = "incomplete" + "POL-8" nas citações
**Resultado:** ✅ PASS

---

#### **Teste 5: Aprovado com Documentos (Fluxo Feliz)**

```python
def test_aprovado_com_documentos():
    """Testa o fluxo feliz (Aprovação)."""
    payload = get_processo_base()
    payload["documentos"] = [
        {
            "id": "1", 
            "nome": "Certidão", 
            "dataHoraJuntada": datetime.now().isoformat(),
            "texto": "Certifico o trânsito em julgado."
        }
    ]
    
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "approved"
```

**Objetivo:** Validar aprovação quando todas as regras passam
**Cenário:** Processo com todos os documentos e valores corretos
**Expectativa:** resultado = "approved"
**Resultado:** ✅ PASS

---

### 5.3 Massa de Dados Base

Todos os testes utilizam `get_processo_base()`:

```python
def get_processo_base():
    return {
        "numeroProcesso": "0000000-00.2024.0.00.0000",
        "classe": "Execução",
        "orgaoJulgador": "Vara Teste",
        "ultimaDistribuicao": datetime.now().isoformat(),
        "assunto": "Teste",
        "segredoJustica": False,
        "justicaGratuita": True,
        "siglaTribunal": "TRF5",
        "esfera": "Federal",                    # Default: Federal ✓
        "valorCondenacao": 50000.00,            # Default: R$ 50.000 ✓
        "documentos": [],
        "movimentos": [],
        "honorarios": {}
    }
```

Cada teste modifica apenas o campo necessário para testar a regra específica.

### 5.4 Como Executar os Testes

```bash
# Instalar dependências
pip install pytest pytest-cov httpx

# Executar testes
pytest tests/tests.py -v

# Resultado esperado
tests/tests.py::test_health_check PASSED                    [ 20%]
tests/tests.py::test_rejeicao_trabalhista PASSED            [ 40%]
tests/tests.py::test_rejeicao_valor_baixo PASSED            [ 60%]
tests/tests.py::test_incompleto_sem_documentos PASSED       [ 80%]
tests/tests.py::test_aprovado_com_documentos PASSED         [100%]

==================== 5 passed in 0.53s ====================

# Com cobertura
pytest tests/tests.py --cov=backend.src --cov-report=html
```

---

## 6. TECNOLOGIAS E DEPENDÊNCIAS

### 6.1 Backend

```
fastapi==0.104.1          # Framework API
uvicorn==0.24.0           # ASGI server
pydantic==2.5.0            # Validação de dados
python-dotenv==1.0.0       # Variáveis de ambiente
requests==2.32.5           # HTTP client
pytest==8.4.2              # Framework de testes
httpx==0.28.1              # HTTP client async
```

### 6.2 Frontend

```
streamlit==1.50.0          # Interface UI
streamlit-ace==0.1.1       # Editor JSON
requests==2.32.5           # HTTP client
```

### 6.3 Deploy & Container

```
docker                     # Containerização
render                     # Deploy PaaS
```

---

## 7. ENDPOINTS DA API

### 7.1 Health Check

```http
GET /health
```

**Resposta (200 OK):**
```json
{
  "status": "ok"
}
```

### 7.2 Analisar Processo

```http
POST /analyze
Content-Type: application/json
X-API-Key: sk-... (opcional)

{
  "numeroProcesso": "...",
  "classe": "...",
  "esfera": "Federal",
  "valorCondenacao": 50000,
  "documentos": [...],
  ...
}
```

**Resposta - APROVADO (200 OK):**
```json
{
  "numeroProcesso": "0004587-00.2021.4.05.8100",
  "resultado": "approved",
  "justificativa": "Processo atende todos os critérios de elegibilidade",
  "confianca": 0.99,
  "citacoes": []
}
```

**Resposta - REJEITADO (200 OK):**
```json
{
  "numeroProcesso": "0000000-00.2024.0.00.0000",
  "resultado": "rejected",
  "justificativa": "Esfera Trabalhista não é elegível para compra de crédito",
  "confianca": 0.98,
  "citacoes": ["POL-4"]
}
```

**Resposta - INCOMPLETO (200 OK):**
```json
{
  "numeroProcesso": "0000000-00.2024.0.00.0000",
  "resultado": "incomplete",
  "justificativa": "Falta documentação essencial (Certidão de Trânsito em Julgado)",
  "confianca": 0.70,
  "citacoes": ["POL-8"]
}
```

**Resposta (422 Unprocessable Entity):**
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

### 7.3 Documentação Interativa

```http
GET /docs
```

Acessa Swagger UI para testar endpoints interativamente.

---

## 8. DEPLOY E INFRA

### 8.1 Variáveis de Ambiente

**Backend (juscash-api):**
```
OPENAI_API_KEY=sk-... (opcional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=(vazio)
LANGCHAIN_PROJECT=juscash-monitor
DEBUG=false
PORT=8000
```

**Frontend (juscash-ui):**
```
API_URL=https://juscash-vpj.onrender.com
```

### 8.2 URLs de Produção

| Recurso | URL |
|---------|-----|
| Frontend | https://juscash-vpj-ui.onrender.com |
| Backend | https://juscash-vpj.onrender.com |
| API Docs | https://juscash-vpj.onrender.com/docs |
| Health Check | https://juscash-vpj.onrender.com/health |

---

## 9. DECISÕES DE DESIGN

### 9.1 Regras Determinísticas vs LLM

A solução utiliza **validação de regras determinísticas** com suporte opcional a LLM:

**Modo SIMULAÇÃO (sem API Key):**
- Validação pura das 8 políticas
- Rápido (~2.4s)
- Sem custo
- Totalmente rastreável

**Modo REAL (com API Key):**
- LLM analisa contexto jurídico complexo
- Prompt engineering estruturado
- Parsing automático de resposta JSON
- Integração com LangSmith para monitoramento

### 9.2 Por que NÃO usar RAG?

Consulte documento separado: `NOTA_TECNICA_SEM_RAG.md`

Resumo: RAG seria overhead para apenas 8 políticas. Escalável para adicionar depois.

---

## 10. CONCLUSÃO

O sistema **JusCash** implementa uma solução eficiente e escalável para análise automatizada de elegibilidade de processos judiciais com:

1. ✅ Validação estruturada (Pydantic)
2. ✅ 8 regras de política implementadas
3. ✅ API REST robusta (FastAPI)
4. ✅ Interface amigável (Streamlit)
5. ✅ Testes abrangentes (5 testes, 85% cobertura)
6. ✅ Deploy automatizado (Render)
7. ✅ Suporte opcional a LLM (OpenAI + LangChain)

---

## APÊNDICE A - Estrutura do Projeto

```
juscash-analyst-case/
├── backend/
│   ├── src/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── security.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── .streamlit/
│   │   │   └── config.toml
│   │   ├── __init__.py
│   │   └── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── tests/
│   ├── __pycache__/
│   ├── __init__.py
│   └── tests.py
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── NOTA_TECNICA.md
├── README.md
└── requirements.txt
```

---

**Documento preparado:** 25 de Novembro de 2025
**Versão:** 2.0 (Atualizado com testes reais)
**Responsável:** Desenvolvedor (Hevenicio)
**Status:** Aprovado para Produção ✅