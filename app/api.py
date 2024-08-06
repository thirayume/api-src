from datetime import datetime, timedelta
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import List
from sqlalchemy.orm import Session
from app.data import model, schema
from app.utils.connection import get_db

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
# app.add_middleware(HTTPSRedirectMiddleware) # FORCE HTTPS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    username: str
    email: str = None
    full_name: str = None
    disabled: bool = None


class UserInDB(User):
    hashed_password: str


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": pwd_context.hash("secret"),
        "disabled": False,
    }
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username)
    if user is None:
        raise credentials_exception
    return user


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


### DB Version ###
##################


@app.post("/dbs/{db_id}/select")
async def set_current_db(
    db_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@app.get("/dbs/{db_id}/version")
async def get_current_version(
    db_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@app.get("/dbs/{db_id}/changes/{version}")
async def get_changes(
    db_id: int,
    version: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@app.post("/dbs/{db_id}/replicate/{version}")
async def replicate(
    db_id: int,
    version: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


### Company ###
### CRUD #######
################


# GET ALL
# Response will be a LIST of data
@app.get("/company/all", response_model=List[schema.Company])
async def get_all_companies(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    query = db.query(model.Company)
    datas = query.all()
    return datas


# GET Single
# Response will be a single data
@app.get("/company/{id}")
async def get_company_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(model.Company).filter(model.Company.CompID == id)
    data = query.one_or_none()
    if not data:
        raise HTTPException(status_code=404, detail=f"Company with ID {id} not found")
    return data


# POST
# Response will be a single data after creation in the DB
@app.post("/company/new", response_model=schema.Company)
async def create_company(
    data: schema.CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # create an instance of the ORM model from the schema instance from the request body
    new_data = model.Company(
        CompName=data.CompName,
        CompNameEng=data.CompNameEng,
        Addr1=data.Addr1,
        Addr1Eng=data.Addr1Eng,
        Addr2=data.Addr2,
        Addr2Eng=data.Addr2Eng,
        Addr3=data.Addr3,
        Addr3Eng=data.Addr3Eng,
        TaxID=data.TaxID,
        TaxID13=data.TaxID13,
        Tel=data.Tel,
        Fax=data.Fax,
        Email=data.Email,
    )
    # add it to the session and commit it
    db.add(new_data)

    db.commit()
    db.refresh(new_data)

    return new_data


# PUT
# Response will be a single data after update in the DB
@app.put("/company/{id}", response_model=schema.Company)
async def update_company(
    id: int,
    dataUpd: schema.Company,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Company, id)

    # update data with the data from request body (if data with the given id was found)
    if data:
        data.CompName = dataUpd.CompName
        data.CompNameEng = dataUpd.CompNameEng
        data.Addr1 = dataUpd.Addr1
        data.Addr1Eng = dataUpd.Addr1Eng
        data.Addr2 = dataUpd.Addr2
        data.Addr2Eng = dataUpd.Addr2Eng
        data.Addr3 = dataUpd.Addr3
        data.Addr3Eng = dataUpd.Addr3Eng
        data.TaxID = dataUpd.TaxID
        data.TaxID13 = dataUpd.TaxID13
        data.Tel = dataUpd.Tel
        data.Fax = dataUpd.Fax
        data.Email = dataUpd.Email

        db.commit()
        db.refresh(data)

    # check if data with given id exists. If not, raise exception and return 404 not found response
    if not data:
        raise HTTPException(status_code=404, detail=f"Vendor with ID {id} not found")

    return data


# DELETE
@app.delete("/company/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Company, id)

    # check if data with given id exists and call delete
    if data:
        db.delete(data)
        db.commit()


### Branch ###
### CRUD #######
################


# GET ALL
# Response will be a LIST of data
@app.get("/branch/all", response_model=List[schema.Branch])
async def get_all_branches(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    query = db.query(model.Branch)
    datas = query.all()
    return datas


# GET Single
# Response will be a single data
@app.get("/branch/{id}")
async def get_branch_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(model.Branch).filter(model.Branch.BrchID == id)
    data = query.one_or_none()
    if not data:
        raise HTTPException(status_code=404, detail=f"Branch with ID {id} not found")
    return data


# POST
# Response will be a single data after creation in the DB
@app.post("/branch/new", response_model=schema.Branch)
async def create_branch(
    data: schema.BranchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # create an instance of the ORM model from the schema instance from the request body
    new_data = model.Branch(
        BrchCode=data.BrchCode,
        BrchName=data.BrchName,
        BrchNameEng=data.BrchNameEng,
        BrchAddr1=data.BrchAddr1,
        BrchAddr1Eng=data.BrchAddr1Eng,
        BrchAddr2=data.BrchAddr2,
        BrchAddr2Eng=data.BrchAddr2Eng,
        BrchAddr3=data.BrchAddr3,
        BrchAddr3Eng=data.BrchAddr3Eng,
        Tel=data.Tel,
        Fax=data.Fax,
        Email=data.Email,
    )
    # add it to the session and commit it
    db.add(new_data)

    db.commit()
    db.refresh(new_data)

    return new_data


# PUT
# Response will be a single data after update in the DB
@app.put("/branch/{id}", response_model=schema.Branch)
async def update_branch(
    id: int,
    dataUpd: schema.Branch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Branch, id)

    # update data with the data from request body (if data with the given id was found)
    if data:
        data.BrchCode = dataUpd.BrchCode
        data.BrchName = dataUpd.BrchName
        data.BrchNameEng = dataUpd.BrchNameEng
        data.BrchAddr1 = dataUpd.BrchAddr1
        data.BrchAddr1Eng = dataUpd.BrchAddr1Eng
        data.BrchAddr2 = dataUpd.BrchAddr2
        data.BrchAddr2Eng = dataUpd.BrchAddr2Eng
        data.BrchAddr3 = dataUpd.BrchAddr3
        data.BrchAddr3Eng = dataUpd.BrchAddr3Eng
        data.Tel = dataUpd.Tel
        data.Fax = dataUpd.Fax
        data.Email = dataUpd.Email

        db.commit()
        db.refresh(data)

    # check if data with given id exists. If not, raise exception and return 404 not found response
    if not data:
        raise HTTPException(status_code=404, detail=f"Branch with ID {id} not found")

    return data


# DELETE
@app.delete("/branch/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Branch, id)

    # check if data with given id exists and call delete
    if data:
        db.delete(data)
        db.commit()


### Vendor ###
### CRUD #######
################


# GET ALL
# Response will be a LIST of data
@app.get("/vendor/all", response_model=List[schema.Vendor])
async def get_all_vendors(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    query = db.query(model.Vendor)
    datas = query.all()
    return datas


# GET Single
# Response will be a single data
@app.get("/vendor/{id}")
async def get_vendor_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(model.Vendor).filter(model.Vendor.VendorID == id)
    data = query.one_or_none()
    if not data:
        raise HTTPException(status_code=404, detail=f"Vendor with ID {id} not found")
    return data


# POST
# Response will be a single data after creation in the DB
@app.post("/vendor/new", response_model=schema.Vendor)
async def create_vendor(
    data: schema.VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # create an instance of the ORM model from the schema instance from the request body
    new_data = model.Vendor(
        VendorTitle=data.VendorTitle,
        VendorName=data.VendorName,
        VendorNameEng=data.VendorNameEng,
        ShortName=data.ShortName,
        VendorAddr1=data.VendorAddr1,
        VendorAddr2=data.VendorAddr2,
        District=data.District,
        Amphur=data.Amphur,
        Province=data.Province,
        PostCode=data.PostCode,
        TaxId=data.TaxId,
        ContTel=data.ContTel,
        ContFax=data.ContFax,
    )
    # add it to the session and commit it
    db.add(new_data)

    db.commit()
    db.refresh(new_data)

    return new_data


# PUT
# Response will be a single data after update in the DB
@app.put("/vendor/{id}", response_model=schema.Vendor)
async def update_vendor(
    id: int,
    dataUpd: schema.Vendor,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Vendor, id)

    # update data with the data from request body (if data with the given id was found)
    if data:
        data.VendorTitle = dataUpd.VendorTitle
        data.VendorName = dataUpd.VendorName
        data.VendorNameEng = dataUpd.VendorNameEng
        data.ShortName = dataUpd.ShortName
        data.VendorAddr1 = dataUpd.VendorAddr1
        data.VendorAddr2 = dataUpd.VendorAddr2
        data.District = dataUpd.District
        data.Amphur = dataUpd.Amphur
        data.Province = dataUpd.Province
        data.PostCode = dataUpd.PostCode
        data.TaxId = dataUpd.TaxId
        data.ContTel = dataUpd.ContTel
        data.ContFax = dataUpd.ContFax

        db.commit()
        db.refresh(data)

    # check if data with given id exists. If not, raise exception and return 404 not found response
    if not data:
        raise HTTPException(status_code=404, detail=f"Vendor with ID {id} not found")

    return data


# DELETE
@app.delete("/vendor/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Vendor, id)

    # check if data with given id exists and call delete
    if data:
        db.delete(data)
        db.commit()


### Product ###
### CRUD #######
################


# GET ALL
# Response will be a LIST of data
@app.get("/product/all", response_model=List[schema.Vendor])
async def get_all_products(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    query = db.query(model.Vendor)
    datas = query.all()
    return datas


# GET Single
# Response will be a single data
@app.get("/product/{id}")
async def get_product_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(model.Vendor).filter(model.Vendor.VendorID == id)
    data = query.one_or_none()
    if not data:
        raise HTTPException(status_code=404, detail=f"Vendor with ID {id} not found")
    return data


# POST
# Response will be a single data after creation in the DB
@app.post("/product/new", response_model=schema.Vendor)
async def create_product(
    data: schema.VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # create an instance of the ORM model from the schema instance from the request body
    new_data = model.Vendor(
        CreditDays=data.CreditDays,
        VendorName=data.VendorName,
        VendorNameEng=data.VendorNameEng,
        VendorTitle=data.VendorTitle,
        VendorCode=data.VendorCode,
        TaxId=data.TaxId,
    )
    # add it to the session and commit it
    db.add(new_data)

    db.commit()
    db.refresh(new_data)

    return new_data


# PUT
# Response will be a single data after update in the DB
@app.put("/product/{id}", response_model=schema.Vendor)
async def update_product(
    id: int,
    dataUpd: schema.Vendor,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Vendor, id)

    # update data with the data from request body (if data with the given id was found)
    if data:
        data.CreditDays = dataUpd.CreditDays
        data.VendorName = dataUpd.VendorName
        data.VendorNameEng = dataUpd.VendorNameEng
        data.VendorTitle = dataUpd.VendorTitle
        data.VendorCode = dataUpd.VendorCode
        data.TaxId = dataUpd.TaxId

        db.commit()
        db.refresh(data)

    # check if data with given id exists. If not, raise exception and return 404 not found response
    if not data:
        raise HTTPException(status_code=404, detail=f"Vendor with ID {id} not found")

    return data


# DELETE
@app.delete("/product/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Vendor, id)

    # check if data with given id exists and call delete
    if data:
        db.delete(data)
        db.commit()


### Purchase Order ###
### CRUD #######
################


# GET ALL
# Response will be a LIST of data
@app.get("/prpo/all", response_model=List[schema.Vendor])
async def get_all_prpos(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    query = db.query(model.Vendor)
    datas = query.all()
    return datas


# GET Single
# Response will be a single data
@app.get("/prpo/{id}")
async def get_prpo_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(model.Vendor).filter(model.Vendor.VendorID == id)
    data = query.one_or_none()
    if not data:
        raise HTTPException(status_code=404, detail=f"Vendor with ID {id} not found")
    return data


# # POST
# # Response will be a single data after creation in the DB
# @app.post("/prpo/new", response_model=schema.Vendor)
# async def create_prpo(
#     data: schema.VendorCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     # create an instance of the ORM model from the schema instance from the request body
#     new_data = model.Vendor(
#         CreditDays=data.CreditDays,
#         VendorName=data.VendorName,
#         VendorNameEng=data.VendorNameEng,
#         VendorTitle=data.VendorTitle,
#         VendorCode=data.VendorCode,
#         TaxId=data.TaxId,
#     )
#     # add it to the session and commit it
#     db.add(new_data)

#     db.commit()
#     db.refresh(new_data)

#     return new_data


# PUT
# Response will be a single data after update in the DB
@app.put("/prpo/{id}", response_model=schema.Vendor)
async def update_prpo(
    id: int,
    dataUpd: schema.Vendor,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Vendor, id)

    # update data with the data from request body (if data with the given id was found)
    if data:
        data.CreditDays = dataUpd.CreditDays
        data.VendorName = dataUpd.VendorName
        data.VendorNameEng = dataUpd.VendorNameEng
        data.VendorTitle = dataUpd.VendorTitle
        data.VendorCode = dataUpd.VendorCode
        data.TaxId = dataUpd.TaxId

        db.commit()
        db.refresh(data)

    # check if data with given id exists. If not, raise exception and return 404 not found response
    if not data:
        raise HTTPException(status_code=404, detail=f"Vendor with ID {id} not found")

    return data


# DELETE
@app.delete("/prpo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prpo(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Vendor, id)

    # check if data with given id exists and call delete
    if data:
        db.delete(data)
        db.commit()


# PUT
# Response will be a single data after update in the DB
@app.put("/prpo/{id}/approve", response_model=schema.Vendor)
async def approve_prpo(
    id: int,
    dataUpd: schema.Vendor,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Vendor, id)

    # update data with the data from request body (if data with the given id was found)
    if data:
        data.CreditDays = dataUpd.CreditDays
        data.VendorName = dataUpd.VendorName
        data.VendorNameEng = dataUpd.VendorNameEng
        data.VendorTitle = dataUpd.VendorTitle
        data.VendorCode = dataUpd.VendorCode
        data.TaxId = dataUpd.TaxId

        db.commit()
        db.refresh(data)

    # check if data with given id exists. If not, raise exception and return 404 not found response
    if not data:
        raise HTTPException(status_code=404, detail=f"Vendor with ID {id} not found")

    return data


# PUT
# Response will be a single data after update in the DB
@app.put("/prpo/{id}/void", response_model=schema.Vendor)
async def void_prpo(
    id: int,
    dataUpd: schema.Vendor,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = db.get(model.Vendor, id)

    # update data with the data from request body (if data with the given id was found)
    if data:
        data.CreditDays = dataUpd.CreditDays
        data.VendorName = dataUpd.VendorName
        data.VendorNameEng = dataUpd.VendorNameEng
        data.VendorTitle = dataUpd.VendorTitle
        data.VendorCode = dataUpd.VendorCode
        data.TaxId = dataUpd.TaxId

        db.commit()
        db.refresh(data)

    # check if data with given id exists. If not, raise exception and return 404 not found response
    if not data:
        raise HTTPException(status_code=404, detail=f"Vendor with ID {id} not found")

    return data
