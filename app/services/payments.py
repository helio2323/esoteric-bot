import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))  
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  

from app.services.driver import Driver
from app.models.profile_actions import ProfileActions
from app.models.supa_connect import SupaConnect
from app.services.logger import Logger
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd
from  datetime import datetime

#from app.services.logger import Logger


class Payments:
    def __init__(self):
        self.driver = Driver()
        self.profile_actions = ProfileActions()
        self.supa = SupaConnect()
        self.logger = Logger()

    def login(self, username, password, site_url):

        try:
            driver = self.driver.start_driver()
            self.driver.driver.get(site_url)
            time.sleep(1)
            self.driver.driver.find_element(By.ID, "FLogin").send_keys(username)
            self.driver.driver.find_element(By.ID, "FSenha").send_keys(password)
            self.driver.driver.find_element(By.XPATH, '/html/body/div/div[2]/form/button').click()

            time.sleep(3)

            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}        

    def table_to_dataframe(self, html_content):

        soup = BeautifulSoup(html_content, 'html.parser')

        # Encontra a tabela desejada (selecionando-a pela classe, id ou outras características)
        table = soup.find('table')

        # Verifica se a tabela foi encontrada
        if table:
            # Inicializa uma lista para armazenar os dados da tabela
            table_data = []
            # Itera sobre as linhas da tabela (<tr>)
            for row in table.find_all('tr'):
                # Inicializa uma lista para armazenar os dados de uma linha
                row_data = []
                # Itera sobre as células da linha (<td>)
                for cell in row.find_all(['td']):
                    # Adiciona o texto da célula à lista de dados da linha
                    value = cell.text.strip()
                    # Verifica se o valor não está vazio
                    if value:
                        row_data.append(value)
                    else:
                        row_data.append(None)
                    # Verifica se a célula contém uma tag de âncora (hiperlink)
                    link = cell.find('a')
                    if link:
                        # Se houver uma tag de âncora, adiciona o link (href) à lista de dados da linha
                        row_data.append(link.get('href'))
                    else:
                        row_data.append(None)
                # Adiciona os dados da linha à lista de dados da tabela
                if row_data:
                    table_data.append(row_data)

            # Imprime os dados da tabela
            
            df = pd.DataFrame(table_data)
            df.to_excel('arquivo.xlsx', index=False)

            return df

    def converter_credito_para_float(self, valor):
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

    def get_table_payments(self, site_id, site_url):

        
        time.sleep(2)
        table =  self.driver.driver.find_element(By.XPATH, '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/th').get_attribute('innerHTML')
        data = self.table_to_dataframe(table)

        df = pd.DataFrame(data)
        df = df.rename(columns={
                    0: 'ID',
                    2: 'Nome',
                    3: 'Link',
                    4: 'CPF',
                    6: 'Creditos',
                })
        df = df.drop(df.index[0])
        df.drop(df.columns[[1, 4]], axis=1, inplace=True)
        df['SiteVinculado'] = site_id

        for index, row in df.iterrows():
            valor_convertido = self.converter_credito_para_float(row['Creditos'])
            df.at[index, 'Creditos'] = valor_convertido

        return df
    
    def get_payments(self, **kwargs):

        self.logger.log_info(f"Capturando pagamentos para inserção/atualização no banco de dados")
        login = self.login(kwargs['username'], kwargs['password'], kwargs['site_url'])

        return


    def extract_payments(self, table, fechamento, site_id):
        payload = []
        self.supa.delte_all_payments(fechamento=fechamento, site_id=site_id)
        for index, row in table.iterrows():

            profile_id = int(row['ID'])
            profile_id = self.supa.get_profile(profile_id, site_id)
            
            print(profile_id)

            payments = {
                "atendente_id": profile_id.data[0]['id'],
                "fechamento": fechamento,
                "site_id": site_id,
                "valor": row['Creditos'],
                "status": "pending",
                # passa a data atual
                "data_criacao": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }    
            
            if row['Creditos'] >= 0:
                payload.append(payments)
        print(f"total de pagamentos: {len(payload)}")
        payment =self.supa.create_payments(payload=payload)
        self.logger.log_info(f"Pagamento {payment.data[0]['id']} inserido no banco de dados")




    def register_payments(self, **kwargs):

        
        self.get_payments(**kwargs)

        self.driver.driver.get(kwargs['site_url'] + 'PG_Atendentes/Pg.Fechamento.php')

        table = self.get_table_payments(kwargs['esoteric_site'], kwargs['site_url'])

        self.extract_payments(table, kwargs['fechamento'], kwargs['esoteric_site'])

        self.supa.update_fechamento(kwargs['fechamento'])
        
        try:
            self.driver.stop_driver()
        
        except Exception as e:
            print(f"Erro ao fechar o driver: {e}")

        return





#payments = Payments()
#payments.register_payments(username=username, password=password, site_url=site_url, fechamento=6, esoteric_site=1)

