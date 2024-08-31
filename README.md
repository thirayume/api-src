# WinSpeed API App

## 1.Install the requirements
```python -m pip install --upgrade pip```
```pip install SQLAlchemy pymssql pyodbc pydantic-settings fastapi[all] python-multipart passlib[bcrypt] pyjwt python-decouple uvicorn```
or using this,
```pip install -r requirements.txt```

## 2.Create .env.sample file and put this information
```
DRIVER_1="SQL Server"
USERNAME_1="your_user"
PSSWD_1="your_password"
SERVERNAME_1="localhost"
DBNAME_1="your_database"
SECRET_1="your_secret"
ALGORITHM_1="HS256"
```

## 2.Startup API Server
```sh
python main.py
```

## 3.Test at Swagger Doc
Built-in Swagger Documentation is available at: [api-docs](http://localhost:8000/docs)