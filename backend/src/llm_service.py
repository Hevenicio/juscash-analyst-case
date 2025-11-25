import os
from typing import Optional
from .schemas import ProcessoInput, DecisaoJudicial, DecisionEnum

# --- INTEGRAÇÃO LANGSMITH (Orquestração) ---
try:
    from langsmith import traceable
except ImportError:
    # Fallback caso a lib não esteja instalada, evita crash
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# ==============================================================================
# SERVIÇO DE INTELIGÊNCIA (BUSINESS LAYER)
# ==============================================================================

SYSTEM_PROMPT = """
Você é o motor de decisão de crédito da JusCash.
Sua análise deve seguir ESTRITAMENTE esta ORDEM DE PRIORIDADE (pare na primeira regra que for ativada):

1. **REJEIÇÃO AUTOMÁTICA (Fatal):**
   - POL-4: Se esfera for 'Trabalhista' -> REJECTED.
   - POL-3: Se valorCondenacao < 1000 -> REJECTED.
   - POL-5: Se houver óbito do autor s/ habilitação -> REJECTED.
   - POL-6: Se houver substabelecimento s/ reserva -> REJECTED.

2. **DADOS INSUFICIENTES (Prioridade sobre a recusa genérica):**
   - POL-8: Se a lista de documentos estiver vazia, ou se não houver documento/movimento provando explicitamente o 'Trânsito em Julgado' -> INCOMPLETE.
     (Justificativa: Não é possível avaliar a elegibilidade POL-1 sem a certidão).

3. **ELEGIBILIDADE FINAL:**
   - POL-1: Se tem Trânsito em Julgado E está em fase de execução -> APPROVED.
   - POL-2: Se tem valor de condenação -> APPROVED.

Se não cair em nenhuma rejeição ou incompleto, e tiver os requisitos da fase 3, aprove.
"""

class CreditAnalysisService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    # @traceable cria um "Run" no LangSmith com o nome "Credit Analysis Router"
    # run_type="chain" indica que é uma função lógica que chama outras
    @traceable(run_type="chain", name="JusCash Analysis Router")
    def analyze(self, processo: ProcessoInput) -> DecisaoJudicial:
        """
        Orquestrador Principal.
        """
        if not self.api_key:
            return self._run_mock_analysis(processo)
        return self._run_openai_analysis(processo)

    @traceable(run_type="tool", name="Mock Rules Engine")
    def _run_mock_analysis(self, processo: ProcessoInput) -> DecisaoJudicial:
        """Lógica determinística (Simulação) monitorada."""
        print("⚠️  [SERVICE] Executando em modo MOCK")
        
        # 1. Checagens de Rejeição (Fatais)
        if "Trabalhista" in processo.esfera:
            return DecisaoJudicial(
                resultado=DecisionEnum.REJECTED,
                justificativa="[MOCK] Processo trabalhista recusado automaticamente (POL-4).",
                citacoes=["POL-4"]
            )
        
        if processo.valorCondenacao and processo.valorCondenacao < 1000:
            return DecisaoJudicial(
                resultado=DecisionEnum.REJECTED,
                justificativa=f"[MOCK] Valor {processo.valorCondenacao} abaixo do mínimo (POL-3).",
                citacoes=["POL-3"]
            )

        # 2. Checagem de Documentos E Movimentos (POL-8 vs POL-1)
        docs_texto = " ".join([d.nome + " " + d.texto for d in processo.documentos]).lower()
        movs_texto = " ".join([m.descricao for m in processo.movimentos]).lower()
        
        texto_completo = docs_texto + " " + movs_texto
        
        termos_transito = ["trânsito em julgado", "transito em julgado", "sentença definitiva", "execução definitiva"]
        tem_transito = any(termo in texto_completo for termo in termos_transito)
        
        if (not processo.documentos) and (not tem_transito):
            return DecisaoJudicial(
                resultado=DecisionEnum.INCOMPLETE,
                justificativa="[MOCK] Não foram encontrados documentos ou movimentos comprovando o Trânsito em Julgado (POL-8).",
                citacoes=["POL-8"]
            )
            
        # 3. Aprovação Default
        return DecisaoJudicial(
            resultado=DecisionEnum.APPROVED,
            justificativa="[MOCK] Processo aprovado. Trânsito em julgado verificado nos autos.",
            citacoes=["POL-1", "POL-2"]
        )

    # run_type="llm" indica que esta função faz chamada a modelo de linguagem
    @traceable(run_type="llm", name="OpenAI GPT-4o-mini")
    def _run_openai_analysis(self, processo: ProcessoInput) -> DecisaoJudicial:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analise: {processo.model_dump_json()}"}
                ],
                response_format=DecisaoJudicial,
                temperature=0.0 
            )
            return response.choices[0].message.parsed
        except Exception as e:
            raise RuntimeError(f"Falha na comunicação com OpenAI: {str(e)}")