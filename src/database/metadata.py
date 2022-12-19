from peewee import *
from playhouse.db_url import connect as db_connect
from .models import *


def init_database(psql_url, drop=False):
    db = db_connect(psql_url, autorollback=True)
    try:
        db.connect()            
    except InternalError as px:
        print(str(px))
        return
    
    model_list = [Checkpoint, SourceData, UsersCall, DBCall, AppCall]    
    for Model in model_list:
        Model.bind(db)        
        if drop:
            Model.drop_table()
        Model.create_table()
        
    return db
        
      
    