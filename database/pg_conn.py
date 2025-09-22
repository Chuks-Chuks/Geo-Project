from sqlalchemy import create_engine
from utils import log, config

settings = config.SETTINGS
log = log.get_logger() 

class DatabaseConnect:
    def __init__(self):
        self.connect = create_engine(f"postgresql://postgres:{settings.db_pass}@settings.db_host}:5432/{settings.db_name}")



try:
    f = DatabaseConnect()
    if f:
        log.info('connection successful')
except Exception as e:
    log.info(f'{e}')


