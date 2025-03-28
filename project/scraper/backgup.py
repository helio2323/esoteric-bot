consegue refatorar esse codigo sem perder as funcoes dele mas deixando mais legivel em com os retornos de erro melhor aplicado

import requests
import pandas as pd
import json

BASE_URL = 'https://talentai.com.br/api/1.1/obj/esoteric-actions'

from Scraper import Navegador

def fechar_sessao_selenium_grid(session_id, grid_url='https://grid.talentai.com.br/wd/hub'):
    url = f"{grid_url}/session/{session_id}"
    response = requests.delete(url)
    if response.status_code == 200:
        print(f"Sessão {session_id} fechada com sucesso!")
    else:
        print(f"Erro ao fechar a sessão {session_id}: {response.status_code} - {response.text}")

# Exemplo de uso:



# Faz Login
async def login(user, password, url_site, navegador):
  
  await navegador.get(url_site)

  await navegador.sendkeys('ID', 'FLogin', user)
  await navegador.sendkeys('ID', 'FSenha', password)
  
  await navegador.click('XPATH', '/html/body/div/div[2]/form/button')

  await navegador.click('XPATH', '/html/body/table/tbody/tr[2]/th/ul/li[4]')

async def create_data_bubble(json_data, url_bb, operation):
  import json
  url = url_bb
  headers = {
      'Authorization': 'Bearer d523a04a372905b9eb07d90000bee51a',
      'Content-Type': 'application/json'
      }

  if operation == 'create':
    response = requests.request("POST", url, data=json_data, headers=headers)
  if operation == 'update':
    response = requests.request("PATCH", url, data=json_data, headers=headers)

  print(response.text)

  return response

async def format_profile_table(site_id, navegador):
  await navegador.click('ID', 'select')
  await navegador.click('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[3]/th/table/tbody/tr/td[1]/select/option[9]')

  table = await navegador.get_table_element('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[4]/th')

  df = pd.DataFrame(table[0])
  df = df.drop(columns=[1, 2, 3, 6, 7, 9, 11, 13, 14, 15, 16, 17, 18])

  #df = df.drop(columns=colunas_para_excluir)
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
  
  site = site_id
  for index, row in df.iterrows():
    #coloca o id do site na coluna site
    row['SiteVinculado'] = site
    
  
  return df

async def format_payments_table(site_id, navegador):

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

  df = df.drop(df.columns[1], axis=1)
  df = df.drop(df.columns[4], axis=1)
  
  site = site_id
  for index, row in df.iterrows():
    #coloca o id do site na coluna site
    row['SiteVinculado'] = site
    
  
  return df
async def get_sites(site_id):
  url = "https://talentai.com.br/api/1.1/obj/esoteric-site"
  headers = {
      'Authorization': 'Bearer d523a04a372905b9eb07d90000bee51a',
      'Content-Type': 'application/json'
      }
  response = requests.request("GET", url, headers=headers)
  
  response = response.json()

  for st in response['response']['results']:
    if site_id == st['_id']:
      usuario = st['Usuario']
      senha = st['Senha']
      url_site = st['url_site']

  return usuario, senha, url_site

async def get_user_profiles(site_id, url_input='https://talentai.com.br/api/1.1/obj/esoteric-perfis'):
    
    async def consulta_bd_api(cursor, limit):
        url = url_input
        params ={
            "cursor": cursor,
            "limit": limit,
        }
        response = requests.get(url, params=params)
        response_data = response.json()
        return response_data
    
    async def define_cursor(response_data):
        # Aqui, você pode implementar a lógica para determinar o próximo cursor.
        # Por exemplo, se a API retornar o próximo cursor diretamente, você pode simplesmente retorná-lo.
        # Caso contrário, você pode calcular o próximo cursor com base nos dados retornados ou em alguma lógica específica.
        
        # Se a API fornecer o próximo cursor diretamente:
        next_cursor = response_data['response']['cursor'] + response_data['response']['count']
        return next_cursor
        
        # Se você precisar de uma lógica mais complexa para determinar o próximo cursor:
        # return None
    
    async def fetch_all_data():
        cursor = 0
        limit = 100
        all_results = []
        
        while True:
            response_data = await consulta_bd_api(cursor, limit)
            results = response_data['response']['results']
            all_results.extend(results)
            
            remaining = response_data['response']['remaining']
            if remaining > 0:
                cursor = await define_cursor(response_data)
                if cursor is None:
                    break
            else:
                break
        
        return all_results
    
    return await fetch_all_data()

async def get_profile_data(site_id, url_input='https://talentai.com.br/api/1.1/obj/esoteric-dadosperfis'):
    
    async def consulta_bd_api(cursor, limit):
        url = url_input
        params ={
            "cursor": cursor,
            "limit": limit,
        }
        response = requests.get(url, params=params)
        response_data = response.json()
        return response_data
    
    async def define_cursor(response_data):
        # Aqui, você pode implementar a lógica para determinar o próximo cursor.
        # Por exemplo, se a API retornar o próximo cursor diretamente, você pode simplesmente retorná-lo.
        # Caso contrário, você pode calcular o próximo cursor com base nos dados retornados ou em alguma lógica específica.
        
        # Se a API fornecer o próximo cursor diretamente:
        next_cursor = response_data['response']['cursor'] + response_data['response']['count']
        return next_cursor
        
        # Se você precisar de uma lógica mais complexa para determinar o próximo cursor:
        # return None
    
    async def fetch_all_data():
        cursor = 0
        limit = 100
        all_results = []
        
        while True:
            response_data = await consulta_bd_api(cursor, limit)
            results = response_data['response']['results']
            all_results.extend(results)
            
            remaining = response_data['response']['remaining']
            if remaining > 0:
                cursor = await define_cursor(response_data)
                if cursor is None:
                    break
            else:
                break
        
        return all_results
    
    return await fetch_all_data()

async def get_profile_infos(navegador):
    
    async def get_type(id_type):
        element = await navegador.get_elements('ID', id_type)

        for item in element:
            if item.get_attribute('checked'):
                Tipo_Chave = item.get_attribute('value')
                return Tipo_Chave

    def remover_formatacao_cpf(cpf):
        # Remove caracteres indesejados
        cpf = cpf.replace(".", "").replace("-", "")
        return cpf
    
    def remover_formatacao_telefone(telefone):
    # Remove caracteres indesejados
        telefone = telefone.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        telefone = '+55' + telefone
        return telefone

    if await get_type('Conta_Tipo') == 'C':
        tp_conta = 'Corrente'
    else:
        tp_conta = 'Poupanca'

    element_chavepix = await navegador.element_get_text('ID', 'PIX')
    element_banco = await navegador.element_get_text('ID', 'Conta_Banco')
    element_agencia = await navegador.element_get_text('ID', 'Conta_Agencia')
    elemet_conta = await navegador.element_get_text('ID', 'Conta_Numero')
    element_favorecido = await navegador.element_get_text('ID', 'Conta_Favorecido')
    element_tipodechave = await get_type('PIXTipo')
    element_tipodeconta = tp_conta

    chavepix = ''

    try:   
        if element_tipodechave == 'CPF':
            chavepix = remover_formatacao_cpf(element_chavepix.get_attribute("value"))
        elif element_tipodechave == 'Telefone':
            chavepix = remover_formatacao_telefone(element_chavepix.get_attribute("value"))
        else:
            chavepix = element_chavepix.get_attribute("value")
    except:
        chavepix = None
    print('Chave PIX: ', chavepix, 'ChaveNaoformatada: ', element_chavepix.get_attribute("value"))   
    
    json_input = json.dumps({
        "ChavePix": chavepix,
        "Banco": element_banco.get_attribute("value"),
        "Agencia": element_agencia.get_attribute("value"),
        "Conta": elemet_conta.get_attribute("value"),
        "Favorecido": element_favorecido.get_attribute("value"),
        "TiposDeChaves": element_tipodechave,
        "TipoDeConta": element_tipodeconta,
                
            })
    return json_input

async def update_percent(action_id, percent):
    if percent == 5 or percent == 10 or percent == 15 or percent == 20 or percent == 25 or percent == 30 or percent == 35 or percent == 40 or percent == 45 or percent == 50 or percent == 55 or percent == 60 or percent == 65 or percent == 70 or percent == 75 or percent == 80 or percent == 85 or percent == 90 or percent == 95 or percent == 100:
        percent = int(percent)
        url = f'{BASE_URL}/{action_id[0]}'
        json_update = json.dumps({"Progresso": percent})
        response = await create_data_bubble(json_update, url, 'update')
        print(response.status_code)

async def verf_infos_profile(user_id, json_input, present_data):

    json_input_data = json.loads(json_input)

    for chave, valor in json_input_data.items():
        try:
            if valor != '':
                present_value = present_data[chave]
                if chave not in present_data:
                    
                    return 'False'
                elif present_data[chave] != valor:
                    
                    return 'False'
        except:
            continue

#FUNCAO PRINCIPAL QUE VAI CHAMAR AS DEMAIS --------------------------------------------------------
async def check_profiles(site_id, action_id=None):
    navegador = Navegador()
    
    import json

    usuario, senha, url_site = await get_sites(site_id) #necessario deixar como parametro
    
    await login(usuario, senha, url_site, navegador)
    #busca o site no bubble
    
    table = await format_profile_table(site_id, navegador)

    response = await get_user_profiles(site_id)

    site_id_to_match = site_id

    response_ids = [int(item['ID']) for item in response if item['SiteVinculado'] == site_id_to_match]


    for index, row in table.iterrows():

        max_items = len(table)

        percentage = int(index / max_items * 100)

        if int(row['ID']) in response_ids:
            print('Item already exists')
            print(f'Progress: {percentage}%')
            await update_percent(action_id, percentage)
        else:
            print(f'Progress: {percentage}%')
            await update_percent(action_id, percentage)
            print('Item nao existe')
            json_row = json.dumps({
            "ID": row['ID'],
            "Nome": row['Nome'],
            "Link": row['Link'],
            "CPF": row['CPF'],
            "SiteVinculado": row['SiteVinculado'],
            #"Site": row['Site'],
            })

            print(json_row)
            resp_ = await create_data_bubble(json_row, 'https://talentai.com.br/api/1.1/obj/esoteric-perfis', 'create')
            
            if resp_.status_code == 400:
                print('Verifique os dados que estao sendo imputados, tem inconsistencia')
                break
    
    await navegador.click('XPATH', '/html/body/table/tbody/tr[1]/td/table/tbody/tr/th[2]/div/div/a[1]')

    await navegador.close() 

async def update_profile_infos(site_id, atualiza_dados, action_id=None):

    async def update_perc(action_id, percent):
        if percent == 5 or percent == 10 or percent == 15 or percent == 20 or percent == 25 or percent == 30 or percent == 35 or percent == 40 or percent == 45 or percent == 50 or percent == 55 or percent == 60 or percent == 65 or percent == 70 or percent == 75 or percent == 80 or percent == 85 or percent == 90 or percent == 95 or percent == 100:
            percent = int(percent)
            url = f'{BASE_URL}/{action_id[0]}'
            json_update = json.dumps({"Progresso": percent})
            response = await create_data_bubble(json_update, url, 'update')
            print(response.status_code)

    #### ETAPA 1 ######

    #Pegar a lista de perfisi do site la no bubble, precisa DEIXAR SOMENTE OS DADOS DO SITE QUE VAMOS VERIFICAR
    profilesData = await get_user_profiles(site_id)
    profilesData= [item for item in profilesData if item.get('SiteVinculado') == site_id]

    print('---------------------------------------')
    print(site_id, atualiza_dados, action_id)
    print(f'Quantidade de perfis no site: {len(profilesData)}')
    print('---------------------------------------')

    #Pegar todos os dados dos perfis la no site do bubble, DEIXAR SOMENTE OS DADOS DO SITE QUE VAMOS VERIFICAR
    detailsData = await get_profile_data(site_id)

    #Definir variavel para fazer a contagem percentual do progresso

    # inicar o navegador
    navegador = Navegador()

    #Fazer Login no site ESOTERICO
    usuario, senha, url_site = await get_sites(site_id)
    await login(usuario, senha, url_site, navegador)


    #### ETAP 2 ####

    details_ids = {detail['_id'] for detail in detailsData}

    max_count = len(profilesData)
    countPercent = 0
  
    for profile in profilesData:

        dados = profile.get('Dados')
        
        if dados in details_ids:
            if atualiza_dados[0] == 'True':
                print('----------------------------------')
                print(f'Dados serão atualizados ', atualiza_dados )
                #print(f"Updating {dados} in detailsData")
                url = f"{url_site}PG_Atendentes/{profile['Link']}"
                #armazena em uma variavel a linha encontrada
                itemDetail = next(item for item in detailsData if item['_id'] == dados)

                #abre o navegador e acessa a url
                await navegador.get(url)
                websiteProfileInfos = await get_profile_infos(navegador)

                #verifica se os dados do perfil são iguais aos dados do detalhe
                verf = await verf_infos_profile(dados, websiteProfileInfos, itemDetail)

                if verf == 'False':
                    url = f'https://talentai.com.br/api/1.1/obj/esoteric-dadosperfis/{dados}'
                    response = await create_data_bubble(websiteProfileInfos, url, 'update')
                    print('Resposta: ', response.status_code)
                    
        else:

            url = f"{url_site}PG_Atendentes/{profile['Link']}"

            #abre o navegador e acessa a url
            await navegador.get(url)
            websiteProfileInfos = await get_profile_infos(navegador)
            
            print('Inserindo dados do perfil')
            url = 'https://talentai.com.br/api/1.1/obj/esoteric-dadosperfis'
            response = await create_data_bubble(websiteProfileInfos, url, 'create')
            dados_id = response.json().get('id')
            print(response.status_code)

            if response.status_code == 201:
                print('Atualizando dados do perfil')
                url = f'https://talentai.com.br/api/1.1/obj/esoteric-perfis/{profile["_id"]}'
                json_dados = json.dumps({"Dados": dados_id, "DadosPerfil": 'True'})
                response_perfil = await create_data_bubble(json_dados, url, 'update')
                print('Resposta: ', response_perfil.status_code, response.status_code)
        
        countPercent += 1
        percentage = int(countPercent / max_count * 100)
        print(f'Progress: {percentage}%')
        print(f'ACTION ID: {action_id}')
        await update_perc(action_id, percentage)

    await navegador.click('XPATH', '/html/body/table/tbody/tr[1]/td/table/tbody/tr/th[2]/div/div/a[1]')
    await navegador.close()

    return {"status": 200}



import json
import traceback

async def get_payments_profiles(site_id, fechamento, action_id=None):
    print("Iniciando get_payments_profiles")
    navegador = Navegador()
    session_id = await navegador.get_session_id()
    
    try:
        print("Obtendo dados do usuário")
        json_data = await get_user_profiles(site_id)
        usuario, senha, url_site = await get_sites(site_id)
        
        print("Realizando login")
        await login(usuario, senha, url_site, navegador)
        
        url_fechamento = url_site + '/PG_Atendentes/Pg.Fechamento.php'
        print(f"Acessando URL de fechamento: {url_fechamento}")
        await navegador.get(url_fechamento)
        
        print("Formatando tabela de pagamentos")
        table = await format_payments_table(site_id, navegador)

        async def converter_credito_para_float(valor):
            import re
            try:
                valor = valor.replace('R$ ', '').strip()
                if '.' in valor and ',' in valor:
                    valor = valor.replace('.', '').replace(',', '.')
                elif '.' in valor and valor.count('.') == 1:
                    pass
                else:
                    valor = valor.replace(',', '.')
                
                numeros = re.findall(r'-?\d+\.?\d*', valor)
                if not numeros:
                    return None
                return float(numeros[0])
            except Exception as e:
                print(f"Erro ao converter crédito: {e}")
                return None
        
        table_size = len(table)
        table_updated = 0
        
        print("Convertendo valores de crédito para float")
        for index, row in table.iterrows():
            row['Creditos'] = await converter_credito_para_float(row['Creditos'])
        
        print("Obtendo pagamentos do usuário")
        response_payments = await get_user_profiles(site_id, 'https://talentai.com.br/api/1.1/obj/esoteric-pagamentos')
        
        max_count = len(table)
        countPercent = 0
        
        for index, row in table.iterrows():
            countPercent += 1
            percentage = int(countPercent / max_count * 100)
            print(f'Progresso: {percentage}%')
            print(f'ACTION ID: {action_id}')
            await update_percent(action_id, percentage)
            
            for obj in json_data:
                if site_id in obj['SiteVinculado'] and obj['ID'] == row['ID']:
                    payment = True
                    try:
                        dados_id = obj['Dados']
                    except KeyError:
                        dados_id = None
                    
                    for payments in response_payments:
                        print(f"Processando pagamento: {payments}")  # Exibir o objeto para depuração

                        perfil = payments.get('Perfil')
                        fechamento_pagamento = payments.get('Fechamento')

                        if perfil is None:
                            print("Erro: Chave 'Perfil' não encontrada no objeto payments")
                            continue

                        if fechamento_pagamento is None:
                            print("Erro: Chave 'Fechamento' não encontrada no objeto payments")
                            continue

                        print(f"Comparando: {perfil} == {obj['_id']} e {fechamento_pagamento} == {fechamento}")

                        if perfil == obj['_id'] and fechamento_pagamento == fechamento:
                            payment = False
                            print("🔄 Atualizando pagamento existente")

                            json_payments = json.dumps({
                                "Creditos": row['Creditos'],
                                "Status": 'Pendente',
                                "Site": obj['SiteVinculado'],
                                "Favorecido": dados_id
                            })

                            url_payments = f'https://talentai.com.br/api/1.1/obj/esoteric-pagamentos/{payments["_id"]}'
                            print(f"Enviando requisição para {url_payments} com payload: {json_payments}")

                            try:
                                response = await create_data_bubble(json_payments, url_payments, 'update')
                                print(f"✅ Resposta da API: {response.status_code}")
                            except Exception as e:
                                print(f"❌ Erro ao enviar requisição: {e}")

                            table_updated += 1
                            print(f"📊 Tamanho da tabela: {table_size}, Atualizados: {table_updated}")


                    
                    if payment:
                        print("Criando novo pagamento")
                        json_payments = json.dumps({
                            "Fechamento": fechamento,
                            "Creditos": row['Creditos'],
                            "Status": 'Pendente',
                            "Perfil": obj['_id'],
                            "Site": obj['SiteVinculado'],
                            "Favorecido": dados_id
                        })
                        url_payments = 'https://talentai.com.br/api/1.1/obj/esoteric-pagamentos'
                        response = await create_data_bubble(json_payments, url_payments, 'create')
                        print(f"Resposta: {response.status_code}")
                        table_updated += 1
                        print(f"Tamanho da tabela: {table_size}, Atualizados: {table_updated}")
    
    except Exception as e:
        print(f"Erro no processamento: {e}")
        print(traceback.format_exc())
        fechar_sessao_selenium_grid(session_id)
    
    await navegador.click('XPATH', '/html/body/table/tbody/tr[1]/td/table/tbody/tr/th[2]/div/div/a[1]')
    await navegador.close()
    
    print(f"Processo finalizado. Atualizados: {table_updated} de {table_size}")
    return {"tablesize": table_size, "table_updated": table_updated, "status": 200}