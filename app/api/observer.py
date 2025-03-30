import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))  
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  

from app.models.supa_connect import SupaConnect
from app.services.profiles import Profiles
from app.services.payments import Payments

import time


class Observer:

    def __init__(self):
        self.supa = SupaConnect()
        self.profiles = Profiles()
        self.payments = Payments()

    def gest_lists(self, **kwargs):

        controlers_list = self.supa.get_controlers()
        #fechamento_list = self.supa.get_fechamentos()

        return controlers_list.data
    
    def observer_controler(self, **kwargs):

        controlers_list = self.supa.get_controlers()

        for controler in controlers_list.data:

           if controler['status'] == 'Na fila' or controler['status'] == 'Em execução':

                response = self.profiles.save_update_profiles(
                    username=controler['usuario'],
                    password=controler['senha'],
                    site_url=controler['site_url'],
                    controle=controler['controler_id'],
                    esoteric_site=controler['controler_site_id']
                )
            
        
        return response


    def observer_fechamento(self, **kwargs):

        fechamento_list = self.supa.get_fechamentos()

        for fechamento in fechamento_list.data:
            if fechamento['status'] == 'Na fila':

                response = self.payments.register_payments(
                    username=fechamento['usuario'],
                    password=fechamento['senha'],
                    site_url=fechamento['site_url'],
                    fechamento=fechamento['fechamento_id'],
                    esoteric_site=fechamento['site_id']
                )
                
        
        return response

    def check_status(self, **kwargs):

        controlers_list = self.supa.get_controlers()

        for controler in controlers_list.data:
            if controler["status"] == "Na fila" or controler["status"] == "Em execução":

                return True
            else:
                pass
        
        return False


    def run_obeserver(self, **kwargs):

        status = self.check_status()

        if status == True:

            self.observer_controler()
        else:
            self.observer_fechamento()



observer = Observer()

observer.run_obeserver()