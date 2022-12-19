from parsers import LogParser, RemoteFileReader
from args import * 
from database import *

def main():
    args = get_args()
    print(f"Start: {__file__}")

    sftp = RemoteFileReader(args.ssh, args.ssh_key)    
    parser = LogParser(path=args.log_path, sftp=sftp)
    init_database(args.psql_url, drop=False)  
    
    # Считаем и установим чекпойнты
    parser.set_chekpoints([(val.proc, val.checkpoint) for val in Checkpoint.filter(layer=1)])
    
    rows = []    
    for row in parser.get_data():
        rows.append(SourceData(**row.as_dict()))
        if len(rows)>10000: # Экономия памяти
            SourceData.bulk_create(rows, 100)
            rows = [] 
        
    SourceData.bulk_create(rows, 100)
    
    #Запишем чекпойнты в базу
    active_procs = []
    for proc, checkpoint in parser.get_chekpoints():
        active_procs.append(proc)
        var = Checkpoint.get_or_none(Checkpoint.layer==1, Checkpoint.proc==proc)
        if var is None:
            Checkpoint.create(layer=1, proc=proc, checkpoint=checkpoint)
        else:
            var.checkpoint=checkpoint
            var.save()
    Checkpoint.delete().where( (Checkpoint.layer == 1) & (Checkpoint.proc.not_in(active_procs)) ).execute()

    print(f"Add {len(rows)} records.")
    print("Done.")
    
if __name__ == "__main__":
    main()