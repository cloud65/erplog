from peewee import *

class Checkpoint(Model):
    """
    Для хранения checkpoint'ов для каждого слоя.
    Причем для первого слоя необходимо учитывать и идентификатор процесса
    """
    layer = IntegerField()
    checkpoint = DateTimeField(null=True)
    proc = CharField(max_length=25)
    

class SourceData(Model):
    date = DateTimeField(index=True)
    duration = IntegerField(default=0)
    event = CharField(max_length=20)
    #rows = TextField()
    processname = CharField(max_length=100, null=True)
    osthread = IntegerField()
    clientid = IntegerField(null=True)
    connectid = IntegerField(null=True)
    applicationname = CharField(max_length=100, null=True)
    usr = CharField(max_length=50, null=True)
    context = TextField(null=True)
    sql = TextField(null=True)
    cputime = IntegerField(default=0)
    memory = IntegerField(default=0)
    memorypeak = IntegerField(default=0)
    
    
class UsersCall(Model):
    date = DateTimeField(index=True)
    duration = IntegerField(default=0)
    duration_call = IntegerField(default=0)
    processname = CharField(max_length=100, null=True)
    applicationname = CharField(max_length=100, null=True)
    usr = CharField(max_length=50, null=True)
    context = TextField(null=True)
    
    
class DBCall(Model):
    date = DateTimeField(index=True)
    duration = IntegerField(default=0)    
    processname = CharField(max_length=100, null=True)
    context = TextField(null=True)
    sql = TextField(null=True)
    

class AppCall(Model):
    date = DateTimeField(index=True)
    duration = IntegerField(default=0)    
    processname = CharField(max_length=100, null=True)
    context = TextField(null=True)
    cputime = IntegerField(default=0)
    memory = IntegerField(default=0)
    memorypeak = IntegerField(default=0)