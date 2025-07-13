# 🏥 Demo - Agente Médico Vizeval

Demonstração interativa do **Agente Médico Inteligente** usando a SDK Vizeval para avaliação automática de respostas de LLMs na área da saúde.

## 🎯 Sobre a Demo

Esta demonstração foi criada para o **Hackathon Adapta** e mostra como a SDK Vizeval pode ser integrada em um agente médico real, fornecendo:

- **Avaliação automática** de respostas médicas
- **Retry inteligente** quando o score não atinge o threshold
- **Métricas de qualidade** detalhadas
- **Interface web interativa** para demonstração

## 🚀 Funcionalidades

### 🤖 Agente Médico Inteligente
- Análise de casos médicos complexos
- Respostas baseadas em evidências
- Priorização da segurança do paciente
- Adaptação automática baseada na complexidade do caso

### 📊 Avaliação Vizeval
- **Score de qualidade** automático para cada resposta
- **Threshold configurável** por complexidade
- **Retry automático** quando necessário
- **Histórico completo** de tentativas

### 🖥️ Interface Dupla
- **Terminal**: Demo interativa no terminal com Rich
- **Web**: Interface Streamlit para apresentações

## 📦 Instalação

### 1. Clonar o repositório
```bash
git clone <repositorio>
cd vizeval-demo
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Editar .env com suas chaves de API
```

### 4. Configurar arquivo .env
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
VIZEVAL_API_KEY=your-vizeval-api-key-here
VIZEVAL_BASE_URL=http://localhost:8000
```

## 🎮 Como Executar

### 🖥️ Demo Terminal
```bash
python medical_agent.py
```

**Características:**
- Interface rica no terminal
- 3 casos médicos pré-definidos
- Exibição detalhada de métricas
- Histórico de tentativas

### 🌐 Demo Web (Streamlit)
```bash
streamlit run streamlit_demo.py
```

**Características:**
- Interface web interativa
- Casos pré-definidos e personalização
- Configuração dinâmica de parâmetros
- Histórico de análises
- Visualização de métricas

## 📋 Casos de Demonstração

### Caso 1 - Complexidade Baixa
- **Paciente**: CASE-001
- **Sintomas**: Sintomas gripais básicos
- **Threshold**: 0.7
- **Foco**: Orientações gerais

### Caso 2 - Complexidade Alta
- **Paciente**: CASE-002
- **Sintomas**: Dor torácica com fatores de risco
- **Threshold**: 0.9
- **Foco**: Urgência médica

### Caso 3 - Complexidade Média
- **Paciente**: CASE-003
- **Sintomas**: Dor abdominal aguda
- **Threshold**: 0.8
- **Foco**: Diagnóstico diferencial

## 🔧 Configuração da API Local

Para usar com a API Vizeval local (localhost:8000):

1. **Certifique-se de que a API Vizeval está rodando**:
   ```bash
   # No diretório da API Vizeval
   uvicorn vizeval.main:app --host 0.0.0.0 --port 8000
   ```

2. **A demo irá conectar automaticamente** em `http://localhost:8000`

## 📊 Métricas Exibidas

### Métricas Principais
- **Score Final**: Pontuação da resposta (0.0 - 1.0)
- **Status**: Passou/Não passou do threshold
- **Tentativas**: Número total de tentativas
- **Melhor Score**: Maior score obtido

### Informações Detalhadas
- **Feedback**: Comentários específicos da avaliação
- **Histórico**: Evolução dos scores entre tentativas
- **Parâmetros**: Configurações usadas na análise

## 🎨 Capturas de Tela

### Terminal Demo
```
🏥 Análise Médica - Paciente CASE-001
╭─ Sintomas gripais típicos com boa evolução... ─╮
│ ... análise médica detalhada ...                │
╰────────────────────────────────────────────────╯

📊 Métricas de Qualidade Vizeval
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Métrica          ┃ Valor                                                                                          ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Score Final      │ 0.856                                                                                          │
│ Passou Threshold │ ✅ Sim                                                                                         │
│ Total Tentativas │ 1                                                                                              │
│ Melhor Score     │ 0.856                                                                                          │
└──────────────────┴────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Web Demo
- Interface moderna com Streamlit
- Configuração dinâmica de parâmetros
- Métricas visuais em tempo real
- Histórico persistente de análises

## 🔍 Estrutura do Projeto

```
vizeval-demo/
├── medical_agent.py      # Agente médico principal
├── streamlit_demo.py     # Interface web Streamlit
├── requirements.txt      # Dependências Python
├── .env.example         # Exemplo de configuração
├── README.md           # Este arquivo
└── .gitignore         # Arquivos ignorados pelo git
```

## 🛠️ Tecnologias Utilizadas

- **Vizeval SDK**: Avaliação automática de LLMs
- **OpenAI API**: Geração de respostas médicas
- **Streamlit**: Interface web interativa
- **Rich**: Interface terminal avançada
- **Python-dotenv**: Gerenciamento de variáveis

## 📈 Casos de Uso

### Para Desenvolvedores
- Exemplo de integração da SDK Vizeval
- Padrões de implementação de agentes médicos
- Configuração de thresholds adaptativos

### Para Demonstrações
- Interface amigável para apresentações
- Casos médicos realistas
- Métricas claras de qualidade

### Para Pesquisa
- Análise de comportamento de retry
- Comparação de thresholds
- Histórico de melhorias

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é parte da demonstração do Hackathon Adapta.

## 🆘 Suporte

Para dúvidas sobre a demo:
- Abra uma issue no GitHub
- Entre em contato com a equipe Vizeval

---

**🚀 Desenvolvido para o Hackathon Adapta**
**💡 Mostrando o futuro da avaliação de IA na saúde** 