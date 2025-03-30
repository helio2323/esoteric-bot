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

#from app.services.logger import Logger


class Profiles:
    def __init__(self):
        self.driver = Driver()
        self.profile_actions = ProfileActions()
        self.supa = SupaConnect()
        self.logger = Logger()
        
    
    def get_profiles(self, **kwargs):
        
        self.logger.log_info(f"Fazendo login no site")
        self.profile_actions.login(kwargs['username'], kwargs['password'], kwargs['site_url'])

        self.profile_actions.enter_atendentes(kwargs['site_url'])
        self.logger.log_info(f"Capturando perfis para inserção/atualização no banco de dados")
        table = self.profile_actions.table_to_dataframe()

        return table

        #salva os profile dentro do BD

    def save_update_profiles(self, **kwargs):

        controle = kwargs['controle']
        self.logger.controle = controle

        self.supa.controle_update(controle_id=controle, payload={'status': 'Em execução'})

        self.logger.log_info(f"Iniciando o processo de atualização dos perfis")
        profiles = self.get_profiles(**kwargs)
        
        save_profiles = self.profile_actions.iter_in_profiles(profiles=profiles, site_url=kwargs['site_url'], esoteric_site=kwargs['esoteric_site'])

        self.driver.stop_driver()

        


username = "automacao"
password = "automacaoautomacao"
site_url = "https://rainhasmisticas.com.br/gerencial_kDsI6fjyPQnf/"

profile = Profiles()
profile.save_update_profiles(username=username, password=password, site_url=site_url, controle=7, esoteric_site=1)