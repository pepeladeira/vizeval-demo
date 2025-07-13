"""
Interface Web Interativa - Agente Médico Vizeval
Demo do Hackathon Adapta
"""

import streamlit as st
import os
import json
from medical_agent import MedicalAgent, MedicalCase, create_sample_cases
from dotenv import load_dotenv

# Configuração da página
st.set_page_config(
    page_title="Agente Médico Vizeval",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            vizeval_base_url="http://localhost:8080"
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
            st.metric(
                label="Score Final",
                value=f"{metrics['final_score']:.3f}",
                delta="Aprovado" if metrics['passed_threshold'] else "Reprovado"
            )
        
        with col2:
            st.metric(
                label="Tentativas",
                value=metrics['total_attempts']
            )
        
        with col3:
            st.metric(
                label="Melhor Score",
                value=f"{metrics['best_score']:.3f}" if metrics['best_score'] else "N/A"
            )
        
        with col4:
            status = "✅ Aprovado" if metrics['passed_threshold'] else "❌ Reprovado"
            st.metric(
                label="Status",
                value=status
            )

def main():
    # Inicializar estado
    init_session_state()
    
    # Header
    st.title("🏥 Agente Médico Vizeval")
    st.markdown("**Demo do Hackathon Adapta** - Avaliação Inteligente de LLMs na Saúde")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Status da API
        st.subheader("🔗 Status da API")
        vizeval_url = st.text_input("URL Vizeval", value="http://localhost:8080")
        
        if st.button("🔄 Conectar Agente"):
            with st.spinner("Conectando..."):
                st.session_state.agent = create_agent()
                if st.session_state.agent:
                    st.success("✅ Agente conectado com sucesso!")
                else:
                    st.error("❌ Falha na conexão")
        
        # Configurações de avaliação
        st.subheader("📊 Parâmetros de Avaliação")
        threshold = st.slider("Threshold Mínimo", 0.0, 1.0, 0.8, 0.05)
        max_retries = st.number_input("Máximo de Tentativas", 1, 10, 3)
        
        # Casos de exemplo
        st.subheader("📋 Casos Pré-definidos")
        sample_cases = create_sample_cases()
        case_names = [f"{case.patient_id} ({case.complexity_level})" for case in sample_cases]
        selected_case_idx = st.selectbox("Selecionar Caso", range(len(case_names)), format_func=lambda x: case_names[x])
    
    # Área principal
    tab1, tab2, tab3 = st.tabs(["🔍 Análise de Caso", "📊 Resultados", "📈 Histórico"])
    
    with tab1:
        st.header("🔍 Análise de Caso Médico")
        
        # Seletor de modo
        mode = st.radio("Modo de Entrada", ["Caso Pré-definido", "Caso Personalizado"])
        
        if mode == "Caso Pré-definido":
            # Usar caso selecionado
            selected_case = sample_cases[selected_case_idx]
            
            # Exibir detalhes do caso
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👤 Informações do Paciente")
                st.write(f"**ID:** {selected_case.patient_id}")
                st.write(f"**Complexidade:** {selected_case.complexity_level.upper()}")
                st.write(f"**Histórico Médico:**")
                st.write(selected_case.medical_history)
            
            with col2:
                st.subheader("🩺 Sintomas Apresentados")
                st.write(selected_case.symptoms)
            
            case_to_analyze = selected_case
            
        else:
            # Caso personalizado
            st.subheader("✏️ Criar Caso Personalizado")
            
            col1, col2 = st.columns(2)
            
            with col1:
                patient_id = st.text_input("ID do Paciente", value="CUSTOM-001")
                complexity = st.selectbox("Complexidade", ["low", "medium", "high"])
                medical_history = st.text_area("Histórico Médico", height=100)
            
            with col2:
                symptoms = st.text_area("Sintomas Apresentados", height=150)
            
            case_to_analyze = MedicalCase(
                patient_id=patient_id,
                symptoms=symptoms,
                medical_history=medical_history,
                complexity_level=complexity,
                expected_focus=[]
            )
        
        # Botão de análise
        if st.button("🚀 Analisar Caso Médico", type="primary"):
            if not st.session_state.agent:
                st.error("❌ Conecte o agente primeiro na barra lateral")
            elif not case_to_analyze.symptoms.strip():
                st.error("❌ Informe os sintomas do paciente")
            else:
                with st.spinner("🔍 Analisando caso médico..."):
                    # Atualizar configurações do agente
                    st.session_state.agent.client.set_vizeval_config({
                        "api_key": st.session_state.agent.vizeval_config.api_key,
                        "evaluator": "medical",
                        "threshold": threshold,
                        "max_retries": max_retries,
                        "base_url": vizeval_url,
                        "metadata": {"streamlit_demo": True}
                    })
                    
                    # Fazer análise
                    results = st.session_state.agent.analyze_case(case_to_analyze)
                    
                    # Salvar no histórico
                    st.session_state.analysis_history.append(results)
                    
                    # Exibir resultados
                    st.success("✅ Análise concluída!")
                    
                    # Mostrar métricas
                    st.subheader("📊 Métricas de Qualidade")
                    display_metrics(results)
                    
                    # Mostrar análise
                    st.subheader("🏥 Análise Médica")
                    st.markdown(results["analysis"])
                    
                    # Feedback da avaliação
                    if "quality_metrics" in results and "feedback" in results["quality_metrics"]:
                        st.subheader("💬 Feedback da Avaliação Vizeval")
                        st.info(results["quality_metrics"]["feedback"])
    
    with tab2:
        st.header("📊 Últimos Resultados")
        
        if st.session_state.analysis_history:
            latest_result = st.session_state.analysis_history[-1]
            
            # Métricas principais
            st.subheader("📈 Métricas de Qualidade")
            display_metrics(latest_result)
            
            # Histórico de tentativas
            if "attempt_history" in latest_result and len(latest_result["attempt_history"]) > 1:
                st.subheader("🔄 Histórico de Tentativas")
                
                attempts_data = []
                for attempt in latest_result["attempt_history"]:
                    attempts_data.append({
                        "Tentativa": attempt["attempt"],
                        "Score": f"{attempt['score']:.3f}" if attempt["score"] else "N/A",
                        "Status": "✅ Aprovado" if attempt["score"] and attempt["score"] >= threshold else "🔄 Retry"
                    })
                
                st.dataframe(attempts_data, use_container_width=True)
            
            # JSON dos resultados
            st.subheader("🔧 Dados Técnicos")
            with st.expander("Ver JSON Completo"):
                st.json(latest_result)
        
        else:
            st.info("📝 Nenhuma análise realizada ainda. Vá para a aba 'Análise de Caso' para começar.")
    
    with tab3:
        st.header("📈 Histórico de Análises")
        
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
            st.subheader("📋 Todas as Análises")
            
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
    st.markdown("---")
    st.markdown("🤖 **Powered by Vizeval SDK** | 🏥 **Hackathon Adapta** | 🚀 **Demo Version 1.0**")

if __name__ == "__main__":
    main() 