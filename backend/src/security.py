from fastapi import Header, HTTPException, status
from typing import Optional
import logging
import re

# Logger dedicado para segurança (Auditoria)
logger = logging.getLogger("api-juscash-security")

async def validate_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key", description="Chave da OpenAI para processamento real")) -> Optional[str]:
    """
    Dependência de segurança (Dependency Injection).
    
    Regras:
    1. Se a chave for omitida -> Retorna None (Permite cair no modo Mock/Simulação).
    2. Se a chave for enviada -> Valida o formato (deve começar com 'sk-').
    
    Se o formato for inválido, rejeita a requisição imediatamente (401 Unauthorized),
    poupando recursos do backend.
    """
    if x_api_key:
        # Sanitização básica (remove espaços extras)
        clean_key = x_api_key.strip()
        
        if not clean_key.startswith("sk-"):
            logger.warning(f"Tentativa de acesso com chave inválida (formato incorreto): {clean_key[:5]}***")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="API Key inválida. Chaves da OpenAI devem começar com 'sk-'.")
        return clean_key

    # Se não enviou chave, loga como acesso em modo simulação
    logger.info("Requisição sem API Key identificada. Encaminhando para Modo Mock.")
    return None