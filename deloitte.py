import requests
import json
import google.generativeai as genai
import asyncio
import streamlit as st
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService # Para protótipo, usar persistente em prod
from google.adk.runners import Runner
from google.genai import types
import os
import warnings
import logging
import dotenv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt # Importar Matplotlib
import seaborn as sns
# --- Configurações Iniciais ---
dotenv.load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key) # osapi vm


idade = [30, 25, 40, 28, 35, 22, 50, 19, 20]
nome = ["joao", "maria", "carlos", "ana", "pedro", "sofia", "ricardo", "Julio", "Davida"]
cidade = ["Luanda", "Sumbe", "Benguela", "Lubango", "Luanda", "Benguela", "Cabinda", "Sumbe", "Luanda"]
profissao = ["Engenheiro", "Designer", "Médico", "Professora", "Arquiteto", "Estudante", "Empresário", "Designer", "Engenheiro"]
email = ["joao@example.com", "maria@example.com", "carlos@example.com", "ana@example.com", "pedro@example.com", "sofia@example.com", "ricardo@example.com", "Juliocesar@gmail.com", "David@gmail.com"]

# Dados de exemplo para simular um banco de dados
df = pd.DataFrame(data={"nome": nome, "idade":idade, "cidade": cidade, "profissao":profissao, "email": email})


def get_user_data(nome_usuario: str):
    """
    Retorna os dados de um usuário específico do banco de dados.
    Args:
        nome_usuario (str): O nome do usuário a ser consultado (case-insensitive).
    Returns:
        dict: Um dicionário com os dados do usuário ou uma mensagem de erro se não encontrado.
    """
    # Filtra o DataFrame pelo nome do usuário (convertendo para minúsculas para comparação)
    user_name_lower = df[df.nome.str.lower() == nome_usuario.lower()]

    if user_name_lower.empty:
        # Retorna um dicionário de erro se o usuário não for encontrado
        return {"error": f"Usuário '{nome_usuario}' não encontrado."}
    else:
        # Se um usuário for encontrado, pega a primeira (e única) linha
        # e converte para um dicionário simples
        return user_name_lower.iloc[0].to_dict()

def add_user(nome: str, idade: int, email:str, cidade: str, profissao: str):
    """
    Adiciona um novo usuário ao banco de dados.
    Args:
        nome (str): O nome do novo usuário.
        idade (int): A idade do novo usuário.
        cidade (str): A cidade do novo usuário.
        email (str): O email do novo usuário.
        profissao (str): A profissão do novo usuário
    Returns:
        dict: Um dicionário indicando o status da operação.
    """
    global df # Permite que a função modifique o DataFrame global

    # Verifica se o email já existe no banco de dados (comparação case-insensitive)
    if email.lower() in df.email.str.lower().values:
        return {"status": "error", "message": f"Email '{email}' já existe no banco de dados."}
    
    # Cria um novo DataFrame com os dados do usuário (convertendo nome e email para minúsculas)
    new_user_df = pd.DataFrame([[nome.lower(), idade, email.lower(), cidade, profissao]], 
                               columns=["nome", "idade", "email", "cidade", "profissao"])
    
    # Concatena o novo usuário ao DataFrame global
    df = pd.concat([df, new_user_df], ignore_index=True)
    return {"status": "success", "message": f"Usuário '{nome}' adicionado com sucesso!"}


def get_time():
    """Retorna a hora atual."""
    now = datetime.now()
    return now.strftime("%H:%M:%S")

def get_weekday():
    """Retorna o dia da semana atual."""
    now = datetime.now()
    return now.strftime("%A")  # Retorna o nome completo do dia da semana, como "Monday", "Tuesday", etc.


def get_user_analytics(cidade: str, profissao: str):
    """
    Retorna todos os usuários que pertencem à mesma cidade e têm as mesmas profissões.
    Args:
        cidade (str): Filtra usuários por cidade.
        profissao (str): Filtra usuários por profissão.
    Returns:
        dict: Um dicionário com a lista de usuários ou uma mensagem de erro.
    """
    # Filtra usuários por cidade e profissão (comparação case-insensitive)
    filtered_users = df[((df.cidade.str.lower() == cidade.lower()) & 
                         (df.profissao.str.lower() == profissao.lower()))]

    if filtered_users.empty:
        return {"users": [], "message": f"Nenhum usuário encontrado na cidade '{cidade}' com a profissão '{profissao}'."}
    else:
        # Retorna uma lista de dicionários, onde cada dicionário é um usuário
        return {"users": filtered_users.to_dict(orient="records")}

def describe():
    """
    Retorna a descrição do meu banco de dados
    returns:
        dict: Um dicionário com a descrição estatística do DataFrame.

    """
    return df.describe().to_json(orient="index")

def generate_age_distribution_chart():
    """
    Gera um histograma da distribuição de idades dos usuários e retorna o objeto da figura para plotagem.
    Returns:
        matplotlib.figure.Figure or None: O objeto da figura do gráfico se for bem-sucedido, caso contrário, None.
    """
    if df.empty or 'idade' not in df.columns:
        # Em vez de retornar um dicionário de erro, retornamos None e o chamador (no Streamlit)
        # pode exibir uma mensagem de erro apropriada.
        st.error("Dados de usuários ou coluna 'idade' não encontrados para gerar o gráfico.")
        return None

    # Cria a figura e os eixos
    fig, ax = plt.subplots(figsize=(10, 6))

    # Cria o histograma com KDE usando os eixos criados
    sns.histplot(df['idade'], kde=True, bins=5, color='skyblue', ax=ax)

    # Define os títulos e rótulos para os eixos do gráfico
    ax.set_title('Distribuição de Idades dos Usuários')
    ax.set_xlabel('Idade')
    ax.set_ylabel('Número de Usuários')
    ax.grid(axis='y', alpha=0.75) # Adiciona grade no eixo Y

    plt.tight_layout() # Ajusta o layout para evitar cortes
    
    # Não salvamos o gráfico, apenas o retornamos
    return fig


@st.cache_resource
def agent_osapi():
    root_agent = Agent(
        name = "osapicare",
        #model="gemini-2.0-flash-exp",
        model= "gemini-2.0-flash-exp",
        # Combine a descrição e as instruções aqui, ou adicione um novo campo se o ADK suportar explicitamente instruções do sistema
        description="""
        Você é um agente que retorna a hora atual, o dia atual da semana, os dados de um usuário, adiciona um novo usuário, mostra a estatística agregada ao usuário, a descrição do meu banco de dados.
        Você deve usar a ferramenta 'get_time' para obter a hora atual.
        Você deve usar a ferramenta 'get_weekday' para obter o dia da semana atual.
        VocÊ deve usar a ferramenta 'get_user_data' para obter os dados de um usuário específico do banco de dados.
        Você deve usar a ferramenta 'add_user' para adicionar um novo usuário ao banco de dados.
        Você deve usar a ferramenta 'get_user_analytics' para fazer a filtração da cidade e profissão dos usuários dentro do banco de dados.
        Você deve usar a ferramenta 'describe' para obter a descrição de como esta o meu banco de dados.
        Você deve usar a ferramenta 'generate_age_distribution_chart' para gerar um gráfico de histograma.
        """,
        tools=[get_time, get_weekday, get_user_data, add_user, get_user_analytics, describe, generate_age_distribution_chart],  # Certifique-se de que essas ferramentas estejam definidas corretamente
        # Se houver um campo para instruções específicas do modelo, ele seria algo como 'system_instruction' ou 'model_instructions'
        # system_instruction="""Siga as diretrizes de segurança e bem-estar do usuário.""" # Exemplo, verifique a documentação do ADK
    )
    print(f"Agente '{root_agent.name}'.")
    return root_agent

root_agent = agent_osapi()

APP_NAME = "OSAPICARE"


@st.cache_resource
def get_session_service():
    """
    Cria e retorna o serviço de sessão.
    O InMemorySessionService gerencia o histórico da conversa automaticamente para a sessão.
    """
    return InMemorySessionService()

session_service = get_session_service()

@st.cache_resource
def get_adk_runner(_agent, _app_name, _session_service):
    """
    Cria e retorna o runner do ADK.
    """
    adk_runner = Runner(
        agent=_agent,
        app_name=_app_name,
        session_service=_session_service
    )
    print("ADK Runner criado globalmente.")
    return adk_runner

# Passa o agente de notas para o runner
adk_runner = get_adk_runner(root_agent, APP_NAME, session_service) # Passando notes_agent

## Aplicação Streamlit

st.title("🩺 Gerenciador laboratorial") # Título da aplicação atualizado

# Inicializa o histórico de chat no st.session_state se ainda não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
if user_message := st.chat_input("Olá! Como posso ajudar você a gerenciar suas actividades hoje?"):
    # Adiciona a mensagem do usuário ao histórico do Streamlit
    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    # Define user_id e session_id.
    user_id = "streamlit_usuario"
    session_id = "default_streamlit_usuario"

    try:
        # Garante que a sessão exista no ADK
        # O InMemorySessionService manterá o estado da sessão.
        # Não é ideal tentar criar uma sessão que já existe, mas para InMemorySessionService,
        # get_session pode ser suficiente para verificar a existência.
        existing_session = asyncio.run(session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id))
        if not existing_session:
            asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id))
            print(f"Sessão '{session_id}' criada para '{user_id}'.")
        else:
            print(f"Sessão '{session_id}' já existe para '{user_id}'.")

        # A nova mensagem do usuário a ser enviada ao agente
        new_user_content = types.Content(role='user', parts=[types.Part(text=user_message)])

        async def run_agent_and_get_response(current_user_id, current_session_id, new_content):
            """
            Executa o agente e retorna a resposta final.
            """
            response_text = "Agente não produziu uma resposta final." 
            async for event in adk_runner.run_async(
                user_id=current_user_id,
                session_id=current_session_id,
                new_message=new_content,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate:
                        response_text = f"Agente escalou: {event.error_message or 'Sem mensagem específica.'}"
                    break 
            return response_text

        # Executa a função assíncrona e obtém o resultado
        response = asyncio.run(run_agent_and_get_response(user_id, session_id, new_user_content))

        # Adiciona a resposta do agente ao histórico do Streamlit
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    except Exception as e:
        st.error(f"Erro ao processar a requisição: {e}")
        st.session_state.messages.append({"role": "assistant", "content": f"Desculpe, ocorreu um erro: {e}"})
