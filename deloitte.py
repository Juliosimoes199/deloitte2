from google.adk.agents import Agent
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt # Importar Matplotlib
import seaborn as sns # Importar Seaborn
import os
import dotenv

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


def create_adk_components():
    # Inicializa o agente uma vez
    root_agent = Agent(
        name = "my_tool_agent",
    #model="gemini-2.0-flash-exp",
    model= "gemini-1.5-pro",
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
    tools=[get_time, get_weekday, get_user_data, add_user, get_user_analytics, describe, generate_age_distribution_chart],
    )
    # Inicializa o serviço de sessão uma vez
    session_service = InMemorySessionService() # Mudar para um persistente em produção!
    # Inicializa o runner uma vez
    adk_runner = Runner(
        agent=root_agent,
        app_name="OSAPICARE",
        session_service=session_service
    )
    return adk_runner, session_service

# Componentes ADK acessíveis globalmente ou através de um singleton pattern
# No Flask, você pode inicializá-los quando a aplicação inicia, ou usar o Flask-SQLAlchemy para gerenciar o escopo de requisição.
# Para um exemplo simples:
ADK_RUNNER, ADK_SESSION_SERVICE = create_adk_components()

# Em uma rota Flask:
@app.route('/chat', methods=['POST'])
async def chat(): # Você precisará de ASGI ou rodar async com threads/subprocessos
    user_message = request.json.get('message')
    email = request.json.get('email') # Você precisaria de uma forma de identificar o usuário real
    senha = request.json.get('senha')
    user_id = request.json.get("user_id") # Você precisaria de uma forma de identificar o usuário real
    session_id = request.json.get("session_id") # Você precisaria de uma forma de gerenciar sessões por usuário
    user_message += f".email do paciente: {email}, senha do paciente: {senha}"

    # Lógica para criar/obter sessão ADK e rodar o agente
    existing_session = await ADK_SESSION_SERVICE.get_session(app_name="OSAPICARE", user_id=user_id, session_id=session_id)
    if not existing_session:
        await ADK_SESSION_SERVICE.create_session(app_name="OSAPICARE", user_id=user_id, session_id=session_id)

    new_user_content = types.Content(role='user', parts=[types.Part(text=user_message)])

    response_text = "Agente não produziu uma resposta final."
    async for event in ADK_RUNNER.run_async(user_id=user_id, session_id=session_id, new_message=new_user_content):
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
            break
    return jsonify({"response": response_text})

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)  # Ajuste o host e a porta conforme necessário
