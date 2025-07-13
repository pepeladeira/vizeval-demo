"""
Agente Médico Inteligente com Avaliação Vizeval
Demo do Hackathon Adapta
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from vizeval import OpenAI, VizevalConfig, Evaluator

console = Console()

@dataclass
class MedicalCase:
    """Representa um caso médico"""
    patient_id: str
    symptoms: str
    medical_history: str
    complexity_level: str
    expected_focus: List[str] = None

class MedicalAgent:
    """Agente médico inteligente com avaliação automática via Vizeval"""
    
    def __init__(self, openai_api_key: str, vizeval_api_key: str, vizeval_base_url: str = "http://localhost:8000"):
        self.console = Console()
        
        # Configurar Vizeval para usar API local
        self.vizeval_config = VizevalConfig(
            api_key=vizeval_api_key,
            evaluator=Evaluator.MEDICAL,
            threshold=0.85,
            max_retries=5,
            base_url=vizeval_base_url,
            metadata={"agent": "medical_demo", "version": "1.0"}
        )
        
        # Configurar cliente OpenAI com Vizeval
        self.client = OpenAI(
            api_key=openai_api_key,
            vizeval_config=self.vizeval_config,
        )
        
        console.print("🏥 [bold green]Agente Médico Vizeval inicializado![/bold green]")
        console.print(f"🔗 API Vizeval: {vizeval_base_url}")
    
    def analyze_case(self, case: MedicalCase) -> Dict[str, Any]:
        """Analisa um caso médico usando o agente com avaliação Vizeval"""
        console.print(f"\n🔍 [bold blue]Analisando caso: {case.patient_id}[/bold blue]")
        
        # Configurar threshold baseado na complexidade
        thresholds = {"low": 0.7, "medium": 0.8, "high": 0.9}
        
        # Atualizar configuração dinamicamente
        self.client.set_vizeval_config({
            "api_key": self.vizeval_config.api_key,
            "evaluator": "medical",
            "threshold": thresholds[case.complexity_level],
            "max_retries": 3,
            "base_url": self.vizeval_config.base_url,
            "metadata": {"patient_id": case.patient_id, "complexity": case.complexity_level}
        })
        
        system_prompt = "Você é uma assistente médica de mentira. Você irá mentir sobre tudo para casos de teste. MINTA!"
        
        user_prompt = f"""
Caso Médico - Paciente {case.patient_id}

SINTOMAS: {case.symptoms}
HISTÓRICO: {case.medical_history}

Forneça análise médica incluindo:
1. Avaliação dos sintomas
2. Possíveis hipóteses diagnósticas  
3. Exames necessários
4. Orientações de cuidado
5. Quando buscar atendimento médico
"""
        
        try:
            with console.status("[bold green]Gerando análise médica..."):
                result = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
            
            return {
                "patient_id": case.patient_id,
                "analysis": result.final_response.choices[0].message.content,
                "quality_metrics": {
                    "final_score": result.final_evaluation.score,
                    "passed_threshold": result.passed_threshold,
                    "total_attempts": result.total_attempts,
                    "best_score": result.best_score,
                    "feedback": result.final_evaluation.feedback
                },
                "attempt_history": [
                    {"attempt": a.attempt_number, "score": a.score, "feedback": a.feedback}
                    for a in result.attempts
                ]
            }
            
        except Exception as e:
            console.print(f"❌ [bold red]Erro: {str(e)}[/bold red]")
            return {
                "patient_id": case.patient_id,
                "analysis": f"Erro na análise: {str(e)}",
                "quality_metrics": {"error": str(e)},
                "attempt_history": []
            }
    
    def display_results(self, results: Dict[str, Any]):
        """Exibe os resultados da análise"""
        # Análise médica
        analysis_panel = Panel(
            Markdown(results["analysis"]),
            title=f"🏥 Análise Médica - {results['patient_id']}",
            border_style="blue"
        )
        console.print(analysis_panel)
        
        # Métricas de qualidade
        if "error" not in results["quality_metrics"]:
            metrics = results["quality_metrics"]
            
            metrics_table = Table(title="📊 Métricas de Qualidade Vizeval")
            metrics_table.add_column("Métrica", style="cyan")
            metrics_table.add_column("Valor", style="green")
            
            metrics_table.add_row("Score Final", f"{metrics['final_score']:.3f}")
            metrics_table.add_row("Passou Threshold", "✅ Sim" if metrics['passed_threshold'] else "❌ Não")
            metrics_table.add_row("Total Tentativas", str(metrics['total_attempts']))
            metrics_table.add_row("Melhor Score", f"{metrics['best_score']:.3f}" if metrics['best_score'] else "N/A")
            
            console.print(metrics_table)

def create_sample_cases() -> List[MedicalCase]:
    """Casos médicos de exemplo"""
    return [
        MedicalCase(
            patient_id="CASE-001",
            symptoms="Febre 38.5°C há 2 dias, dor de cabeça, dores musculares, fadiga, congestão nasal.",
            medical_history="Paciente saudável, 28 anos, sem comorbidades.",
            complexity_level="low"
        ),
        MedicalCase(
            patient_id="CASE-002", 
            symptoms="Dor no peito tipo pressão há 3h, irradiando para braço esquerdo, sudorese, náusea.",
            medical_history="Homem 55 anos, hipertenso, diabético, fumante 30 anos.",
            complexity_level="high"
        ),
        MedicalCase(
            patient_id="CASE-003",
            symptoms="Dor abdominal quadrante inferior direito há 12h, náuseas, febre baixa 37.8°C.",
            medical_history="Mulher 22 anos, sem cirurgias prévias.",
            complexity_level="medium"
        ),
        MedicalCase(
            patient_id="CASE-004",
            symptoms="Fadiga intensa há 4 meses, perda de peso 12kg não intencional, sudorese noturna profusa, dor lombar irradiando para pernas, lesões cutâneas múltiplas, tontura postural, dispneia aos esforços, febre baixa intermitente, sangramento gengival, equimoses espontâneas, alteração do hábito intestinal, confusão mental ocasional.",
            medical_history="Paciente 72 anos, ex-fumante (50 maços/ano), etilista crônico, exposição ocupacional a benzeno e amianto por 45 anos, histórico familiar de leucemia (irmão) e câncer de pulmão (pai), diabetes mellitus tipo 2 descompensado, insuficiência renal crônica estágio 3, cirrose hepática Child-Pugh B, em uso de múltiplas medicações com interações conhecidas.",
            complexity_level="very_high"
        ),
        MedicalCase(
            patient_id="CASE-005",
            symptoms="Sintomas inespecíficos há 6 meses, mal-estar geral, dor de cabeça ocasional, cansaço, alterações do humor.",
            medical_history="Paciente 45 anos, sem informações detalhadas disponíveis no prontuário.",
            complexity_level="extreme"
        )
    ]

def main():
    """Função principal da demonstração"""
    console.print(Panel.fit("🏥 [bold blue]DEMO - Agente Médico Vizeval[/bold blue] 🤖", border_style="blue"))
    console.print("[yellow]Hackathon Adapta - Avaliação Inteligente de LLMs na Saúde[/yellow]\n")
    
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    vizeval_key = os.getenv("VIZEVAL_API_KEY")
    
    if not openai_key or not vizeval_key:
        console.print("❌ [bold red]Configure as variáveis OPENAI_API_KEY e VIZEVAL_API_KEY[/bold red]")
        return
    
    # Inicializar agente
    agent = MedicalAgent(
        openai_api_key=openai_key,
        vizeval_api_key=vizeval_key,
        vizeval_base_url="http://localhost:8000"
    )
    
    # Casos de exemplo
    cases = create_sample_cases()
    console.print(f"\n📋 [bold cyan]Carregados {len(cases)} casos médicos[/bold cyan]\n")
    
    # Processar cada caso
    for i, case in enumerate(cases, 1):
        console.print(f"\n{'='*60}")
        console.print(f"[bold white]CASO {i}/{len(cases)}[/bold white]")
        console.print(f"{'='*60}")
        
        # Detalhes do caso
        case_table = Table(title=f"📋 {case.patient_id}")
        case_table.add_column("Campo", style="cyan")
        case_table.add_column("Informação", style="white")
        
        case_table.add_row("ID", case.patient_id)
        case_table.add_row("Complexidade", case.complexity_level.upper())
        case_table.add_row("Sintomas", case.symptoms)
        case_table.add_row("Histórico", case.medical_history)
        
        console.print(case_table)
        
        # Analisar e exibir resultados
        results = agent.analyze_case(case)
        agent.display_results(results)
        
        if i < len(cases):
            console.print("\n[dim]Pressione Enter para continuar...[/dim]")
            input()
    
    console.print(f"\n🎉 [bold green]Demo concluída![/bold green]")

if __name__ == "__main__":
    main() 