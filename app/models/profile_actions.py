from app.services.driver import Driver
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from app.models.supa_connect import SupaConnect
from app.services.logger import Logger
from tqdm import tqdm


class ProfileActions:
    def __init__(self, logger=None):
        self.driver = Driver()
        self.supa = SupaConnect()
        self.logger = logger if logger else Logger()

    
    def login(self, username, password, site_url):

        try:
            self.driver.start_driver()
            self.driver.driver.get(site_url)
            time.sleep(1)
            self.driver.driver.find_element(By.ID, "FLogin").send_keys(username)
            self.driver.driver.find_element(By.ID, "FSenha").send_keys(password)
            self.driver.driver.find_element(By.XPATH, '/html/body/div/div[2]/form/button').click()

            time.sleep(3)

            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def enter_atendentes(self, site_url):
        try:
            self.driver.driver.get(site_url + '/PG_Atendentes')
            self.driver.driver.find_element(By.ID, "select").click()
            self.driver.driver.find_element(By.XPATH, "/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[3]/th/table/tbody/tr/td[1]/select/option[9]").click()

            return {'status': 'success'}        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


    def get_checked_pix_tipo(self):
        """
        Encontra todos os inputs com name "PIXTipo" e itera sobre eles para
        retornar o valor do input selecionado.

        Parâmetros:
        - self: instância do Selenium Webself.

        Retorna:
        - O valor (atributo 'value') do input selecionado ou None se nenhum estiver marcado.
        """
        # Busca todos os inputs do tipo rádio com name "PIXTipo"
        pix_options = self.driver.driver.find_elements(By.XPATH, "//input[@name='PIXTipo']")
        
        # Itera sobre os elementos e retorna o que estiver selecionado
        for option in pix_options:
            if option.is_selected():
                return {"status": "success", "value": option.get_attribute('value')}
        
        return {"status": "error", "message": "Nenhum pix selecionado"}

    def get_checked_conta_tipo(self):
        """
        Encontra todos os inputs com name "Conta_Tipo", itera sobre eles para
        identificar o selecionado e retorna "Corrente" se o valor for "C" ou "Poupança" se for "P".

        Parâmetros:
        - self: instância do Selenium Webself.

        Retorna:
        - Uma string com o tipo de conta ou None se nenhum estiver marcado.
        """
        conta_options = self.driver.driver.find_elements(By.XPATH, "//input[@name='Conta_Tipo']")
        
        for option in conta_options:
            if option.is_selected():
                value = option.get_attribute("value")
                if value == "C":
                    return "Corrente"
                elif value == "P":
                    return "Poupança"
                else:
                    return value  # Para outros casos, se houver
        return None
    
    def table_to_dataframe(self):
        html_content = self.driver.driver.find_element(
            By.XPATH, '/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[4]/th'
        ).get_attribute('innerHTML')

        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the first table
        table = soup.find('table')

        # Check if the table was found
        if table:
            # Initialize a list to store the table data
            table_data = []
            # Iterate over rows in the table (<tr>)
            for row in table.find_all('tr'):
                row_data = []
                # Iterate over the cells (<td>)
                for cell in row.find_all(['td']):
                    value = cell.text.strip()
                    row_data.append(value if value else None)
                    # Check for a hyperlink
                    link = cell.find('a')
                    row_data.append(link.get('href') if link else None)
                if row_data:
                    table_data.append(row_data)

            # Create DataFrame from table_data
            df = pd.DataFrame(table_data)
            df.to_excel('arquivo.xlsx', index=False)

            # Uncomment or modify the following if you need to drop specific columns 
            # (using column indices might need adjustments based on the actual data structure)
            colunas_excluir = [1, 2, 3, 6, 7, 9, 11, 13, 14, 15, 16, 17, 18]
            df = df.drop(columns=colunas_excluir, errors='ignore')
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
            return df

        else:
            self.logger.error("No table found on the page.")
            return None

    def get_profile_infos(self, site_id, esoteric_site):
        elementos = self.driver.driver.find_elements(By.XPATH, "/html/body/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/th/form/table/tbody/tr[56]/td[2]/img")
        foto = elementos[0].get_attribute("src") if elementos else None

        profile = {
            "nome": self.driver.driver.find_element(By.ID, "Nome").get_attribute("value"),
            "data_cadastro": self.driver.driver.find_element(By.ID, "DataCadastro").get_attribute("value"),
            "cpf": self.driver.driver.find_element(By.ID, "CPF").get_attribute("value"),
            "rg": self.driver.driver.find_element(By.ID, "RG").get_attribute("value"),
            "dt_nascimento": self.driver.driver.find_element(By.ID, "DataNascimento").get_attribute("value"),
            "email": self.driver.driver.find_element(By.ID, "Email").get_attribute("value"),
            "cep": self.driver.driver.find_element(By.ID, "En_CEP").get_attribute("value"),
            "logradouro": self.driver.driver.find_element(By.ID, "En_Endereco").get_attribute("value"),
            "complemento": self.driver.driver.find_element(By.ID, "En_Complemento").get_attribute("value"),
            "numero": self.driver.driver.find_element(By.ID, "En_Numero").get_attribute("value"),
            "bairro": self.driver.driver.find_element(By.ID, "En_Bairro").get_attribute("value"),
            "cidade": self.driver.driver.find_element(By.ID, "En_Cidade").get_attribute("value"),
            "uf": self.driver.driver.find_element(By.ID, "En_Estado").get_attribute("value"),
            "telefone": self.driver.driver.find_element(By.ID, "Telefone01").get_attribute("value"),
            "pix": self.driver.driver.find_element(By.ID, "PIX").get_attribute("value"),
            # Se desejar utilizar as funções já criadas para pegar o tipo, descomente as linhas abaixo:
            "tipo_pix": self.get_checked_pix_tipo(),
            "banco": self.driver.driver.find_element(By.ID, "Conta_Banco").get_attribute("value"),
            "agencia": self.driver.driver.find_element(By.ID, "Conta_Agencia").get_attribute("value"),
            "conta": self.driver.driver.find_element(By.ID, "Conta_Numero").get_attribute("value"),
            "favorecido": self.driver.driver.find_element(By.ID, "Conta_Favorecido").get_attribute("value"),
            "cpf_conta": self.driver.driver.find_element(By.ID, "Conta_CPF").get_attribute("value"),
            "tipo_conta": self.get_checked_conta_tipo(),
            "foto": foto,
            "site_nome": self.driver.driver.find_element(By.ID, "SiteNome").get_attribute("value"),
            "experiencia": self.driver.driver.find_element(By.ID, "Experiencia").get_attribute("value"),
            "horarioatendimento": self.driver.driver.find_element(By.ID, "HorarioAtendimento").get_attribute("value"),
            "oraculos": self.driver.driver.find_element(By.ID, "Oraculos").get_attribute("value"),
            "frase": self.driver.driver.find_element(By.ID, "Frase").get_attribute("value"),
            "sitedescricao": self.driver.driver.find_element(By.ID, "SiteDescricao").get_attribute("value"),
            "id_site": site_id,
            "esoteric_site": esoteric_site,
            "status": False
        }
        return profile

    def profiles_exist(self, **kwargs):

        print(kwargs["id_site"], kwargs["esoteric_site"])

        profile = self.supa.get_profile(kwargs['id_site'], kwargs['esoteric_site'])

        return profile


    def iter_in_profiles(self, profiles, site_url, esoteric_site, **kwargs):
        profile_saved = []
        profile_updated = []
        controle = self.logger.controle
        
        # Adicionando tqdm para a barra de progresso
        for index, row in tqdm(profiles.iterrows(), total=len(profiles), desc="Processando perfis", unit="perfil"):
            self.logger.log_info(f"Processando perfil {row['ID']}")
            try:
                self.driver.get(site_url + "/PG_Atendentes/Pg.Edicao.php?Codigo=" + str(row['ID']))

                time.sleep(0.5)

                profile = self.get_profile_infos(site_id=row['ID'], esoteric_site=esoteric_site)

                profile_exists = self.profiles_exist(id_site=row['ID'], esoteric_site=esoteric_site)
                
                if len(profile_exists.data) > 0:
                    resp_update = self.supa.update_profiles(profile=profile, profile_id=row['ID'], esoteric_site=esoteric_site)
                    profile_updated.append(resp_update.data[0]["id_site"])
                    self.logger.log_info(f"Perfil {row['ID']} atualizado com sucesso!")
                else:
                    resp_save = self.supa.save_profiles(profile=profile)
                    profile_saved.append(resp_save.data[0]["id_site"])
                    self.logger.log_info(f"Perfil {row['ID']} salvo com sucesso!")
            except Exception as e:
                self.logger.log_error(f"Erro ao processar perfil {row['ID']}: {e}")
                continue

        self.logger.log_info(f"Total de perfis salvos: {len(profile_saved)}")
        self.logger.log_info(f"Total de perfis atualizados: {len(profile_updated)}")

        self.supa.controle_update(controle_id=controle, payload={'status': 'Concluído'})
        return profile_saved


