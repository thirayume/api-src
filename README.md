# API App

## 1.Install Dependencies
```py -m pip install --upgrade pip```
```pip install SQLAlchemy pymssql pyodbc pydantic-settings fastapi[all] python-multipart passlib[bcrypt] pyjwt uvicorn```

## 2.Create .env.sample file and put this information
```
DRIVER="SQL Server"
USERNAME="your_user"
PSSWD="your_password"
SERVERNAME="localhost"
DB = "your_database"
```

## 2.Startup API Server
```python main.py```

## 3.Swagger Doc
Built-in Swagger Documentation is available at: [api-docs](http://localhost:8000/docs)