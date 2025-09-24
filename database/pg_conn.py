from utils import log, config
from sqlalchemy import create_engine


settings = config.SETTINGS
log = log.get_logger() 
# log.info(f'Here are the credentials: {settings.db_port}, {settings.db_host}')

class DatabaseConnect:
    def __init__(self):
        self.connect = create_engine(f"postgresql://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}")

    def get_engine(self):
        return self.connect

