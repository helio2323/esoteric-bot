import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
import requests

class SupaConnect:
    def __init__(self):
        self.url = url
        self.key = key
        self.supabase = supabase

    def get_profile(self, id, esoteric_site):
        data = self.supabase.table("Esoteric-atendentes").select("*") .match({"id_site": id, "esoteric_site": esoteric_site}).execute()
        return data
    
    def get_profiles(self):
        data = self.supabase.table("Esoteric-atendentes").select("*").execute()
        return data

    def save_profiles(self, **kwargs):

        payload = kwargs['profile']

        data = self.supabase.table("Esoteric-atendentes").insert(payload).execute()

        # Assert we pulled real data.
        assert len(data.data) > 0

        return data

    def update_profiles(self, **kwargs):
        
        payload = kwargs['profile']
        profile_id = kwargs['profile_id']
        esoteric_site = kwargs['esoteric_site']

        data = supabase.table("Esoteric-atendentes").update(payload).match({"id_site": profile_id, "esoteric_site": esoteric_site}).execute()

        return data

    def controle_update(self, **kwargs):

        payload = kwargs['payload']
        controle_id = kwargs['controle_id']

        data = supabase.table("Esoteric-controler").update(payload).eq("id", controle_id).execute()

        return data

    def create_payments(self, **kwargs):

        #insere uma lista de pagamentos
        data = supabase.table("Esoteric-pagamentos").insert(kwargs['payload']).execute()
        return data
    
    def get_payments(self, **kwargs):

        fechamento = kwargs['fechamento']

        data = supabase.table("Esoteric-pagamentos").select("*").match({"fechamento": fechamento, "site_id": kwargs['site_id']}).execute()

        return data

    def delte_all_payments(self, **kwargs):
        payment_ids = []

        fechamento = kwargs['fechamento']
        site_id = kwargs['site_id']

        fechamentos = self.get_payments(fechamento=fechamento, site_id=site_id)

        for fechamento in fechamentos.data:
            payment_ids.append(fechamento['id'])

        #for fechamento in fechamentos.data:
        supabase.table("Esoteric-pagamentos").delete().in_("id", payment_ids).execute()

        
        return 
    
    def get_controlers(self):
        data = supabase.table("Esoteric_view").select("*").execute()
        return data

    def get_fechamentos(self):
        data = supabase.table("Esoteric_fechamentos_sites_view").select("*").execute()
        return data
    
    def update_fechamento(self, fechamento_id):

        data = supabase.table("Esoteric-Fechamentos").update({"status": "Concluído"}).eq("id", fechamento_id).execute()

        return data

