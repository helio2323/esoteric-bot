import requests
import pandas as pd

from Scraper import Navegador


# Faz Login
async def login(user, password, url_site, navegador):
  
  await navegador.get(url_site)

  await navegador.sendkeys('ID', 'FLogin', user)
  await navegador.sendkeys('ID', 'FSenha', password)
  
  await navegador.click('XPATH', '/html/body/div/div[2]/form/button')

  await navegador.click('XPATH', '/html/body/table/tbody/tr[2]/th/ul/li[4]')

async def create_data_bubble(json_data):
  import json
  url = 'https://consium.com.br/version-test/api/1.1/obj/esoteric-perfis'
  headers = {
      'Authorization': 'Bearer d523a04a372905b9eb07d90000bee51a',
      'Content-Type': 'application/json'
      }

  
  response = requests.request("POST", url, data=json_data, headers=headers)

  print(response.text)

  return response

async def format_profile_table(site_id, navegador):
  await navegador.click('ID', 'select')
  await navegador.click('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[3]/th/table/tbody/tr/td[1]/select/option[9]')

  table = await navegador.get_table_element('XPATH', '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[4]/th')

  df = pd.DataFrame(table[0])

  df = df.rename(columns={
    0: 'ID',
    1: 'Nome',
    2: 'Link',
    3: 'CPF',
    4: 'Creditos',
    5: 'Status',
    6: 'SiteVinculado',
  })

  df = df.drop(df.index[0])

  df = df.iloc[:, :7]
  site = site_id
  for index, row in df.iterrows():
    #coloca o id do site na coluna site
    row['SiteVinculado'] = site
    
  
  return df

async def get_sites(site_id):
  url = "https://consium.com.br/version-test/api/1.1/obj/esoteric-site"
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

async def get_user_profiles(site_id):
    
    async def consulta_bd_api(cursor, limit):
        url = "https://consium.com.br/version-test/api/1.1/obj/esoteric-perfis"
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

#FUNCAO PRINCIPAL QUE VAI CHAMAR AS DEMAIS --------------------------------------------------------
async def check_profiles(site_id):
    navegador = Navegador()
    
    import json

    usuario, senha, url_site = await get_sites(site_id) #necessario deixar como parametro
    
    await login(usuario, senha, url_site, navegador)
    #busca o site no bubble
    
    table = await format_profile_table(site_id, navegador)

    response = await get_user_profiles('1713480487576x673188887945805800')

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
            resp_ = await create_data_bubble(json_row)
            
            if resp_.status_code == 400:
                print('Verifique os dados que estao sendo imputados, tem inconsistencia')
                break

    await navegador.close()        

