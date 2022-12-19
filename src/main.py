from datetime import datetime
from bottle import request, get, route, run, template
from reports import *
from database import init_database
from args import * 

OPTIONS = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "option": "30",
    "btn_db_call": "is-info",
    "btn_app_call": "is-text",
    "btn_app_mem": "is-text",
    "btn_user_call": "is-text",
}

def get_template():
    return """
    <!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
    <title>Анализ ERP-системы</title>
    <style>
        .report td {
            padding: 4px;
        }
        .wrap {
            max-width: 30vw;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .pointer {
            cursor: pointer;
        }        
        .popup {
            display: none;
            position: absolute;            
            z-index: 1;
            background: #e9e199;
            padding: 8px;
            font-size: 1rem;
            color: #000;
            border-radius: 2px;
            animation: fadeIn 0.6s;
        }
    </style>
</head>
<body>
    <form method="GET" action="report">
    <section class="section">
    <div class="container">
      <h1 class="title">Анализ производительности ERP-системы</h1>
      <p class="subtitle">
        Укажите вид отчета и параметры
      </p>
          <div class="field-body">
            <div class="field">
             <label class="label">На дату</label>
              <p class="control is-expanded">
                <input class="input" type="date" name="date" value="{{ date }}">            
              </p>
            </div>
            <div class="field">
             <label class="label">Параметр</label>
              <p class="control is-expanded">
                <input class="input" type="number" name="option" value="{{ option }}">            
              </p>
            </div>
        </div>
        <div style='padding:0.5em;'>
          <button class="button {{ btn_db_call }}" name="report" value="db_call">Длительные запросы к СУБД</button>
          <button class="button {{ btn_app_call }}" name="report" value="app_call">Длительные методы сервера приложений</button>          
          <button class="button {{ btn_user_call }}" name="report" value="user_call">Блокировка интерфейса пользователя</button>
          <button class="button {{ btn_app_mem }}" name="report" value="app_mem">Памятиемкие методы сервера приложений (топ)</button>
        </div> 
    </div>
  
    <report>  
    
  </section>
  
  </form>
  
</body>
<script>  
    document.addEventListener("DOMContentLoaded", function(){
        const td = document.querySelectorAll('td');
        for (i = 0; i < td.length; ++i) {
            if (td[i].textContent.length>50){
                td[i].innerHTML = `<div class="wrap pointer">${td[i].textContent}</div>
                    <div class='popup' style='display:none'></div>`;
                td[i].addEventListener('mouseover', ({target}) => {
                    const div=target.querySelector('.popup')
                    if (div){
                        div.style.display='block';
                        div.innerHTML=target.textContent
                    }
                }, false);
                td[i].addEventListener('mouseleave', ({target}) => {
                    const div=target.querySelector('.popup')
                    if (div){
                        div.style.display='none';
                        div.innerHTML=''
                    }
                }, false);
            } 
        }
    });
</script>
</html>
"""


@route('/')
def index():
    return get_report()


@get('/report')
def get_report():
    date = request.query.get('date', datetime.now().strftime("%Y-%m-%d"))
    option = request.query.get('option', "30")
    report = request.query.get('report', 'app_call')
    OPTIONS['date'] = date
    OPTIONS['option'] = option
    for key in OPTIONS.keys():
        if 'is-' in OPTIONS[key]:
            OPTIONS[key] = "is-info" if key=="btn_"+report else "is-text"
    
    
    func = lambda a,b: ""
    if report=="user_call":
        func = report_user_call
    elif report=="db_call":
        func = report_db_call
    elif report=="app_call":
        func = report_app_call
    elif report=="app_mem":
        func = report_app_mem

        
    try:
        data = func(datetime.strptime(date, "%Y-%m-%d"), float(option))
    except Exception as e:
        data = str(e)
    
    return template(get_template().replace("<report>", data), **OPTIONS)


if __name__ == '__main__':
    args = get_args()
    init_database(args.psql_url, drop=False)
    run(host='0.0.0.0', port=8002, debug=True)