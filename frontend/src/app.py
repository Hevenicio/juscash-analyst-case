from streamlit_ace import st_ace
from typing import Dict
import streamlit as st
import requests
import logging
import json
import sys
import os
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAÇÃO DE LOGGING
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [FRONTEND] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("juscash-ui")

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA E CONEXÃO
# ==============================================================================
st.set_page_config(page_title = "JusCash - UI", layout = "wide", page_icon = "⚖️")

# Determinação dinâmica do Backend
# API_URL = "http://backend:8000" 

# try:
#     requests.get(f"{API_URL}/health", timeout = 1)
#     logger.info(f"Conectado ao ambiente Docker: {API_URL}")
# except:
#     API_URL = "http://localhost:8000"
#     logger.info(f"Ambiente Docker não encontrado. Usando Localhost: {API_URL}")


API_URL = os.getenv("API_URL", "http://localhost:8000")
logger.info(f"API URL configurada: {API_URL}")


def send_request(data: Dict, api_key: str = None):
    """Envia requisição para a API com logging."""
    headers = {"X-API-Key": api_key} if api_key else {}
    
    if api_key:
        masked_key = f"{api_key[:3]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
        logger.info(f"Modo REAL ativado. Usando API Key: {masked_key}")
    else:
        logger.info("Modo SIMULAÇÃO ativado (Sem API Key fornecida).")

    logger.info(f"Enviando processo {data.get('numeroProcesso', 'N/A')} para análise...")
    
    try:
        # Timeout maior (30s) para LLMs
        res = requests.post(f"{API_URL}/analyze", json = data, headers = headers, timeout = 30)
        res.raise_for_status()
        logger.info("Resposta da API recebida com sucesso (200 OK).")
        return res.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Backend indisponível. Verifique se a API está rodando."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Erro da API ({res.status_code}): {res.text}"}
    except Exception as e:
        return {"error": str(e)}

# ==============================================================================
# 3. INTERFACE (UI)
# ==============================================================================
st.markdown("<h1 style='text-align: center;'>⚖️ JusCash - Verificador de Processos Judiciais</h1>", unsafe_allow_html = True)
st.divider()

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Sobre o Sistema")
    st.markdown("""
    Este sistema utiliza IA para analisar processos judiciais e determinar
    se devem ser aprovados, rejeitados ou estão incompletos para compra de crédito.
    
    **Decisões possíveis:**
    - ✅ **Approved**: Processo atende todas as políticas
    - ❌ **Rejected**: Processo viola alguma política
    - ⚠️ **Incomplete**: Falta documentação essencial
    """)
    st.divider()

col1, col2 = st.columns(2, border = True)

with col1:
    st.subheader("Entrada de Dados")
    with st.sidebar:
        st.markdown("#### Configuração")
        api_key = st.text_input("Adicione a chave (sk-...) API da OpenAI", type = "password", help = "Se vazio, usa modo Simulação")
        st.divider()
        st.info("💡 **Dica:** Use a aba 'Formulário' para testes rápidos e 'Editor JSON' para payloads complexos.")
        #st.divider()

    # Abas
    tab_json, tab_form, tab_upload = st.tabs(["**💻 Editor JSON**", "**📝 Formulário Completo**", " **📂 Upload Arquivo**"])

    # --- LÓGICA DE INICIALIZAÇÃO ---
    if 'json_input_content' not in st.session_state:
        default_json = {
            "numeroProcesso": "0004587-00.2021.4.05.8100",
            "classe": "Execução Fiscal", 
            "orgaoJulgador": "Vara Federal 1",
            "ultimaDistribuicao": datetime.now().isoformat(), 
            "assunto": "Tributário", 
            "segredoJustica": False, 
            "justicaGratuita": True,
            "siglaTribunal": "TRF5", 
            "esfera": "Federal",
            "valorCondenacao": 50000.00,
            "documentos": [], 
            "movimentos": [],
            "honorarios": {}
        }
        st.session_state['json_input_content'] = json.dumps(default_json, indent = 3, ensure_ascii = False)
    
    # Inicializa contador de execuções para corrigir bug de cache do editor
    if 'run_id' not in st.session_state:
        st.session_state['run_id'] = 0

    # --- ABA 1: EDITOR JSON ---
    with tab_json:
        txt_input = st_ace(
            value = st.session_state['json_input_content'],
            language = "json",
            show_gutter = True,
            theme = "solarized_dark",
            auto_update = True,
            height = 400,
            font_size = 16,
            key = "editor_entrada"
        )

        if txt_input != st.session_state['json_input_content']:
            st.session_state['json_input_content'] = txt_input
        
        if st.button("🚀 Analisar JSON", type = 'primary', use_container_width = True):
            st.session_state['analisar_clicado'] = True

    # --- ABA 1: FORMULÁRIO COMPLETO ---
    with tab_form:
        st.markdown("#### 1. Dados Básicos")
        c1, c2 = st.columns(2)
        num_proc = c1.text_input("Número do Processo", value="0001234-56.2023.4.05.8100")
        classe = c2.text_input("Classe Processual", value="Cumprimento de Sentença")
        
        c3, c4 = st.columns(2)
        orgao = c3.text_input("Órgão Julgador", value="19ª VARA FEDERAL - SOBRAL/CE")
        assunto = c4.text_input("Assunto", value="Rural (Art. 48/51)")

        c5, c6 = st.columns(2)
        sigla = c5.text_input("Sigla Tribunal", value="TRF5")
        esfera = c6.selectbox("Esfera", ["Federal", "Estadual", "Trabalhista"])

        st.markdown("#### 2. Valores e Status")
        c7, c8, c9 = st.columns(3)
        val_cond = c7.number_input("Valor Condenação (R$)", value=50000.0, step=1000.0)
        segredo = c8.checkbox("Segredo de Justiça", value=False)
        justica_grat = c9.checkbox("Justiça Gratuita", value=True)

        st.markdown("#### 3. Documentação Essencial")
        docs_selecionados = st.multiselect(
            "Selecione os documentos presentes nos autos:",
            [
                "Sentença de Mérito",
                "Certidão de Trânsito em Julgado",
                "Planilha de Cálculos",
                "Requisição (RPV/Precatório)",
                "Substabelecimento sem Reserva (Simulação de Erro)"
            ],
            default=[]
        )

        st.markdown("#### 4. Honorários (Opcional)")
        h1, h2, h3 = st.columns(3)
        hon_contrat = h1.number_input("Contratuais (R$)", value=6000.0, min_value=0.0)
        hon_peric = h2.number_input("Periciais (R$)", value=1200.0, min_value=0.0)
        hon_sucumb = h3.number_input("Sucumbenciais (R$)", value=3000.0, min_value=0.0)

        if st.button("🚀 Gerar JSON e Analisar", type="primary", use_container_width=True):
            # Converte form para JSON
            lista_docs = []
            timestamp_base = datetime.now().isoformat()
            
            mapa_docs = {
                "Sentença de Mérito": {"id": "DOC-1", "texto": "Julgo procedente o pedido..."},
                "Certidão de Trânsito em Julgado": {"id": "DOC-2", "texto": "Certifico que a sentença transitou em julgado..."},
                "Planilha de Cálculos": {"id": "DOC-3", "texto": "Planilha de débitos atualizada..."},
                "Requisição (RPV/Precatório)": {"id": "DOC-4", "texto": "Expeça-se ofício requisitório..."},
                "Substabelecimento sem Reserva (Simulação de Erro)": {"id": "DOC-5", "texto": "Substabeleço sem reserva de poderes..."}
            }

            for doc_nome in docs_selecionados:
                doc_info = mapa_docs.get(doc_nome, {"id": "DOC-X", "texto": "Conteúdo genérico"})
                lista_docs.append({
                    "id": doc_info["id"],
                    "nome": doc_nome,
                    "dataHoraJuntada": timestamp_base,
                    "texto": doc_info["texto"]
                })

            payload = {
                "numeroProcesso": num_proc,
                "classe": classe,
                "orgaoJulgador": orgao,
                "ultimaDistribuicao": timestamp_base,
                "assunto": assunto,
                "segredoJustica": segredo,
                "justicaGratuita": justica_grat,
                "siglaTribunal": sigla,
                "esfera": esfera,
                "valorCondenacao": val_cond,
                "valorCausa": val_cond, 
                "documentos": lista_docs,
                "movimentos": [{"dataHora": timestamp_base, "descricao": "Movimento gerado via formulário"}], 
                "honorarios": {
                    "contratuais": hon_contrat,
                    "periciais": hon_peric,
                    "sucumbenciais": hon_sucumb
                }
            }
            
            st.session_state['json_input_content'] = json.dumps(payload, indent = 3, ensure_ascii = False)
            st.session_state['analisar_clicado'] = True
            st.rerun()

    # --- ABA 3: UPLOAD ---
    with tab_upload:
        uploaded_file = st.file_uploader("Carregar arquivo JSON", type=["json", "txt"])
        if uploaded_file is not None:
            try:
                file_content = json.load(uploaded_file)
                formatted_json = json.dumps(file_content, indent = 3, ensure_ascii = False)
                st.success("Arquivo carregado!")
                #st.code(formatted_json, language="json")
                st_ace(
                    value = formatted_json,
                    language = "json",
                    theme = "solarized_dark",
                    wrap = True,
                    readonly = True,
                    show_gutter = True,
                    auto_update = True,
                    font_size = 16,
                    height = 450,
                    key = "preview_upload"
                )
                if st.button("🚀 Analisar Arquivo", type="primary", use_container_width = True):
                    st.session_state['json_input_content'] = formatted_json
                    st.session_state['analisar_clicado'] = True
                    st.rerun()
            except Exception as e:
                st.error(f"Erro: {str(e)}")

with col2:
    st.subheader("Resultado da Análise")

    if 'json_output_content' not in st.session_state:
        st.session_state['json_output_content'] = '{\n   "Decision": "Aguardando a analise do processo ..."\n}'
    
    if st.session_state.get('analisar_clicado'):
        # Incrementa ID para forçar refresh do editor
        st.session_state['run_id'] += 1
        
        if api_key:
            st.toast("Modo REAL: Conectando à OpenAI...", icon = "🔑")
        else:
            st.toast("Modo SIMULAÇÃO: Usando regras locais.", icon = "🛠️")

        logger.info("Usuário clicou no botão 'Analisar Processo'")
        
        try:
            data = json.loads(st.session_state['json_input_content'])
            with st.spinner("Analisando ..."):
                resp = send_request(data, api_key)
            
            with st.sidebar: pass 

            if "error" in resp:
                st.error(resp["error"])
            else:
                status = resp.get("resultado", "").upper()
                
                
                if status == "APPROVED":
                    st.success("✅ **DECISÃO: APROVADO**")
                elif status == "REJECTED":
                    st.error("❌ **DECISÃO: REJEITADO**")
                else:
                    st.warning(f"⚠️ **DECISÃO: {status}**")
                    
                st.info(f"📝 **Justificativa:** {resp.get('justificativa')}")
                
                st.session_state['json_output_content'] = json.dumps(resp, indent = 3, ensure_ascii = False)
                    
        except json.JSONDecodeError:
            st.error("JSON de entrada inválido.")
        
        # Desliga gatilho
        st.session_state['analisar_clicado'] = False

    # Editor de Saída (Usando key dinâmica para evitar cache)
    st.markdown("**Resposta Técnica (JSON):**")

    #st.code(st.session_state['json_output_content'], language = "json", line_numbers = True)

    st_ace(
        value = st.session_state['json_output_content'],
        language = "json",
        theme = "solarized_dark",
        wrap = True,
        readonly = True,        
        show_gutter = True,
        auto_update = True, 
        font_size = 16,
        height = 350,
        key = f"editor_saida_{st.session_state['run_id']}"
    )