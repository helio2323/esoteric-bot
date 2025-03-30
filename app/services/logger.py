import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Logger:
    _instance = None  # Singleton para evitar múltiplas instâncias

    def __new__(cls, log_file="logs/app.log", controle=None, fechamento=None):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(log_file, controle, fechamento)
        return cls._instance

    def _initialize(self, log_file, controle, fechamento):
        # Obtém as credenciais do Supabase das variáveis de ambiente
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY devem estar definidas.")

        # Conexão com o Supabase
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Define o controle padrão e fechamento
        self.controle = controle
        self.fechamento = fechamento

        # Criação do diretório de logs caso não exista
        self.log_file = log_file
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)

        # Configuração do Logger
        self.logger = logging.getLogger("app_logger")
        if not self.logger.hasHandlers():  # Evita adicionar handlers repetidos
            self.logger.setLevel(logging.DEBUG)
            
            # Formatação de log sem data/hora na mensagem
            formatter = logging.Formatter('%(levelname)s - %(message)s')

            # Manipuladores (Handlers) de log
            file_handler = logging.FileHandler(self.log_file, mode="a", encoding="utf-8")
            file_handler.setFormatter(formatter)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)

            # Adicionando os handlers ao logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(stream_handler)

            # Adiciona o handler personalizado para salvar os logs no Supabase
            supabase_handler = SupabaseLogHandler(self.supabase, self.controle, self.fechamento)
            supabase_handler.setFormatter(formatter)
            self.logger.addHandler(supabase_handler)

    def log_info(self, message, controle=None, fechamento=None):
        self.logger.info(message, extra={"controle": controle or self.controle, "fechamento": fechamento or self.fechamento})

    def log_warning(self, message, controle=None, fechamento=None):
        self.logger.warning(message, extra={"controle": controle or self.controle, "fechamento": fechamento or self.fechamento})

    def log_error(self, message, controle=None, fechamento=None):
        self.logger.error(message, extra={"controle": controle or self.controle, "fechamento": fechamento or self.fechamento})

    def log_debug(self, message, controle=None, fechamento=None):
        self.logger.debug(message, extra={"controle": controle or self.controle, "fechamento": fechamento or self.fechamento})

# Classe para enviar logs ao Supabase
class SupabaseLogHandler(logging.Handler):
    def __init__(self, supabase_client, controle, fechamento=None):
        super().__init__()
        self.supabase_client = supabase_client
        self.default_controle = controle  # Define o controle padrão
        self.default_fechamento = fechamento  # Define o fechamento padrão

    def emit(self, record):
        log_entry = self.format(record)
        controle = getattr(record, "controle", self.default_controle)  # Usa o controle padrão caso não seja definido
        fechamento = getattr(record, "fechamento", self.default_fechamento)  # Usa o fechamento padrão caso não seja definido
        self.save_log_to_supabase(record.levelname, log_entry, controle, fechamento)

    def save_log_to_supabase(self, level, message, controle, fechamento):
        try:
            data = {"level": level, "message": message, "controle": controle}
            
            # Adiciona o campo fechamento apenas se ele tiver um valor
            if fechamento is not None:
                data["fechamento"] = fechamento
            
            response = self.supabase_client.table("elogs").insert(data).execute()
            if len(response.data) == 0:
                print(f"Falha ao salvar log no Supabase: {response}")
        except Exception as e:
            print(f"Erro ao salvar log no Supabase: {e}")