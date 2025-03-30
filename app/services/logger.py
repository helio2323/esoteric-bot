import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Logger:
    _instance = None  # Singleton para evitar múltiplas instâncias

    def __new__(cls, log_file="logs/app.log", controle="default"):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(log_file, controle)
        return cls._instance

    def _initialize(self, log_file, controle):
        # Obtém as credenciais do Supabase das variáveis de ambiente
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY devem estar definidas.")

        # Conexão com o Supabase
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Define o controle padrão
        self.controle = controle

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
            supabase_handler = SupabaseLogHandler(self.supabase, self.controle)
            supabase_handler.setFormatter(formatter)
            self.logger.addHandler(supabase_handler)

    def log_info(self, message, controle=None):
        self.logger.info(message, extra={"controle": controle or self.controle})

    def log_warning(self, message, controle=None):
        self.logger.warning(message, extra={"controle": controle or self.controle})

    def log_error(self, message, controle=None):
        self.logger.error(message, extra={"controle": controle or self.controle})

    def log_debug(self, message, controle=None):
        self.logger.debug(message, extra={"controle": controle or self.controle})

# Classe para enviar logs ao Supabase
class SupabaseLogHandler(logging.Handler):
    def __init__(self, supabase_client, controle):
        super().__init__()
        self.supabase_client = supabase_client
        self.default_controle = controle  # Define o controle padrão

    def emit(self, record):
        log_entry = self.format(record)
        controle = getattr(record, "controle", self.default_controle)  # Usa o controle padrão caso não seja definido
        self.save_log_to_supabase(record.levelname, log_entry, controle)

    def save_log_to_supabase(self, level, message, controle):
        try:
            data = {"level": level, "message": message, "controle": controle}
            response = self.supabase_client.table("elogs").insert(data).execute()
            if len(response.data) == 0:
                print(f"Falha ao salvar log no Supabase: {response}")
        except Exception as e:
            print(f"Erro ao salvar log no Supabase: {e}")
