# Fazer o Deploy desse agente em um servidor Flask com Google ADK
from flask import Flask, request, jsonify
import requests
import json
import asyncio
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.agents import Agent
import google.generativeai as genai
import os
import dotenv

dotenv.load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

app = Flask(__name__)



def registar_paciente(numero_identificacao:str, nome_completo:str, data_nascimento:str, contacto_telefonico:str, id_sexo:int, email:str, senha:str):
    """
    Regista um novo paciente na unidade hospitalar.
    Args:
        numero_identificacao (str): O numero de bilhete do paciente.
        nome_completo (str): O nome completo do paciente.
        data_nascimento (str): A data de nascimento do paciente (ex: 1990-01-01).
        contacto_telefonico (int): O contacto telefonico do paciente.
        id_sexo (int): O ID do sexo do paciente (1 para masculino, 2 para feminino).
        email (str): O email do paciente.
        senha (str): A senha do paciente.

    Returns:
        dict: O JSON da resposta se o login for bem-sucedido e as informações do novo paciente como o id e um dicionário de mais algumas informações uteis, Erro caso contrário.
    """
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "senha": senha
    }

    try:
        url = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/auth/local/signin"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx

        #return response.json()
        resposta_login = response.json()
        access_token = resposta_login.get("access_token")
        health_unit_ref = resposta_login.get("health_unit_ref")
        url_acesso = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/pacients"
        headers = {
            "Authorization": f"Bearer {access_token}",
                   }
        data = {
            "numero_identificacao": numero_identificacao,
            "nome_completo": nome_completo,
            "data_nascimento": data_nascimento,
            "contacto_telefonico": contacto_telefonico,
            "id_sexo": id_sexo
        }
        requisicao = requests.post(url_acesso, headers=headers, json=data)
        return {"Status": requisicao.status_code, "Requisição": requisicao.json()}

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        print(f"Resposta do servidor: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Erro de Timeout: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro inesperado ocorreu: {req_err}")
        return None
    
def criar_agendamento(id_paciente:str, id_tipo_exame:int, data_agendamento:str, hora_agendamento:str, email:str, senha:str):
    """
    Faz uma requisição de login para a URL fornecida com as credenciais.

    Args:
        id_paciente (str): O ID do paciente.
        id_tipo_exame (int): O ID do tipo de exame(ex: 1 para Covide-19, 2 para Hepatite B...).
        data_agendamento (str): A data do agendamento no formato 'YYYY-MM-DD'.
        hora_agendamento (str): A hora do agendamento no formato 'HH:MM'.

    Returns:
        dict: retorna um dicionário com o status da requisição e a resposta JSON, ou None em caso de erro.
    """
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "senha": senha
    }

    try:

        url = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/auth/local/signin"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx

        #return response.json()
        resposta_login = response.json()
        access_token = resposta_login.get("access_token")
        health_unit_ref = resposta_login.get("health_unit_ref")
        url_acesso = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/schedulings/set-schedule"
        headers = {
            "Authorization": f"Bearer {access_token}",
                   }
        data = {
            "id_paciente": id_paciente,
            "id_unidade_de_saude": health_unit_ref,
            "exames_paciente": [
        {
            "id_tipo_exame": id_tipo_exame,
            "data_agendamento": data_agendamento,
            "hora_agendamento": hora_agendamento
        }]

        }
        requisicao = requests.post(url_acesso, headers=headers, json=data)
        return {"Status": requisicao.status_code, "Requisição": requisicao.json()}

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        print(f"Resposta do servidor: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Erro de Timeout: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro inesperado ocorreu: {req_err}")
        return None
    
def get_exames(email:str, senha:str):
    """
    Faz uma requisição para obter o id correspondente ao tipo de exame, o nome dos exames e descrição dos tipos de exames disponíveis.
    Essa função é uma ferramenta interna que nunca deve ser exposta ao usuário, apenas utilizada para extrair informações como o id correspondente ao tipo de exame para o preencher a variável id_tipo_exame na função criar_agendamento.
    Args:
        email (str): O email do usuário.
        senha (str): A senha do usuário.
    Returns:
        dict: retorna um dicionário com o status da requisição e a resposta JSON, ou None em caso de erro.
    """
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "senha": senha
    }

    try:
        url = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/auth/local/signin"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx

        #return response.json()
        resposta_login = response.json()
        access_token = resposta_login.get("access_token")
        health_unit_ref = resposta_login.get("health_unit_ref")
        url_acesso = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/exam-types"
        headers = {
            "Authorization": f"Bearer {access_token}",
                   }

        requisicao = requests.get(url_acesso, headers=headers)
        return {"Status": requisicao.status_code, "Requisição": requisicao.json()}

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        print(f"Resposta do servidor: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Erro de Timeout: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro inesperado ocorreu: {req_err}")
        return None
    

def get_pacientes(email:str, senha:str):
    """
    Faz uma requisição para obter os dados pessoais dos pacientes, como nome, id do paciente, sexo, número telefónico e data de nascimento.
    Essa função é uma ferramenta interna que nunca deve ser exposta ao usuário, apenas utilizada para extrair informações necessárias no momento.
    
    Args:
        email (str): O email do usuário.
        senha (str): A senha do usuário.
    
    Returns:
        dict: retorna um dicionário com o status da requisição e a resposta JSON, ou None em caso de erro.
    """
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "senha": senha
    }

    try:
        url = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/auth/local/signin"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx

        #return response.json()
        resposta_login = response.json()
        access_token = resposta_login.get("access_token")
        health_unit_ref = resposta_login.get("health_unit_ref")
        url_acesso = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/pacients"
        headers = {
            "Authorization": f"Bearer {access_token}",
                   }

        requisicao = requests.get(url_acesso, headers=headers)
        return {"Status": requisicao.status_code, "Requisição": requisicao.json()}

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        print(f"Resposta do servidor: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Erro de Timeout: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro inesperado ocorreu: {req_err}")
        return None

def get_user():
    """
    Obtém o link da página de pacientes da plataforma OsapiCare.
    Essa função deve ser usada para acessar a lista de pacientes registrados na unidade hospitalar.
    Args:
        None
    Returns:
        str: O link da página de pacientes. 
    """
    return {"Link":"https://akin-lis-app-web.vercel.app/akin/patient"}
    

def editar_exames(id_exame:str, id_agendamento:str, data_agendamento:None, hora_agendamento:None, status:None, status_pagamento:None, email:str, senha:str):
    """
    Edita um agendamento de exame existente.
    Esta função permite atualizar a data, hora, status do agendamento e status do pagamento de um exame agendado.
    Os parâmetros são usados para modificar as informações do agendamento existente e não são todos obrigatório.
    O id_agendamento e id_exame são obrigatórios, enquanto os restantes podem ser deixadas como estão se não forem fornecidas novas informações.
    
    Args:
        id_agendamento (str): O ID do agendamento a ser editado.
        data_agendamento (str): A nova data do agendamento no formato 'YYYY-MM-DD'.
        hora_agendamento (str): A nova hora do agendamento no formato 'HH:MM'.
        status (str): O novo status do agendamento (ex: "pendente", "confirmado", "cancelado").
        status_pagamento (str): O novo status do pagamento (ex: "pendente", "pago", "cancelado").
        id_exame (int): O ID do tipo de exame a ser editado (ex: 1 para Covide-19, 2 para Hepatite B...).
        email (str): O email do usuário.
        senha (str): A senha do usuário.
    
    Returns:
        dict: Retorna um dicionário com o status da requisição e a resposta JSON, ou None em caso de erro.
    """
    if not id_agendamento:
        raise ValueError("O id_agendamento é obrigatório para editar um agendamento.")
    if not data_agendamento and not hora_agendamento and not status and not status_pagamento:
        raise ValueError("Pelo menos um dos parâmetros data_agendamento, hora_agendamento, status ou status_pagamento deve ser fornecido para editar o agendamento.")

    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "senha": senha
    }

    try:

        url = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/auth/local/signin"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx

        #return response.json()
        resposta_login = response.json()
        access_token = resposta_login.get("access_token")
        health_unit_ref = resposta_login.get("health_unit_ref")
        url_acesso = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/exams/" + id_exame
        headers = {
            "Authorization": f"Bearer {access_token}",
                   }
        data = {
            "id_agendamento": id_agendamento,
            "data_agendamento": data_agendamento,
            "hora_agendamento": hora_agendamento,
            "status": status,
            "status_pagamento": status_pagamento,
        }
        requisicao = requests.post(url_acesso, headers=headers, json=data)
        return {"Status": requisicao.status_code, "Requisição": requisicao.json()}

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        print(f"Resposta do servidor: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Erro de Timeout: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro inesperado ocorreu: {req_err}")
        return None
    
    

def lista_exames_por_pacientes(id_paciente:str, email:str, senha:str):
    """
    Obtém a lista de exames agendados para um paciente específico.
    Esta função permite consultar os exames agendados para um paciente com base no ID do paciente fornecido.
    Essa função é útil para verificar os exames agendados, seus status e outras informações relevantes sobre os agendamentos do paciente.
    Essa função é uma ferramenta interna que nunca deve ser exposta ao usuário, apenas utilizada para extrair informações necessárias no momento.
    
    Args:
        id_paciente (str): O ID do paciente.
        email (str): O email do usuário.
        senha (str): A senha do usuário.

    Returns:
        dict: Retorna um dicionário com o status da requisição e a resposta JSON, ou None em caso de erro.
    """

    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "senha": senha
    }

    try:

        url = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/auth/local/signin"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx

        #return response.json()
        resposta_login = response.json()
        access_token = resposta_login.get("access_token")
        health_unit_ref = resposta_login.get("health_unit_ref")
        url_acesso = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/exams/patient/" + id_paciente
        headers = {
            "Authorization": f"Bearer {access_token}",
                   }
        requisicao = requests.get(url_acesso, headers=headers)
        return {"Status": requisicao.status_code, "Requisição": requisicao.json()}

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        print(f"Resposta do servidor: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Erro de Timeout: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro inesperado ocorreu: {req_err}")
        return None



def create_adk_components():
    # Inicializa o agente uma vez
    root_agent = Agent(
        name="osapicare",
        model="gemini-2.0-flash-exp",
        description="""
        Você é um **assistente inteligente e prestativo especializado em gestão de dos processos laboratorias da plataforma OsapiCare, você torna as actividades laboratoriais mas simples e fácil de ser realizado**.
        Você pode ajudar os usuários a **registar pacientes, agendar exames e obter informações sobre tipos de exames disponíveis**.
        Você pode usar as seguintes ferramentas:
        - **registar_paciente**: Registra um novo paciente na unidade hospitalar.
        - **criar_agendamento**: Cria um agendamento de exame para um paciente.
        - **get_exames**: Obtém os tipos de exames disponíveis, incluindo o ID, nome e descrição dos exames para ser usado na criação de novo agendamento.
        - **get_pacientes**: Obtém os dados pessoais dos pacientes, como nome, id do paciente, sexo, número telefónico e data de nascimento, que deveras utilizar quando necessário para extrair alguma informação necessária no momento e nunca mostres aos usuário, essa é uma ferramenta tua interna que nunca deve ser exposta.
        - **get_user**: Obtém o link da página de pacientes da plataforma OsapiCare, que pode ser usado para acessar a lista de pacientes registrados na unidade hospitalar.
        - **editar_exames**: Editar um agendamento de exame existente, permitindo atualizar a data, hora, status do agendamento e status do pagamento de um exame agendado.
        - **lista_exames_por_pacientes**: Obtém a lista de exames agendados para um paciente específico, permitindo consultar os exames agendados, seus status e outras informações relevantes sobre os agendamentos do paciente.
        Você deve sempre usar a ferramenta **get_exames** para obter o ID do tipo de exame antes de criar um agendamento com a ferramenta **criar_agendamento**.
        Você deve sempre usar a ferramenta **lsta_exames_por_pacientes** para ver o id e informações relevantes dos exame de um determinado paciente para poder editar um agendamento de exame existente com a ferramenta **editar_exames**, nunca pergunte o id do agendamento ou id do exame ao usuário, sempre use a ferramenta **lista_exames_por_pacientes** para obter essas informações.
        Você deve sempre usar a ferramenta **get_pacientes** para obter os dados dos pacientes antes de criar um agendamento com a ferramenta **criar_agendamento**, nunca pergunte o id do paciente ao usuário, sempre use a ferramenta **get_pacientes** para obter essas informações.
        Sempre que o usuário quiser agendar um exame, você deve primeiro obter o ID do tipo de exame usando a ferramenta **get_exames** e depois usar o ID do paciente e o ID do tipo de exame para criar o agendamento com a ferramenta **criar_agendamento**, nunca pessa permissão para usar a função **get_exames** sempre use para obter o id do tipo de exame a partir do nome do tipo de exame que o usuário quiser agendar.
        Você deve sempre verificar se o paciente já está registrado antes de criar um agendamento, usando a ferramenta **get_pacientes** para obter os dados dos pacientes.
        Você deve sempre responder de forma clara e concisa, e se não souber a resposta, deve informar o usuário que não tem certeza.
        Se o usuário fizer uma pergunta que não esteja relacionada com a gestão de processos laboratoriais, você deve informar que não pode ajudar com isso.
        """, # Sua descrição completa
        tools=[registar_paciente, criar_agendamento, get_exames, get_pacientes, get_user, editar_exames, lista_exames_por_pacientes],
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