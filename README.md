#### Предварительный

## Анализ логов работы ERP-системы


### Реализует ETL-процесс формирования витрин данных для анализа производительности ERP-системы.

* src - содержит скрипты и вспомогательные файлы, реализующие все этапы процесса
* doc - документация


### Установка

Настроить сбор технологического журнала (https://v8.1c.ru/platforma/tehnologicheskiy-zhurnal/) используя параметрф файла **1c/logcfg.xml**

#### Сервер витрин
Созаем каталог
```mkdir -p /opt/erp-log```

Помещаем в него содержимое **src**
Создаем виртуальное окрущение python и устанавливаем зависимости
```
cd /opt/erp-log
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Создаем пользователя и группу:
```
useradd erplog -d /opt/erp-log -M
groupadd erplog
usermod -aG erplog erplog
chown erplog.erplog -R /opt/erp-log
```


создаем ссылки:
Веб-интерфейс
```
ln -s /opt/erp-log/erp-log-gui.service /etc/systemd/system/
```
Формирование слоев каждый час
```
ln -s /opt/erp-log/update-layers.sh /etc/cron.hourly/
```

запускаем GUI
```
systemctl daemon-reload
systemctl start erp-log-gui.service
```

#### Если разрешено запускать скрипт формирования первого слоя на сервере приложений
Созаем каталог
```mkdir -p /opt/erp-log```

Помещаем в него содержимое **src**
Создаем виртуальное окрущение python и устанавливаем зависимости
```
cd /opt/erp-log
python3 -m venv venv
pip install -r requirements.txt
```
Созаем ссылку
```
ln -s /opt/erp-log/update-layers.sh /etc/cron.hourly/
```
В файле **update-layers.sh** оставляем вызов только *1_log_parser.py*,
а на сервере витрин из него его исключаем

#### Если разрешено получать данные с сервера приложений только по ssh
Необходимо в файле **config.json** указать
```
"ssh": "user@hostame",
"ssh_key": "Путь к ключу ssh"
```
иначе оставить пустые значения
