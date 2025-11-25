# JusCash - AI Credit Analysis
Solução técnica para o desafio de Analista de Machine Learning/IA. O sistema analisa processos judiciais utilizando LLMs para determinar a elegibilidade de compra de crédito, seguindo políticas rigorosas de governança.

##  🏗 Arquitetura
O projeto segue uma arquitetura de microsserviços modularizada:

- **Frontend:** Streamlit (Interface Visual)
- **Backend:** FastAPI (API REST)
- **Core AI:** OpenAI GPT-4o-mini (Motor de Decisão com Saída Estruturada)-
- **Validadores:** Pydantic (Garantia de Schema)

## 🚀 Como Rodar
### Pré-requisitos
- Docker e Docker Compose instalados.
- Uma chave da OpenAI (opcional, o sistema roda em modo "Mock" sem ela).

#### Passo 1: Configurar Variáveis
Crie um arquivo `.env` na raiz e adicione sua chave:

```bash
OPENAI_API_KEY=sk-sua-chave-aqui
```
#### Passo 2: Executar com Docker (Recomendado)

Este comando subirá tanto a API quanto a Interface Visual.

```bash
docker-compose up --build
```

#### Passo 3: Acessar
- Interface Visual: http://localhost:850
- Documentação da API: http://localhost:8000/docs

### 📂 Estrutura de Arquivos

- **juscash_api.py**: Ponto de entrada da API.
- **juscash_frontend.py**: Cliente visual.
- **llm_service.py**: Lógica de negócio e integração com IA.
- **schemas.py**: Contratos de dados compartilhados.

### ✅ Decisões Técnicas
- [1] **Structured Outputs**: Utilização do modo `response_format` da OpenAI para garantir JSON válido e aderência estrita ao schema Pydantic.
- [2] **Separação de Responsabilidades**: O Frontend não contém lógica de negócio; ele apenas consome a API.
- [3] **Tipagem Estática**: Uso extensivo de Type Hints para robustez.



## docker compose up --build -d --remove-orphans
##  docker compose logs -f streamlit