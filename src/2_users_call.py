from datetime import datetime,  timedelta
from database import *
from args import * 

def main():
    args = get_args()
    init_database(args.psql_url, drop=False)
    
    proc='user_call'
    #UsersCall.drop_table()
    #UsersCall.create_table()
    
    val_checkpoint = Checkpoint.get_or_none(layer=2, proc=proc)
    if val_checkpoint is None:
        val_checkpoint = Checkpoint.create(layer=2, proc=proc, checkpoint=datetime(1970, 1, 1))
        
    checkpoint = val_checkpoint.checkpoint
    
    print(f"Start: {__file__}")
    print(f"Checkpoint: {checkpoint}")
    
    # Определять связь запрос-ответ и серверную функцию будем по FIFO
    # возможно связь будет установлена неверно для коротких вызовов,
    # но нас интересуют длительные вызовы
    
    # разделим коннекты разных пользователей сортировкой по connectid и osthread    
    query_request = SourceData.select().where(
            (SourceData.date>checkpoint) 
            & (SourceData.event=='VRSREQUEST')
        ).order_by(SourceData.connectid, SourceData.osthread, SourceData.date)
        
    query_response = SourceData.select().where(
            (SourceData.date>checkpoint) 
            & (SourceData.event=='VRSRESPONSE')
        ).order_by(SourceData.connectid, SourceData.osthread, SourceData.date)
        
    query_call = SourceData.select().where(
            (SourceData.date>checkpoint) 
            & (SourceData.event=='CALL')
            & (SourceData.context.is_null(False))
        ).order_by(SourceData.connectid, SourceData.osthread, SourceData.date)
    
    requests = list(query_request)
    responses = list(query_response)
    calls = list(query_call)
    done_id = list()
    
    
    result = list()
    for request in requests:
        # Ищем ответы
        resp_list = list(filter(
                lambda x: (
                    x.date>request.date 
                    and x.connectid==request.connectid
                    and x.osthread==request.osthread
                    and x.clientid==request.clientid                    
                    and not x.id in done_id
                ), responses))
        
        if not len(resp_list): # Если не нашли ответ
            continue
        response = resp_list[0]
        done_id.append(response.id)
        
        delta = response.date-request.date
        duration=delta.microseconds + delta.seconds*1000000
        
        
        # Ищем сервеные вызовы
        call_list = list(filter(
                lambda x: (
                    x.date>response.date 
                    #and x.duration>=duration
                    and x.connectid==response.connectid
                    and x.osthread==response.osthread
                    and x.clientid==response.clientid                                        
                    and not x.id in done_id
                ), calls))
        
        if not len(call_list): # Если нет вызовов, то нам это не интересно
            continue
        
        call = call_list[0]
        done_id.append(call.id)
        if call.context is None: # Вызов без контекста нам не интересен
            continue
        
        # Полученные данные готовим для записи в СУБД
        call_row = UsersCall(
                date=request.date, 
                duration_call=call.duration, 
                duration=duration,
                processname=call.processname, 
                applicationname=call.applicationname, 
                usr=call.usr, 
                context=call.context)
        result.append(call_row)
        checkpoint = max(call.date, checkpoint)
        
        #print(response.date, request.date, duration, call.duration)
        
    UsersCall.bulk_create(result, 100) # Запись в БД
    
    val_checkpoint.checkpoint = checkpoint
    val_checkpoint.save()
    
    print(f"Add {len(result)} records.")
    print(f"New checkpoint: {checkpoint}")
    print("Done.")

if __name__ == "__main__":    
    main()