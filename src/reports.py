from datetime import datetime, timedelta
import pandas as pd
from peewee import fn
from database import *
from args import * 

def day_interval(date):
    return (
        datetime(date.year, date.month, date.day), 
        datetime(date.year, date.month, date.day) + timedelta(days=1),
    )
        

def report_user_call(date=None, duration=30):
    date_begin, date_end = day_interval(date or datetime.now())
    
    fields = [
        UsersCall.context, 
        UsersCall.processname, 
        fn.Count(UsersCall.id).alias('count'),
        fn.Sum(UsersCall.duration).alias('duration'),
        fn.Avg(UsersCall.duration).alias('avg'),
        fn.Max(UsersCall.duration).alias('max'),
    ]
    
    query = UsersCall.select(*fields).where(
            (UsersCall.date>=date_begin)
            & (UsersCall.date<date_end)
            & (UsersCall.duration>duration*1e6)            
        ).group_by(UsersCall.context, UsersCall.processname).order_by(SQL('avg').desc())
    
    result = list(query.dicts())
    if len(result)==0:
        return "Not data"
        
    df = pd.DataFrame(result)
    
    df['duration'] = round(df['duration']/1e6, 3)
    df['avg'] = round(pd.to_numeric(df['avg'])/1e6, 3)
    df['max'] = round(df['max']/1e6, 3)
    
    df.columns = ['Метод', 'База', 'Количество', 'Суммарная длительность', 'Средняя длительность', 'Максимальная длительность']
    
    return df.to_html(classes='report')


def report_db_call(date=None, duration=30):
    date_begin, date_end = day_interval(date or datetime.now())
    
    fields = [
        DBCall.context, 
        DBCall.processname, 
        DBCall.sql, 
        fn.Count(DBCall.id).alias('count'),
        fn.Sum(DBCall.duration).alias('duration'),
        fn.Avg(DBCall.duration).alias('avg'),
        fn.Max(DBCall.duration).alias('max'),
    ]
    
    query = DBCall.select(*fields).where(
            (DBCall.date>=date_begin)
            & (DBCall.date<date_end)
            & (DBCall.duration>duration*1e6)            
        ).group_by(DBCall.context, DBCall.sql, DBCall.processname).order_by(SQL('avg').desc())

    result = list(query.dicts())
    if len(result)==0:
        return "Not data"
        
    df = pd.DataFrame(result)

    df['duration'] = round(df['duration']/1e6, 3)
    df['avg'] = round(pd.to_numeric(df['avg'])/1e6, 3)
    df['max'] = round(df['max']/1e6, 3)
    df.columns = ['Метод', 'База', 'Текст', 'Количество', 'Суммарная длительность', 'Средняя длительность', 'Максимальная длительность']
    
    return df.to_html(classes='report')
    
    
def report_app_call(date=None, duration=30):
    date_begin, date_end = day_interval(date or datetime.now())
    
    fields = [
        AppCall.context, 
        AppCall.processname, 
        fn.Count(AppCall.id).alias('count'),
        fn.Sum(AppCall.duration).alias('duration'),
        fn.Avg(AppCall.duration).alias('avg'),        
        fn.Max(AppCall.duration).alias('max'),
        fn.Avg(AppCall.cputime).alias('cpu'),
    ]
    
    query = AppCall.select(*fields).where(
            (AppCall.date>=date_begin)
            & (AppCall.date<date_end)
            & (AppCall.duration>duration*1e6)            
        ).group_by(AppCall.context, AppCall.processname).order_by(SQL('avg').desc())

    result = list(query.dicts())
    #print(result)
    if len(result)==0:
        return "Not data"
        
    df = pd.DataFrame(result)

    df['duration'] = round(df['duration']/1e6, 3)
    df['avg'] = round(pd.to_numeric(df['avg'])/1e6, 3)
    df['max'] = round(df['max']/1e6, 3)
    df['cpu'] = pd.to_numeric(df['cpu'])
    df.columns = ['Метод', 'База', 'Количество', 'Суммарная длительность', 'Средняя длительность', 'Максимальная длительность', "Сред.CPU"]
    
    return df.to_html(classes='report')


def report_app_mem(date=None, top=10):
    date_begin, date_end = day_interval(date or datetime.now())
    
    fields = [
        AppCall.context, 
        AppCall.processname, 
        fn.Count(AppCall.id).alias('count'),
        fn.Avg(AppCall.memorypeak).alias('avg'),
        fn.Max(AppCall.memorypeak).alias('max'),
    ]
    
    query = AppCall.select(*fields).where(
            (AppCall.date>=date_begin)
            & (AppCall.date<date_end)                        
        ).group_by(AppCall.context, AppCall.processname).order_by(SQL('max').desc()).limit(top)

    result = list(query.dicts())    
    if len(result)==0:
        return "Not data"
        
    df = pd.DataFrame(result)

    df['avg'] = round(pd.to_numeric(df['avg']))
    df['max'] = df['max']
    df.columns = ['Метод', 'База', 'Количество', 'Среднее', 'Максимальное']
    
    return df.to_html(classes='report')

if __name__ == "__main__":
    args = get_args()
    init_database(args.psql_url, drop=False)
    report_app_call(duration=0.001)