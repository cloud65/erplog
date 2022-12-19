from datetime import datetime,  timedelta
from database import *
from args import * 
from re import search as re_search

def main():
    args = get_args()
    init_database(args.psql_url, drop=False)
    proc = 'app_call'
    
    #AppCall.drop_table()
    #AppCall.create_table()
    
    val_checkpoint = Checkpoint.get_or_none(layer=2, proc=proc)
    if val_checkpoint is None:
        val_checkpoint = Checkpoint.create(layer=2, proc=proc, checkpoint=datetime(1970, 1, 1))
        
    checkpoint = val_checkpoint.checkpoint
    
    print(f"Start: {__file__}")
    print(f"Checkpoint: {checkpoint}")
    
           
    query_call = SourceData.select().where(
            (SourceData.date>checkpoint) 
            & (SourceData.event=='CALL')
            & (SourceData.context.is_null(False))
        )
    
        
    result = list()
    for call in query_call:
        # Полученные данные готовим для записи в СУБД
        call_row = AppCall(
                date=call.date, 
                duration=call.duration, 
                processname=call.processname, 
                context=call.context,#re_search(r'\w.+\n|^\w.+$', call.context).group(),
                cputime=call.cputime,
                memory=call.memory,
                memorypeak=call.memorypeak,
            )
        result.append(call_row)
        checkpoint = max(call.date, checkpoint)
        
    AppCall.bulk_create(result, 100) # Запись в БД
    
    val_checkpoint.checkpoint = checkpoint
    val_checkpoint.save()
    
    print(f"Add {len(result)} records.")
    print(f"New checkpoint: {checkpoint}")
    print("Done.")

if __name__ == "__main__":    
    main()