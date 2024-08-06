# API App

## 1.Install Dependencies
```pip install SQLAlchemy pymssql pydantic-settings fastapi[all] python-multipart passlib[bcrypt] pyjwt uvicorn```

## 2.Create .env.sample file and put this information
```DRIVER=\"\"
USERNAME=
PSSWD = ""
SERVERNAME = ""
INSTANCENAME = ""
DB = ""```

## 2.Startup API Server
```python main.py```

## 3.Swagger Doc
Built-in Swagger Documentation is available at: [api-docs](http://localhost:8000/docs)