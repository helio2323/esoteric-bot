import requests
import pandas as pd
import json

from Scraper import Navegador

def fechar_sessao_selenium_grid(session_id, grid_url='https://grid.consium.com.br/wd/hub'):
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
  url = "https://consium.com.br/api/1.1/obj/esoteric-site"
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

async def get_user_profiles(site_id, url_input='https://consium.com.br/api/1.1/obj/esoteric-perfis'):
    
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

    element_dict_chave = {
        "CPF": await navegador.element_get_text('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/th/form/table/tbody/tr[29]/td[2]/input[@value="CPF"]'),
        "CNPJ": await navegador.element_get_text('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/th/form/table/tbody/tr[29]/td[2]/input[@value="CNPJ"]'),
        "Telefone": await navegador.element_get_text('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/th/form/table/tbody/tr[29]/td[2]/input[@value="Telefone"]'),
        "E-mail": await navegador.element_get_text('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/th/form/table/tbody/tr[29]/td[2]/input[@value="E-mail"]'),
        "Chave Aleatória": await navegador.element_get_text('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/th/form/table/tbody/tr[29]/td[2]/input[@value="Chave Aleatória"]')
    }

    elemet_dict_conta = {
        "Conta Corrente": await navegador.element_get_text('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/th/form/table/tbody/tr[38]/td[2]/input[1]'),
        "Poupança": await navegador.element_get_text('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/th/form/table/tbody/tr[38]/td[2]/input[2]')
    }
    def remover_formatacao_cpf(cpf):
        # Remove caracteres indesejados
        cpf = cpf.replace(".", "").replace("-", "")
        return cpf
    
    def remover_formatacao_telefone(telefone):
    # Remove caracteres indesejados
        telefone = telefone.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        telefone = '+55' + telefone
        return telefone

    def get_selected_element(element):
        for key, value in element.items():
            if value:
                if value.is_selected():
                    key_selected = key
                    return key_selected
                else:
                    ...
            else:
                print(f"Nenhum elemento encontrado para '{key}'.")

    element_chavepix = await navegador.element_get_text('ID', 'PIX')
    element_banco = await navegador.element_get_text('ID', 'Conta_Banco')
    element_agencia = await navegador.element_get_text('ID', 'Conta_Agencia')
    elemet_conta = await navegador.element_get_text('ID', 'Conta_Numero')
    element_favorecido = await navegador.element_get_text('ID', 'Conta_Favorecido')
    element_tipodechave = get_selected_element(element_dict_chave)
    element_tipodeconta = get_selected_element(elemet_dict_conta)

    chavepix = ''

    try:
        tipo_chave = element_tipodechave.encode('iso-8859-1').decode('utf-8')
        tipo_conta = element_tipodeconta.encode('iso-8859-1').decode('utf-8')
    except:
        tipo_chave = element_tipodechave
        tipo_conta = element_tipodeconta
    try:   
        if tipo_chave == 'CPF':
            chavepix = remover_formatacao_cpf(element_chavepix.get_attribute("value"))
        elif tipo_chave == 'Telefone':
            chavepix = remover_formatacao_telefone(element_chavepix.get_attribute("value"))
    except:
        chavepix = None
    print('Chave PIX: ', chavepix, 'ChaveNaoformatada: ', element_chavepix.get_attribute("value"))   
    
    json_input = json.dumps({
        "ChavePix": chavepix,
        "Banco": element_banco.get_attribute("value"),
        "Agencia": element_agencia.get_attribute("value"),
        "Conta": elemet_conta.get_attribute("value"),
        "Favorecido": element_favorecido.get_attribute("value"),
        "TiposDeChaves": tipo_chave,
        "TipoDeConta": tipo_conta,
                
            })
    return json_input

#FUNCAO PRINCIPAL QUE VAI CHAMAR AS DEMAIS --------------------------------------------------------
async def check_profiles(site_id):
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
        if int(row['ID']) in response_ids:
            print('Item already exists')
        else:
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
            resp_ = await create_data_bubble(json_row, 'https://consium.com.br/api/1.1/obj/esoteric-perfis', 'create')
            
            if resp_.status_code == 400:
                print('Verifique os dados que estao sendo imputados, tem inconsistencia')
                break
    
    await navegador.click('XPATH', '/html/body/table/tbody/tr[1]/td/table/tbody/tr/th[2]/div/div/a[1]')

    await navegador.close() 

async def update_profile_infos(site_id, atualiza_dados, ):


    navegador = Navegador()
    session_id = navegador.get_session_id()
    json_data = await get_user_profiles(site_id)
    usuario, senha, url_site = await get_sites(site_id)
    await login(usuario, senha, url_site, navegador)

    for item in json_data:
        url = f"{url_site}/PG_Atendentes/{item['Link']}"
        if site_id == item['SiteVinculado']:

          if item['DadosPerfil'] == True:
            if atualiza_dados == 'True':
                
                await navegador.get(url)
                json_input = await get_profile_infos(navegador)
                try:
                    dados_id = item["Dados"]
                except:
                    dados_id = None
                if dados_id != None:
                    print('Atualizando dados do perfil')
                    url = f'https://consium.com.br/api/1.1/obj/esoteric-dadosperfis/{dados_id}' #esta pegando o ID do perfis mas precisa pegar do dadosperfis
                    response = await create_data_bubble(json_input, url, 'update')

                    print('Resposta: ', response.status_code)
          else:
                
            await navegador.get(url)
            json_input = await get_profile_infos(navegador)              

            print('Inserindo dados do perfil')
            url = 'https://consium.com.br/api/1.1/obj/esoteric-dadosperfis'
            response = await create_data_bubble(json_input, url, 'create')
            dados_id = ''
            dados_id = response.json().get('id')
            print(json_input)
            #verificar se dados_id e diferente de vazio
            print(response.status_code)
            if response.status_code == 201:
                print('Atualizando dados do perfil')
                url = f'https://consium.com.br/api/1.1/obj/esoteric-perfis/{item["_id"]}'
                json_dados = json.dumps({"Dados": dados_id, "DadosPerfil": 'True'})
                response_perfil = await create_data_bubble(json_dados, url, 'update')

                print('Resposta: ', response_perfil.status_code, response.status_code)


    await navegador.click('XPATH', '/html/body/table/tbody/tr[1]/td/table/tbody/tr/th[2]/div/div/a[1]')

    await navegador.close()

    return {"status": 200}


async def get_payments_profiles(site_id, fechamento):

    navegador = Navegador()
    session_id = navegador.get_session_id()

    try:
        json_data = await get_user_profiles(site_id)
        usuario, senha, url_site = await get_sites(site_id)
        await login(usuario, senha, url_site, navegador)

        url_fechamento = url_site + '/PG_Atendentes/Pg.Fechamento.php'

        await navegador.get(url_fechamento)

        table = await format_payments_table(site_id, navegador)

        async def converter_credito_para_float(valor):
            import re

            # Remover o prefixo 'R$ ' e substituir ',' por '.'
            valor = valor.replace('R$ ', '').replace(',', '.')

            # Encontrar todos os números na string usando expressão regular
            numeros = re.findall(r'\d+', valor)

            # Concatenar os números encontrados
            valor_concatenado = ''.join(numeros)
            valor_concatenado = float(valor_concatenado)
            valor_concatenado = valor_concatenado / 100
            try:
                # Converter para float
                return float(valor_concatenado)
            except ValueError:
                # Handle the case where the conversion fails
                return None

        #define o tamanho da tabela
        table_size = len(table)
        table_updated = 0

        for index, row in table.iterrows():
        #coloca o id do site na coluna site
            floatCredits = await converter_credito_para_float(row['Creditos'])
            row['Creditos'] = floatCredits

        response_payments = await get_user_profiles(site_id, 'https://consium.com.br/api/1.1/obj/esoteric-pagamentos')

        #redefinir table com somente 3 linhas de daos

        for index, row in table.iterrows():
            for obj in json_data:
                if site_id in obj['SiteVinculado'] and obj['ID'] == row['ID']:
                    payment = True
                    try:
                        dados_id = obj['Dados']
                    except:
                        dados_id = None
                    for payments in response_payments:
                        if payments['Perfil'] == obj['_id'] and payments['Fechamento'] == fechamento:
                            payment = False
                            #atualiza os dados do pagamento
                            json_payments = json.dumps({
                                "Creditos": row['Creditos'],
                                "Status": 'Pendente',
                                "Site": obj['SiteVinculado'],
                                "Favorecido": dados_id
                            })

                            url_payments = f'https://consium.com.br/api/1.1/obj/esoteric-pagamentos/{payments["_id"]}'
                            response = await create_data_bubble(json_payments, url_payments, 'update')

                            table_updated += 1
                            print(table_size, table_updated)
                            
                            print(response.status_code)
                    print('Checando', payment)    
                    if payment == True:

                        json_payments = json.dumps({
                            "Fechamento": fechamento,
                            "Creditos": row['Creditos'],
                            "Status": 'Pendente',
                            "Perfil": obj['_id'],
                            "Site": obj['SiteVinculado'],
                            "Favorecido": dados_id
                        })

                        url_payments = f'https://consium.com.br/api/1.1/obj/esoteric-pagamentos'

                        response = await create_data_bubble(json_payments, url_payments, 'create')

                        print(response.status_code)

                        table_updated += 1
                        print(table_size, table_updated)
                        #Realiza o cadastro dentro da tabela pagamentos
                        #O pagamento deve ter o ano e mes de registro

                        #Vincula o pagamento a um perfil
                        ##print('Item already exists', obj['SiteVinculado'])
                        #Caso o cadastro ja exista faz a atualizacao dos dados
                        pass
    except:
        fechar_sessao_selenium_grid(session_id)    
                        
    await navegador.click('XPATH', '/html/body/table/tbody/tr[1]/td/table/tbody/tr/th[2]/div/div/a[1]')

    await navegador.close()

    print(table_updated, table_size)

    return {"tablesize": table_size, "table_updated": table_updated, "status": 200}