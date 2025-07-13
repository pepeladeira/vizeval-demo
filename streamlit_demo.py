"""
Interface Web Interativa - Agente Médico Unimed
Demo do Hackathon Adapta - Avaliação Inteligente com Vizeval
"""

import streamlit as st
import os
import json
from medical_agent import MedicalAgent, MedicalCase, create_sample_cases
from dotenv import load_dotenv

# Configuração da página
st.set_page_config(
    page_title="Agente Médico Unimed",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para tema Unimed
st.markdown("""
<style>
    /* Tema principal Unimed */
    .main > div {
        background-color: #f8f9fa;
    }
    
    /* Header customizado */
    .unimed-header {
        background: linear-gradient(135deg, #00a651 0%, #7cc142 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .unimed-header h1 {
        color: white !important;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .unimed-header p {
        color: #e8f5e8;
        font-size: 1.1rem;
        margin-bottom: 0;
    }
    
    /* Botões com tema Unimed */
    .stButton > button {
        background-color: #00a651;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #008a44;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 166, 81, 0.3);
    }
    
         /* Métricas personalizadas */
     .metric-container {
         background: white;
         padding: 1.5rem;
         border-radius: 10px;
         border-left: 4px solid #00a651;
         margin: 1rem 0;
         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
     }
    
    /* Sidebar com tema Unimed */
    .css-1d391kg {
        background-color: #f0f8f0;
    }
    
    /* Tabs com tema Unimed */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #e8f5e8;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #00a651;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #00a651;
        color: white;
    }
    
         /* Cards de informação */
     .info-card {
         background: white;
         padding: 1.5rem;
         border-radius: 10px;
         border: 1px solid #e8f5e8;
         margin: 1rem 0;
         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
     }
     
     .info-card h3, .info-card h4 {
         color: #00a651;
         margin-bottom: 1rem;
         font-size: 1.1rem;
         font-weight: 600;
     }
     
     .info-card p, .info-card div {
         margin-bottom: 0.5rem;
         line-height: 1.5;
         color: #333;
     }
     
     .info-card p:last-child, .info-card div:last-child {
         margin-bottom: 0;
     }
    
    /* Logo placeholder */
    .logo-placeholder {
        background: white;
        border: 2px dashed #00a651;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        color: #00a651;
        margin-bottom: 1rem;
    }
    
    /* Footer */
    .footer {
        background: #f0f8f0;
        padding: 2rem;
        border-radius: 10px;
        margin-top: 2rem;
        text-align: center;
        color: #00a651;
    }
</style>
""", unsafe_allow_html=True)

# Carregar variáveis de ambiente
load_dotenv()

def init_session_state():
    """Inicializa o estado da sessão"""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

def create_agent():
    """Cria o agente médico"""
    openai_key = os.getenv("OPENAI_API_KEY")
    vizeval_key = os.getenv("VIZEVAL_API_KEY")
    
    if not openai_key or not vizeval_key:
        st.error("❌ Configure as variáveis OPENAI_API_KEY e VIZEVAL_API_KEY")
        return None
    
    try:
        agent = MedicalAgent(
            openai_api_key=openai_key,
            vizeval_api_key=vizeval_key,
            vizeval_base_url="http://localhost:8000"
        )
        return agent
    except Exception as e:
        st.error(f"❌ Erro ao criar agente: {str(e)}")
        return None

def display_metrics(results):
    """Exibe métricas de qualidade em colunas"""
    if "error" not in results["quality_metrics"]:
        metrics = results["quality_metrics"]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta_text = "Aprovado" if metrics['passed_threshold'] else "Reprovado"
            delta_color = "#00a651" if metrics['passed_threshold'] else "#ff4444"
            st.markdown(f'''
            <div class="metric-container">
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Score Final</div>
                <div style="font-size: 2rem; font-weight: bold; color: #000;">{metrics['final_score']:.3f}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="metric-container">
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Tentativas</div>
                <div style="font-size: 2rem; font-weight: bold; color: #000;">{metrics['total_attempts']}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            best_score_value = f"{metrics['best_score']:.3f}" if metrics['best_score'] else "N/A"
            st.markdown(f'''
            <div class="metric-container">
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Melhor Score</div>
                <div style="font-size: 2rem; font-weight: bold; color: #000;">{best_score_value}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col4:
            status = "✅ Aprovado" if metrics['passed_threshold'] else "❌ Reprovado"
            status_color = "#00a651" if metrics['passed_threshold'] else "#ff4444"
            st.markdown(f'''
            <div class="metric-container">
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Status</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: {status_color};">{status}</div>
            </div>
            ''', unsafe_allow_html=True)

def main():
    # Inicializar estado
    init_session_state()
    
    # Header customizado da Unimed
    st.markdown("""
    <div class="unimed-header">
        <div class="logo-placeholder">
            <h3>🏥 UNIMED</h3>
        </div>
        <h1>Agente Médico Inteligente</h1>
        <p>Powered by Vizeval AI - Avaliação Inteligente de Diagnósticos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para configurações
    with st.sidebar:
        st.markdown("### ⚙️ Configurações do Sistema")
        
        # Logo da Unimed na sidebar
        st.markdown("""
        <div class="logo-placeholder">
            <h4>🏥 UNIMED</h4>
            <small>Sistema de Diagnóstico IA</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Status da API
        st.markdown("#### 🔗 Conexão Vizeval")
        vizeval_url = st.text_input("URL do Vizeval", value="http://localhost:8000")
        
        if st.button("🔄 Conectar Sistema"):
            with st.spinner("Conectando com Vizeval..."):
                st.session_state.agent = create_agent()
                if st.session_state.agent:
                    st.success("✅ Sistema Unimed conectado!")
                else:
                    st.error("❌ Falha na conexão com Vizeval")
        
        # Configurações de avaliação
        st.markdown("#### 📊 Parâmetros de Avaliação")
        threshold = st.slider("Threshold de Qualidade", 0.0, 1.0, 0.8, 0.05)
        max_retries = st.number_input("Máximo de Tentativas", 1, 10, 3)
        
        # Casos de exemplo
        st.markdown("#### 📋 Casos Clínicos")
        sample_cases = create_sample_cases()
        case_names = [f"{case.patient_id} ({case.complexity_level})" for case in sample_cases]
        selected_case_idx = st.selectbox("Selecionar Caso", range(len(case_names)), format_func=lambda x: case_names[x])
    
    # Área principal
    tab1, tab2, tab3 = st.tabs(["🔍 Análise Clínica", "📊 Resultados", "📈 Histórico"])
    
    with tab1:
        st.markdown("## 🔍 Análise de Caso Clínico")
        
        # Usar caso selecionado na sidebar
        selected_case = sample_cases[selected_case_idx]
        
        # Exibir detalhes do caso
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f'''
            <div class="info-card">
                <h4>👤 Informações do Paciente</h4>
                <p><strong>ID:</strong> {selected_case.patient_id}</p>
                <p><strong>Complexidade:</strong> {selected_case.complexity_level.upper()}</p>
                <p><strong>Histórico Médico:</strong></p>
                <p>{selected_case.medical_history}</p>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="info-card">
                <h4>🩺 Sintomas Apresentados</h4>
                <p>{selected_case.symptoms}</p>
            </div>
            ''', unsafe_allow_html=True)
        
        case_to_analyze = selected_case
        
        # Botão de análise
        if st.button("🚀 Executar Análise Médica", type="primary"):
            if not st.session_state.agent:
                st.error("❌ Conecte o sistema Vizeval primeiro na barra lateral")
            elif not case_to_analyze.symptoms.strip():
                st.error("❌ Informe os sintomas do paciente")
            else:
                with st.spinner("🔍 Analisando caso com sistema Unimed..."):
                    # Atualizar configurações do agente
                    st.session_state.agent.client.set_vizeval_config({
                        "api_key": st.session_state.agent.vizeval_config.api_key,
                        "evaluator": "medical",
                        "threshold": threshold,
                        "max_retries": max_retries,
                        "base_url": vizeval_url,
                        "metadata": {"unimed_system": True, "streamlit_demo": True}
                    })
                    
                    # Fazer análise
                    results = st.session_state.agent.analyze_case(case_to_analyze)
                    
                    # Salvar no histórico
                    st.session_state.analysis_history.append(results)
                    
                    # Exibir apenas o resultado da análise médica
                    st.success("✅ Análise Unimed concluída com sucesso!")
                    
                    # Mostrar apenas a análise médica
                    analysis_text = results["analysis"].replace('\n', '<br>')
                    st.markdown(f'''
                    <div class="info-card">
                        <h4>🏥 Diagnóstico Médico Unimed</h4>
                        <div style="white-space: pre-wrap; line-height: 1.6;">{analysis_text}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Informar sobre métricas na aba Resultados
                    st.info("📊 Para ver as métricas de qualidade e avaliação Vizeval, acesse a aba **Resultados**")
    
    with tab2:
        st.markdown("## 📊 Resultados da Análise")
        
        if st.session_state.analysis_history:
            latest_result = st.session_state.analysis_history[-1]
            
            # Métricas principais
            st.markdown("### 📈 Métricas de Qualidade")
            display_metrics(latest_result)
            
            # Histórico de tentativas
            if "attempt_history" in latest_result and len(latest_result["attempt_history"]) > 1:
                st.markdown("### 🔄 Histórico de Tentativas")
                
                attempts_data = []
                for attempt in latest_result["attempt_history"]:
                    attempts_data.append({
                        "Tentativa": attempt["attempt"],
                        "Score": f"{attempt['score']:.3f}" if attempt["score"] else "N/A",
                        "Status": "✅ Aprovado" if attempt["score"] and attempt["score"] >= threshold else "🔄 Retry"
                    })
                
                st.dataframe(attempts_data, use_container_width=True)
            
            # JSON dos resultados
            st.markdown("### 🔧 Dados Técnicos")
            with st.expander("Ver Dados Completos do Vizeval"):
                st.json(latest_result)
        
        else:
            st.info("📝 Nenhuma análise realizada ainda. Vá para a aba 'Análise Clínica' para começar.")
    
    with tab3:
        st.markdown("## 📈 Histórico de Análises")
        
        if st.session_state.analysis_history:
            # Estatísticas gerais
            total_analyses = len(st.session_state.analysis_history)
            avg_score = sum(r["quality_metrics"].get("final_score", 0) for r in st.session_state.analysis_history) / total_analyses
            total_attempts = sum(r["quality_metrics"].get("total_attempts", 0) for r in st.session_state.analysis_history)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Análises", total_analyses)
            with col2:
                st.metric("Score Médio", f"{avg_score:.3f}")
            with col3:
                st.metric("Total de Tentativas", total_attempts)
            
            # Tabela do histórico
            st.markdown("### 📋 Todas as Análises")
            
            history_data = []
            for i, result in enumerate(st.session_state.analysis_history):
                metrics = result["quality_metrics"]
                history_data.append({
                    "#": i + 1,
                    "Paciente": result["patient_id"],
                    "Score": f"{metrics.get('final_score', 0):.3f}",
                    "Status": "✅" if metrics.get('passed_threshold', False) else "❌",
                    "Tentativas": metrics.get('total_attempts', 'N/A')
                })
            
            st.dataframe(history_data, use_container_width=True)
            
            # Botão para limpar histórico
            if st.button("🗑️ Limpar Histórico"):
                st.session_state.analysis_history = []
                st.rerun()
        
        else:
            st.info("📝 Nenhuma análise no histórico ainda.")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <h4>🏥 Sistema Unimed de Diagnóstico Inteligente</h4>
        <p>🤖 <strong>Powered by Vizeval AI</strong> | 🏥 <strong>Hackathon Adapta</strong> | 🚀 <strong>Demo Version 1.0</strong></p>
        <p><small>Avaliação de qualidade em tempo real com tecnologia Vizeval</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 