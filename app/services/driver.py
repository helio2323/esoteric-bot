# driver_service.py
from seleniumbase import Driver as SeleniumBaseDriver
from seleniumbase import BaseCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
import requests
from app.services.logger import Logger

class Driver(BaseCase):
    def __init__(self):
        # Configurar opções do Chrome
        self.options = uc.ChromeOptions()
        self.options.add_argument("--enable-automation")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument("--kiosk-printing")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-popup-blocking")
        
        # Adicionar preferências para controlar PDFs
        prefs = {
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": False,
            "download.open_pdf_in_system_viewer": False,
            "download.default_directory": "/caminho/para/pasta/downloads"  # Substitua pelo caminho desejado
        }
        self.options.add_experimental_option("prefs", prefs)


        self.logger = Logger()
        
        # Remova ou comente a linha abaixo se não for usar o método add_extension para UC Mode

                
        # Inicializar o driver como None para que ele não seja iniciado
        self.driver = None

    def start_driver(self):
        if not self.driver:
            # Inicializar o driver do SeleniumBase com o modo UC e passando o diretório da extensão descompactada
            #self.driver = SeleniumBaseDriver(uc=True, extension_dir='./extensions/solver')
            self.driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub", options=self.options)
            #self.driver.get("https://www.google.com")
            self.logger.log_info("Driver iniciado com sucesso")
        else:
            self.logger.log_info("Driver já está em execução")
        return self.driver
        
    def stop_driver(self):
        if self.driver:
            self.driver.quit()
            self.logger.log_info("Driver encerrado com sucesso")
        else:
            self.logger.log_info("Driver não está em execução")

    def safe_get_image_src(self, xpath):
        """Tenta obter o atributo src de uma imagem, retornando None se não existir."""
        elementos = self.find_elements(By.XPATH, xpath)
        return elementos[0].get_attribute("src") if elementos else None

    def get_session_id (self):
        return self.driver.session_id

    def disable_alert(self):
        self.driver.switch_to.alert.dismiss()

    def element_get_text(self, element, tag):
        if element in self.locator:
            try:
                # Aguardar até que o elemento seja visível e, em seguida, retornar seu texto
                element_text = self.wait.until(EC.visibility_of_element_located((self.locator[element], tag)))
                return element_text
            except TimeoutException:
                print("Elemento não encontrado")   
                  
    def get_elements(self, element, tag):
        if element in self.locator:
            try:
                # Aguardar até que o elemento seja visível e, em seguida, retornar seu texto
                elements = self.wait.until(EC.visibility_of_all_elements_located((self.locator[element], tag)))
                return elements
            except TimeoutException:
                print("Elemento não encontrado")

    def get(self, url):
        # await o.sleep(0)
        self.driver.get(url)
    def close(self):
    #  await o.sleep(0)
        self.driver.quit()   

    def close_session(self, session_id):
        grid_url = "https://grid.talentai.com.br/wd/hub"
        session_url = f"{grid_url}/session/{session_id}"
        response = requests.delete(session_url)
        if response.status_code == 200:
            print("Sessão fechada com sucesso!")
        else:
            print("Falha ao fechar a sessão.")

        return response    
    # Funcao para digitar no elemento           
    def sendkeys(self, element, tag, keys):
    #  await o.sleep(0)
        if element in self.locator:
            try:
                self.wait.until(EC.presence_of_element_located((self.locator[element], tag))).send_keys(keys)
            except TimeoutException:
                print("Elemento não encontrado")
                
    # Funcao para clicar no elemento                
    def click(self, element, tag):
    #  await asyncio.sleep(0)
        if element in self.locator:
            try:
                self.wait.until(EC.visibility_of_element_located((self.locator[element], tag))).click()
            except TimeoutException:    
                print("Elemento não encontrado")