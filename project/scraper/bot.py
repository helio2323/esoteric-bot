from scraper import Navegador

navegador = Navegador()

# Faz Login
async def login(user, password):
  await navegador.get('https://www.ciganasdooriente.com.br/gerencial_nfpcBWk2PVYJ/default.php')

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

async def format_profile_table():
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
  site = '1713232817453x483766471272943900'
  for index, row in df.iterrows():
    #coloca o id do site na coluna site
    row['SiteVinculado'] = site
    
  
  return df