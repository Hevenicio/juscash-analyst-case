from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

# ==============================================================================
# MODELOS DE DADOS (SHARED)
# ==============================================================================

class Documento(BaseModel):
    id: str
    dataHoraJuntada: datetime
    nome: str
    texto: str

class Movimento(BaseModel):
    dataHora: datetime
    descricao: str

class Honorarios(BaseModel):
    contratuais: Optional[float] = 0.0
    periciais: Optional[float] = 0.0
    sucumbenciais: Optional[float] = 0.0

class ProcessoInput(BaseModel):
    numeroProcesso: str = Field(..., json_schema_extra={"example": "0004587-00.2021.4.05.8100"})
    classe: str
    orgaoJulgador: str
    ultimaDistribuicao: datetime
    valorCausa: Optional[float] = None # Optional para evitar erro 422, Isso é seguro porque nenhuma das regras de negócio (POL-1 a POL-8) utiliza o "Valor da Causa" para decisão (elas usam "Valor da Condenação").
    assunto: str
    segredoJustica: bool
    justicaGratuita: bool
    siglaTribunal: str
    esfera: str
    valorCondenacao: Optional[float] = None
    documentos: List[Documento]
    movimentos: List[Movimento]
    honorarios: Optional[Honorarios] = None

class DecisionEnum(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    INCOMPLETE = "incomplete"

class DecisaoJudicial(BaseModel):
    resultado: DecisionEnum = Field(..., description="Decisão final normalizada")
    justificativa: str = Field(..., description="Razão detalhada da decisão")
    citacoes: List[str] = Field(..., description="IDs das políticas aplicadas (ex: POL-1)")