
# Export SonarQube issues to HTML    
    
## Инструкция  

* Перейти в http://localhost:9000/account/security 
* Ввести название токена, тип User Token, нажать кнопку Generate
* Скопировать токен и вставить в `config.toml`
* Также в `config.toml` отредактировать другие настройки

В командной строке:
  
* `python -m venv ./venv`  
  
### Windows  
* `./venv/Scripts/Activate.ps1 - для PowerShell или ./venv/Scripts/activate.bat - для cmd`  
* `pip install -r requirements.txt`  
* `python main.py`  
  
### Linux  
* `./venv/bin/pip install -r requirements.txt`  
* `./venv/bin/python main.py`
