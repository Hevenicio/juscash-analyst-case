from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.schemas import ProcessoInput, DecisaoJudicial
import pytest
from datetime import datetime
client = TestClient(app)

# Massa de dados base para testes
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
        "esfera": "Federal",
        "valorCondenacao": 50000.00,
        "documentos": [],
        "movimentos": [],
        "honorarios": {}
    }

def test_health_check():
    """Verifica se a API está de pé."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_rejeicao_trabalhista():
    """Testa a regra POL-4 (Esfera Trabalhista)."""
    payload = get_processo_base()
    payload["esfera"] = "Trabalhista"
    
    # Envia sem API Key para forçar modo Mock
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "rejected"
    assert "POL-4" in data["citacoes"]

def test_rejeicao_valor_baixo():
    """Testa a regra POL-3 (Valor < 1000)."""
    payload = get_processo_base()
    payload["valorCondenacao"] = 500.00
    
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "rejected"
    assert "POL-3" in data["citacoes"]

def test_incompleto_sem_documentos():
    """Testa a regra POL-8 (Falta de documentos de trânsito)."""
    payload = get_processo_base()
    payload["documentos"] = [] # Lista vazia
    
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "incomplete"
    assert "POL-8" in data["citacoes"]

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