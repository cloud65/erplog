from os.path import join as path_join, split as path_split, normpath
from os import sep as os_sep
from re import search as re_search, compile as re_compile
from datetime import datetime
import glob
import paramiko
import stat

class RemoteFileReader:
    def __init__(self, addr, key_file):
        username, host = tuple(addr.split('@'))
        sshkey = paramiko.RSAKey.from_private_key_file(key_file)
        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=host, username=username, allow_agent=True, pkey=sshkey)

        self.client = ssh_client.open_sftp()     
        
    def glob(self, path, pattern):
        p = re_compile(pattern)
        root = self.client.listdir(path)
        file_list = []
        for f in (f"{path}/{entry}" for entry in root):
            f_stat = self.client.stat(f)
            # ... if it is a directory call paramiko_glob recursively.
            if stat.S_ISDIR(f_stat.st_mode):
                file_list += self.glob(f, pattern)
            # ... if it is a file, check the name pattern and append it to file_list.
            elif p.match(f):
                file_list.append(f)
        return file_list
        
    def open(self, filename, mode='r'):
        return self.client.open(filename, mode)

# Класс записи лога
class LogRow:
    def __init__(self, filename, row):
        self.date = datetime.strptime(f"{filename}{row.split('-')[0]}", '%y%m%d%H%M:%S.%f')
        self.__rows = [row]
        
    def add_row(self, row):
        self.__rows.append(row)
        
    def update_props(self):
        s = "\n".join(self.__rows)
        props = s.split(',')        
        self.event = props[1]
        self.duration = int(props[0].split('-')[1])
        
        while s!="": # разобъем на key=value с учетом многострочных значений
            pos = s.find(',')    
            if pos==-1:
                pos = len(s)
            val = s[:pos]    
            key_val = val.split("=")    
            if len(key_val)>1:        
                key = key_val[0].strip().split(':')[-1].lower()
                if key_val[1] and key_val[1][0] in ['"', "'"]:
                    pos = s.find('=')+1
                    s = s[pos+1:]            
                    pos = s.find(key_val[1][0])
                    val = s[:pos]
                    #print('****', s)
                else:
                    val = key_val[1].strip()
                setattr(self, key, val)        
            s = s[pos+1:]
                
    
    def __str__(self):
        return f'{self.date} {self.event} {self.__rows[0]}'
        
    def __getattr__(self, name):
        return None
        
    def as_dict(self):
        return {
            "date": self.date,
            "event": self.event,
            #"rows": "\n".join(self.__rows),
            "duration": self.duration,
            "processname": self.processname,
            "osthread": self.osthread,
            "clientid": self.clientid,
            "connectid": self.connectid,
            "applicationname": self.applicationname,
            "usr": self.usr,
            "context": self.context,            
            "sql": self.sql,
            "cputime": self.cputime or 0,
            "memory": self.memory or 0,
            "memorypeak": self.memorypeak or 0, 
        }
    

# Класс для парсинга
class LogParser:
    def __init__(self, path, sftp=None):
        self.path = path
        self.sftp = sftp
        self.__chekpoints = {} 
        self.__active_proc = [] # храним актуальные процессы

    def set_chekpoints(self, chekpoints):
        self.__chekpoints = { val[0]: val[1] for val in chekpoints }
        
    def get_chekpoints(self):
        return [(proc, chp) for proc, chp in self.__chekpoints.items() if proc in self.__active_proc]

    def get_files(self):
        if self.sftp is None:
            return [f for f in glob.glob(path_join(self.path, '*.log'), recursive=True)]            
        else:
            return [f for f in self.sftp.glob(self.path, '.*\.log')] 
    
        
    def get_data(self):             
        # лог запись может содержать перевод строки, поэтому мы сначала создадим массив строк
        data = []
        for filename in self.get_files():
            try: # Обернем в try, так как за время чтения следующий файл может удалится
                if self.sftp is None:
                    file = open(filename, mode="r", encoding="utf-8-sig")
                else:
                    file = self.sftp.open(filename, mode="r")
            except:
                continue
        
            path_and_name = path_split(filename)
            
            #Выделим checkpoint
            proc = normpath(path_and_name[0]).split(os_sep)[-1]
            checkpoint = self.__chekpoints.get(proc, datetime(1970,1,1))
            self.__active_proc.append(proc)
            
            # дата и час берем из имени файла            
            date_log = path_and_name[1].split('.')[0]     
            
            for line in file:
                str_line = line.strip().encode().decode('utf-8-sig')
                if not str_line:
                    continue
                if re_search(r'^\d{2}\:\d{2}\.\d{6}\-\d+\,.+', str_line):
                    if len(data): # Обновим свойства предыдущей записи
                        data[-1].update_props()                    
                    row = LogRow(date_log, str_line)
                    if row.date>checkpoint:                                                  
                        data.append(row)
                else:
                    if row.date>checkpoint:
                        data[-1].add_row(line.strip())
            file.close()
            if len(data):
                self.__chekpoints[proc] = data[-1].date
                data[-1].update_props()
        return data        