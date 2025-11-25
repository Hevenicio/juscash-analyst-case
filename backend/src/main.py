from fastapi import FastAPI, HTTPException, Depends
from typing import Optional
import logging
import sys

from .schemas import ProcessoInput, DecisaoJudicial
from .llm_service import CreditAnalysisService
# Importa a nova dependência de segurança
from .security import validate_api_key

# ==============================================================================
# 1. CONFIGURAÇÃO DE LOGGING
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("api-juscash")

# ==============================================================================
# 2. CONFIGURAÇÃO DA API
# ==============================================================================
app = FastAPI(
    title="JusCash - Verificador de Processos Judiciais API",
    description="API responsável por validar processos judiciais usando Regras de Política e LLM. Analisa elegibilidade de crédito baseada em metadados jurídicos.",
    version="2.2.0"
)

@app.get("/health", tags=["Status"])
async def health_check():
    logger.debug("Health check solicitado.")
    return {"status": "ok", "service": "juscash-modular-api"}

@app.post("/analyze", response_model=DecisaoJudicial, tags=["Core"])
async def analyze_process(processo: ProcessoInput,
                          api_key: Optional[str] = Depends(validate_api_key) # Depends() para injetar a validação
                          ):
    """
    Endpoint REST protegido.
    A validação da API Key ocorre ANTES de entrar nesta função.
    """
    logger.info(f"Recebendo solicitação de análise para o processo: {processo.numeroProcesso}")
    
    try:
        # Injeta a chave já validada (ou None) no serviço
        service = CreditAnalysisService(api_key=api_key)
        
        logger.debug("Enviando dados para o Motor de IA...")
        resultado = service.analyze(processo)
        
        logger.info(f"Processo {processo.numeroProcesso} processado. Decisão: {resultado.resultado}")
        
        return resultado
        
    except RuntimeError as e:
        logger.error(f"Erro Operacional no LLM Service: {str(e)}")
        raise HTTPException(status_code=502, detail=str(e))
        
    except Exception as e:
        logger.error(f"Erro Crítico não tratado: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno no servidor.")

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor Uvicorn com Módulo de Segurança...")
    uvicorn.run("juscash_api:app", host="0.0.0.0", port=8000, reload=True)