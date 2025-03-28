import requests
import pandas as pd
import json
import traceback

BASE_URL = 'https://talentai.com.br/api/1.1/obj/esoteric-actions'
AUTH_HEADERS = {
    'Authorization': 'Bearer d523a04a372905b9eb07d90000bee51a',
    'Content-Type': 'application/json'
}

from Scraper import Navegador


def fechar_sessao_selenium_grid(session_id, grid_url='https://grid.talentai.com.br/wd/hub'):
    """
    Fecha a sessão do Selenium Grid.
    """
    url = f"{grid_url}/session/{session_id}"
    response = requests.delete(url)
    if response.status_code == 200:
        print(f"Sessão {session_id} fechada com sucesso!")
    else:
        print(f"Erro ao fechar a sessão {session_id}: {response.status_code} - {response.text}")


async def login(user, password, url_site, navegador):
    """
    Realiza o login no site.
    """
    try:
        await navegador.get(url_site)
        await navegador.sendkeys('ID', 'FLogin', user)
        await navegador.sendkeys('ID', 'FSenha', password)
        await navegador.click('XPATH', '/html/body/div/div[2]/form/button')
        await navegador.click('XPATH', '/html/body/table/tbody/tr[2]/th/ul/li[4]')
    except Exception as e:
        print(f"Erro no login: {e}")


async def create_data_bubble(json_data, url_bb, operation):
    """
    Cria ou atualiza dados no Bubble.
    """
    try:
        if operation == 'create':
            response = requests.request("POST", url_bb, data=json_data, headers=AUTH_HEADERS)
        elif operation == 'update':
            response = requests.request("PATCH", url_bb, data=json_data, headers=AUTH_HEADERS)
        else:
            raise ValueError("Operação inválida. Use 'create' ou 'update'.")
        print(response.text)
        return response
    except Exception as e:
        print(f"Erro na operação {operation} na URL {url_bb}: {e}")


async def format_profile_table(site_id, navegador):
    """
    Formata a tabela de perfis extraída do site e retorna um DataFrame com os dados filtrados.
    """
    try:
        await navegador.click('ID', 'select')
        await navegador.click('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[3]/th/table/tbody/tr/td[1]/select/option[9]')
        table = await navegador.get_table_element('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[4]/th')
        df = pd.DataFrame(table[0])
        # Remoção de colunas indesejadas
        colunas_excluir = [1, 2, 3, 6, 7, 9, 11, 13, 14, 15, 16, 17, 18]
        df = df.drop(columns=colunas_excluir)
        df = df.rename(columns={
            0: 'ID',
            4: 'Nome',
            5: 'Link',
            8: 'CPF',
            10: 'Creditos',
            12: 'Status',
            19: 'SiteVinculado',
        })
        df = df.drop(df.index[0])
        # Adiciona o id do site na coluna 'SiteVinculado'
        df['SiteVinculado'] = site_id
        return df
    except Exception as e:
        print(f"Erro ao formatar a tabela de perfis: {e}")


async def format_payments_table(site_id, navegador):
    """
    Formata a tabela de pagamentos extraída do site e retorna um DataFrame com os dados processados.
    """
    try:
        table = await navegador.get_table_element('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/th')
        df = pd.DataFrame(table[0])
        df = df.rename(columns={
            0: 'ID',
            2: 'Nome',
            3: 'Link',
            4: 'CPF',
            6: 'Creditos',
        })
        df = df.drop(df.index[0])
        # Remove colunas desnecessárias
        df.drop(df.columns[[1, 4]], axis=1, inplace=True)
        df['SiteVinculado'] = site_id
        return df
    except Exception as e:
        print(f"Erro ao formatar a tabela de pagamentos: {e}")


async def get_sites(site_id):
    """
    Consulta a API para obter as informações do site e retorna usuário, senha e URL.
    """
    try:
        url = "https://talentai.com.br/api/1.1/obj/esoteric-site"
        response = requests.get(url, headers=AUTH_HEADERS)
        response_json = response.json()
        for st in response_json['response']['results']:
            if site_id == st['_id']:
                return st['Usuario'], st['Senha'], st['url_site']
        raise ValueError("Site não encontrado para o id informado.")
    except Exception as e:
        print(f"Erro ao obter dados do site: {e}")


async def get_user_profiles(site_id, url_input='https://talentai.com.br/api/1.1/obj/esoteric-perfis'):
    """
    Consulta a API para obter todos os perfis de usuário e retorna uma lista de resultados.
    """
    async def consulta_bd_api(cursor, limit):
        params = {"cursor": cursor, "limit": limit}
        response = requests.get(url_input, params=params, headers=AUTH_HEADERS)
        return response.json()

    async def define_cursor(response_data):
        # Calcula o próximo cursor com base nos dados retornados
        return response_data['response']['cursor'] + response_data['response']['count']

    async def fetch_all_data():
        cursor, limit = 0, 100
        all_results = []
        while True:
            response_data = await consulta_bd_api(cursor, limit)
            results = response_data['response']['results']
            all_results.extend(results)
            if response_data['response']['remaining'] > 0:
                cursor = await define_cursor(response_data)
            else:
                break
        return all_results

    return await fetch_all_data()


async def get_profile_data(site_id, url_input='https://talentai.com.br/api/1.1/obj/esoteric-dadosperfis'):
    """
    Consulta a API para obter os dados dos perfis e retorna uma lista de resultados.
    """
    async def consulta_bd_api(cursor, limit):
        params = {"cursor": cursor, "limit": limit}
        response = requests.get(url_input, params=params, headers=AUTH_HEADERS)
        return response.json()

    async def define_cursor(response_data):
        return response_data['response']['cursor'] + response_data['response']['count']

    async def fetch_all_data():
        cursor, limit = 0, 100
        all_results = []
        while True:
            response_data = await consulta_bd_api(cursor, limit)
            results = response_data['response']['results']
            all_results.extend(results)
            if response_data['response']['remaining'] > 0:
                cursor = await define_cursor(response_data)
            else:
                break
        return all_results

    return await fetch_all_data()


async def get_profile_infos(navegador):
    """
    Obtém informações do perfil a partir dos elementos da página.
    """
    async def get_type(id_type):
        elements = await navegador.get_elements('ID', id_type)
        for item in elements:
            if item.get_attribute('checked'):
                return item.get_attribute('value')

    def remover_formatacao_cpf(cpf):
        return cpf.replace(".", "").replace("-", "")

    def remover_formatacao_telefone(telefone):
        telefone = telefone.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        return '+55' + telefone

    try:
        tipo_chave = await get_type('PIXTipo')
        tp_conta = 'Corrente' if await get_type('Conta_Tipo') == 'C' else 'Poupanca'

        element_chavepix = await navegador.element_get_text('ID', 'PIX')
        element_banco = await navegador.element_get_text('ID', 'Conta_Banco')
        element_agencia = await navegador.element_get_text('ID', 'Conta_Agencia')
        element_conta = await navegador.element_get_text('ID', 'Conta_Numero')
        element_favorecido = await navegador.element_get_text('ID', 'Conta_Favorecido')

        # Define o valor da chave PIX com tratamento de formatação
        try:
            raw_valor = element_chavepix.get_attribute("value")
            if tipo_chave == 'CPF':
                chavepix = remover_formatacao_cpf(raw_valor)
            elif tipo_chave == 'Telefone':
                chavepix = remover_formatacao_telefone(raw_valor)
            else:
                chavepix = raw_valor
        except Exception as e:
            print(f"Erro ao obter chave PIX: {e}")
            chavepix = None

        print('Chave PIX:', chavepix, 'Valor original:', element_chavepix.get_attribute("value"))

        json_input = json.dumps({
            "ChavePix": chavepix,
            "Banco": element_banco.get_attribute("value"),
            "Agencia": element_agencia.get_attribute("value"),
            "Conta": element_conta.get_attribute("value"),
            "Favorecido": element_favorecido.get_attribute("value"),
            "TiposDeChaves": tipo_chave,
            "TipoDeConta": tp_conta,
        })
        return json_input
    except Exception as e:
        print(f"Erro ao obter informações do perfil: {e}")


async def update_percent(action_id, percent):
    """
    Atualiza o percentual de progresso na API do Bubble, se o valor for permitido.
    """
    try:
        if percent in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]:
            url = f'{BASE_URL}/{action_id[0]}'
            json_update = json.dumps({"Progresso": int(percent)})
            response = await create_data_bubble(json_update, url, 'update')
            print("Status atualização:", response.status_code)
    except Exception as e:
        print(f"Erro ao atualizar percentual: {e}")


async def verf_infos_profile(user_id, json_input, present_data):
    """
    Verifica se os dados do perfil obtidos do site coincidem com os dados armazenados.
    Retorna 'False' se houver discrepância.
    """
    try:
        json_input_data = json.loads(json_input)
        for chave, valor in json_input_data.items():
            if valor != '':
                if chave not in present_data or present_data[chave] != valor:
                    return 'False'
    except Exception as e:
        print(f"Erro ao verificar informações do perfil: {e}")
    # Se tudo estiver de acordo, pode retornar algo (ou None)
    return 'True'


async def check_profiles(site_id, action_id=None):
    """
    Função principal que verifica e insere perfis não existentes.
    """
    navegador = Navegador()
    try:
        usuario, senha, url_site = await get_sites(site_id)
        await login(usuario, senha, url_site, navegador)
        table = await format_profile_table(site_id, navegador)
        response_profiles = await get_user_profiles(site_id)
        response_ids = [int(item.get('ID', 0)) for item in response_profiles if item.get('SiteVinculado') == site_id]

        total_items = len(table)
        for index, row in table.iterrows():
            percentage = int(index / total_items * 100)
            await update_percent(action_id, percentage)
            if int(row['ID']) in response_ids:
                print('Item already exists. Progress:', f'{percentage}%')
            else:
                print('Item não existe. Progress:', f'{percentage}%')
                json_row = json.dumps({
                    "ID": row['ID'],
                    "Nome": row['Nome'],
                    "Link": row['Link'],
                    "CPF": row['CPF'],
                    "SiteVinculado": row['SiteVinculado'],
                })
                print("Payload:", json_row)
                resp = await create_data_bubble(json_row, 'https://talentai.com.br/api/1.1/obj/esoteric-perfis', 'create')
                if resp.status_code == 400:
                    print('Verifique os dados informados, há inconsistência.')
                    break

        await navegador.click('XPATH', '/html/body/table/tbody/tr[1]/td/table/tbody/tr/th[2]/div/div/a[1]')
    except Exception as e:
        print(f"Erro na verificação de perfis: {e}")
    finally:
        await navegador.close()


async def update_profile_infos(site_id, atualiza_dados, action_id=None):
    """
    Atualiza as informações do perfil, inserindo ou atualizando os dados conforme necessário.
    """
    async def update_perc(percent):
        await update_percent(action_id, percent)

    try:
        profilesData = await get_user_profiles(site_id)
        profilesData = [item for item in profilesData if item.get('SiteVinculado') == site_id]
        print(f'Quantidade de perfis no site: {len(profilesData)}')

        detailsData = await get_profile_data(site_id)
        details_ids = {detail['_id'] for detail in detailsData}

        navegador = Navegador()
        usuario, senha, url_site = await get_sites(site_id)
        await login(usuario, senha, url_site, navegador)

        max_count = len(profilesData)
        count_percent = 0

        for profile in profilesData:
            dados = profile.get('Dados')
            if dados in details_ids:
                if atualiza_dados[0] == 'True':
                    print('Atualizando dados do perfil.')
                    url_profile = f"{url_site}PG_Atendentes/{profile['Link']}"
                    itemDetail = next((item for item in detailsData if item['_id'] == dados), None)
                    if itemDetail:
                        await navegador.get(url_profile)
                        websiteProfileInfos = await get_profile_infos(navegador)
                        if await verf_infos_profile(dados, websiteProfileInfos, itemDetail) == 'False':
                            url_update = f'https://talentai.com.br/api/1.1/obj/esoteric-dadosperfis/{dados}'
                            response = await create_data_bubble(websiteProfileInfos, url_update, 'update')
                            print('Status update:', response.status_code)
            else:
                url_profile = f"{url_site}PG_Atendentes/{profile['Link']}"
                await navegador.get(url_profile)
                websiteProfileInfos = await get_profile_infos(navegador)
                print('Inserindo dados do perfil.')
                url_create = 'https://talentai.com.br/api/1.1/obj/esoteric-dadosperfis'
                response = await create_data_bubble(websiteProfileInfos, url_create, 'create')
                dados_id = response.json().get('id')
                print("Status create:", response.status_code)
                if response.status_code == 201:
                    url_perfil = f'https://talentai.com.br/api/1.1/obj/esoteric-perfis/{profile["_id"]}'
                    json_dados = json.dumps({"Dados": dados_id, "DadosPerfil": 'True'})
                    response_perfil = await create_data_bubble(json_dados, url_perfil, 'update')
                    print('Status atualização do perfil:', response_perfil.status_code)
            count_percent += 1
            percentage = int(count_percent / max_count * 100)
            print(f'Progresso: {percentage}% | ACTION ID: {action_id}')
            await update_perc(percentage)

        await navegador.click('XPATH', '/html/body/table/tbody/tr[1]/td/table/tbody/tr/th[2]/div/div/a[1]')
    except Exception as e:
        print(f"Erro na atualização de informações do perfil: {e}")
    finally:
        await navegador.close()
    return {"status": 200}


async def get_payments_profiles(site_id, fechamento, action_id=None):
    """
    Processa os pagamentos dos perfis, atualizando ou inserindo conforme necessário.
    Evita erros de chave ausente e converte corretamente os valores de crédito.
    """
    print("Iniciando get_payments_profiles")
    navegador = Navegador()
    session_id = await navegador.get_session_id()
    table_updated = 0

    try:
        # Obtém os perfis dos usuários
        json_profiles = await get_user_profiles(site_id)
        usuario, senha, url_site = await get_sites(site_id)
        print("Realizando login")
        await login(usuario, senha, url_site, navegador)

        # Acessa a URL de fechamento
        url_fechamento = url_site + '/PG_Atendentes/Pg.Fechamento.php'
        print(f"Acessando URL de fechamento: {url_fechamento}")
        await navegador.get(url_fechamento)

        # Formata a tabela de pagamentos
        table = await format_payments_table(site_id, navegador)

        # Função para converter valor de crédito para float
        async def converter_credito_para_float(valor):
            import re
            try:
                valor = valor.replace('R$ ', '').strip()
                if '.' in valor and ',' in valor:
                    valor = valor.replace('.', '').replace(',', '.')
                elif ',' in valor:
                    valor = valor.replace(',', '.')
                numeros = re.findall(r'-?\d+\.?\d*', valor)
                return float(numeros[0]) if numeros else None
            except Exception as e:
                print(f"Erro ao converter crédito: {e}")
                return None

        # Atualiza cada valor de crédito no DataFrame
        for index, row in table.iterrows():
            valor_convertido = await converter_credito_para_float(row['Creditos'])
            table.at[index, 'Creditos'] = valor_convertido

        # Obtém os pagamentos já existentes
        response_payments = await get_user_profiles(site_id, 'https://talentai.com.br/api/1.1/obj/esoteric-pagamentos')

        max_count = len(table)
        count_percent = 0

        for index, row in table.iterrows():
            count_percent += 1
            percentage = int(count_percent / max_count * 100)
            print(f'Progresso: {percentage}% | ACTION ID: {action_id}')
            await update_percent(action_id, percentage)

            # Para cada perfil, utiliza .get() para evitar KeyError em "SiteVinculado"
            for obj in json_profiles:
                site_vinculado = obj.get('SiteVinculado', '')
                if site_vinculado and site_id in site_vinculado and obj.get('ID') == row['ID']:
                    payment_exists = False
                    dados_id = obj.get('Dados', None)

                    # Percorre os pagamentos existentes para verificar se já há registro para o perfil
                    for payment in response_payments:
                        perfil = payment.get('Perfil')
                        fechamento_pagamento = payment.get('Fechamento')
                        if perfil is None or fechamento_pagamento is None:
                            print("Erro: dados de pagamento incompletos.")
                            continue

                        print(f"Comparando: {perfil} == {obj.get('_id')} e {fechamento_pagamento} == {fechamento}")
                        if perfil == obj.get('_id') and fechamento_pagamento == fechamento:
                            payment_exists = True
                            print("Atualizando pagamento existente")
                            json_payments = json.dumps({
                                "Creditos": row['Creditos'],
                                "Status": 'Pendente',
                                "Site": obj.get('SiteVinculado'),
                                "Favorecido": dados_id
                            })
                            url_payments = f'https://talentai.com.br/api/1.1/obj/esoteric-pagamentos/{payment.get("_id")}'
                            try:
                                response = await create_data_bubble(json_payments, url_payments, 'update')
                                print("Status update pagamento:", response.status_code)
                            except Exception as e:
                                print(f"Erro ao atualizar pagamento: {e}")
                            table_updated += 1
                            break

                    if not payment_exists:
                        print("Criando novo pagamento")
                        json_payments = json.dumps({
                            "Fechamento": fechamento,
                            "Creditos": row['Creditos'],
                            "Status": 'Pendente',
                            "Perfil": obj.get('_id'),
                            "Site": obj.get('SiteVinculado'),
                            "Favorecido": dados_id
                        })
                        url_payments = 'https://talentai.com.br/api/1.1/obj/esoteric-pagamentos'
                        response = await create_data_bubble(json_payments, url_payments, 'create')
                        print("Status create pagamento:", response.status_code)
                        table_updated += 1

    except Exception as e:
        print(f"Erro no processamento dos pagamentos: {e}")
        print(traceback.format_exc())
        fechar_sessao_selenium_grid(session_id)
    finally:
        await navegador.click('XPATH', '/html/body/table/tbody/tr[1]/td/table/tbody/tr/th[2]/div/div/a[1]')
        await navegador.close()

    print(f"Processo finalizado. Atualizados: {table_updated} de {len(table)}")
    return {"tablesize": len(table), "table_updated": table_updated, "status": 200}
