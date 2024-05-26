from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
import pandas as pd
from bs4 import BeautifulSoup
import requests

class Navegador:
    def __init__(self):
        # Configurar opções do Chrome
        options = Options()
        options.add_argument("--enable-automation")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--kiosk-printing")


        # Inicializar o WebDriver do Chrome com as opções configuradas
        #self.driver = webdriver.Remote(command_executor="https://grid.consium.com.br/wd/hub", options=options)
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.by = By
        self.locator = {
            "XPATH": By.XPATH,
            "ID": By.ID,
            "CLASS_NAME": By.CLASS_NAME,
            "LINK_TEXT": By.LINK_TEXT,
            "NAME": By.NAME,
            "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT,
            "TAG_NAME": By.TAG_NAME
        }

    async def get_session_id (self):
        return self.driver.session_id

    async def disable_alert(self):
        self.driver.switch_to.alert.dismiss()

    async def element_get_text(self, element, tag):
        if element in self.locator:
            try:
                # Aguardar até que o elemento seja visível e, em seguida, retornar seu texto
                element_text = self.wait.until(EC.visibility_of_element_located((self.locator[element], tag)))
                return element_text
            except TimeoutException:
                print("Elemento não encontrado")   
                  
    async def get_elements(self, element, tag):
        if element in self.locator:
            try:
                # Aguardar até que o elemento seja visível e, em seguida, retornar seu texto
                elements = self.wait.until(EC.visibility_of_all_elements_located((self.locator[element], tag)))
                return elements
            except TimeoutException:
                print("Elemento não encontrado")

    async def get(self, url):
        # await asyncio.sleep(0)
        self.driver.get(url)
    async def close(self):
    #  await asyncio.sleep(0)
        self.driver.quit()   

    async def close_session(self, session_id):
        grid_url = "https://grid.consium.com.br/wd/hub"
        session_url = f"{grid_url}/session/{session_id}"
        response = requests.delete(session_url)
        if response.status_code == 200:
            print("Sessão fechada com sucesso!")
        else:
            print("Falha ao fechar a sessão.")

        return response    
    # Funcao para digitar no elemento           
    async def sendkeys(self, element, tag, keys):
    #  await asyncio.sleep(0)
        if element in self.locator:
            try:
                self.wait.until(EC.presence_of_element_located((self.locator[element], tag))).send_keys(keys)
            except TimeoutException:
                print("Elemento não encontrado")
                
    # Funcao para clicar no elemento                
    async def click(self, element, tag):
    #  await asyncio.sleep(0)
        if element in self.locator:
            try:
                self.wait.until(EC.visibility_of_element_located((self.locator[element], tag))).click()
            except TimeoutException:    
                print("Elemento não encontrado")


    async def get_table_element(self, element, tag):
        try:
            # Obter o conteúdo HTML da tag <tbody>
            html_content = self.wait.until(EC.visibility_of_element_located((self.locator[element], tag))).get_attribute('innerHTML')
            # Extrair dados da tabela e transforma em dataframe
            data = await self.table_to_dataframe(html_content)
            qtd_linhas = len(data)
            return data, qtd_linhas
        except TimeoutException:
            print("Elemento não encontrado")

    async def table_to_dataframe(self, html_content):

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
        

                   
