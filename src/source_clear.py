from parsers import LogParser, RemoteFileReader
from database import *
from args import * 

def main():
    
    print(f"Start: {__file__}")
    args = get_args()
    init_database(args.psql_url, drop=False) 
    
    events = {
        "app_call": ["CALL"],
        "user_call": ["VRSREQUEST", "VRSRESPONSE"],
        "db_call": ["DBPOSTGRS"],
    }
    
    # Считаем и установим чекпойнты
    rows = 0
    for point in Checkpoint.filter(layer=2):
        rows += SourceData.delete().where(
                (SourceData.event.in_(events[point.proc]))
                &
                (SourceData.date<point.checkpoint)
            ).execute()
    
    print(f"Delete {rows} source records.")
    print("Done.")
    
if __name__ == "__main__":
    main()