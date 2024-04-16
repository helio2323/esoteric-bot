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
from flask import request

class Navegador:
  def __init__ (self):
      # Necessário fazer instalação do chrome versao mais recente sempre
      self.option = webdriver.Remote(command_executor="http://localhost:4444/wd/hub", options=Options())
      #self.option.add_argument("--enable-automation")
      self.option.add_argument("--start-maximized")
      self.option.add_argument("--disable-notifications")
      self.option.add_argument("--disable-popup-blocking")
      
      self.driver = webdriver.Chrome(options=self.option)
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
  async def get(self, url):
      # await asyncio.sleep(0)
      self.driver.get(url)
  async def close(self):
    #  await asyncio.sleep(0)
      self.driver.quit()
      
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

