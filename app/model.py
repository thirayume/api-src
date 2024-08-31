from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String
from app.utils.connection import Base

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": pwd_context.hash("secret"),
        "disabled": False,
    }
}

ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


### Company ###
# Create Schema (Pydantic Model)
class CompanySchema(BaseModel):
    CompID: int | None = None
    CompName: str | None = None
    CompNameEng: str | None = None
    Addr1: str | None = None
    Addr1Eng: str | None = None
    Addr2: str | None = None
    Addr2Eng: str | None = None
    Addr3: str | None = None
    Addr3Eng: str | None = None
    TaxID: str | None = None
    TaxID13: str | None = None
    Tel: str | None = None
    Fax: str | None = None
    Email: str | None = None


class Company(CompanySchema):
    # Orm Mode is used to support models that map to ORM objects (sqlAlchemy)
    class Config:
        from_attributes = True


class Company(Base):
    __tablename__ = "EMComp"

    CompID = Column(Integer, primary_key=True)
    CompName = Column(String(255))
    CompNameEng = Column(String(255))
    Addr1 = Column(String(255))
    Addr1Eng = Column(String(255))
    Addr2 = Column(String(255))
    Addr2Eng = Column(String(255))
    Addr3 = Column(String(255))
    Addr3Eng = Column(String(255))
    TaxID = Column(String(25))
    TaxID13 = Column(String(25))
    Tel = Column(String(25))
    Fax = Column(String(25))
    Email = Column(String(25))


### Branch ###
# Create Schema (Pydantic Model)
class BranchSchema(BaseModel):
    BrchID: int | None = None
    BrchCode: str | None = None
    BrchName: str | None = None
    BrchNameEng: str | None = None
    BrchAddr1: str | None = None
    BrchAddr1Eng: str | None = None
    BrchAddr2: str | None = None
    BrchAddr2Eng: str | None = None
    BrchAddr3: str | None = None
    BrchAddr3Eng: str | None = None
    Tel: str | None = None
    Fax: str | None = None
    Email: str | None = None


class Branch(BranchSchema):
    # Orm Mode is used to support models that map to ORM objects (sqlAlchemy)
    class Config:
        from_attributes = True


class Branch(Base):
    __tablename__ = "EMBrch"

    BrchID = Column(Integer, primary_key=True)
    BrchCode = Column(String(25))
    BrchName = Column(String(255))
    BrchNameEng = Column(String(255))
    BrchAddr1 = Column(String(255))
    BrchAddr1Eng = Column(String(255))
    BrchAddr2 = Column(String(255))
    BrchAddr2Eng = Column(String(255))
    BrchAddr3 = Column(String(255))
    BrchAddr3Eng = Column(String(255))
    Tel = Column(String(25))
    Fax = Column(String(25))
    Email = Column(String(25))


### Vendor ###
# Create Schema (Pydantic Model)
class VendorSchema(BaseModel):
    VendorID: int | None = 0
    VendorTitle: str | None = None
    VendorName: str | None = None
    VendorNameEng: str | None = None
    ShortName: str | None = None
    VendorCode: str | None = None
    VendorType: str | None = 1
    VendorAddr1: str | None = None
    VendorAddr2: str | None = None
    District: str | None = None
    Amphur: str | None = None
    Province: str | None = None
    PostCode: str | None = None
    TaxId: str | None = None
    ContTel: str | None = None
    ContFax: str | None = None


class Vendor(VendorSchema):
    # Orm Mode is used to support models that map to ORM objects (sqlAlchemy)
    class Config:
        from_attributes = True


class Vendor(Base):
    __tablename__ = "EMVendor"

    VendorID = Column(
        Integer, primary_key=True, autoincrement=False
    )  # Primary key, not auto-incrementing
    VendorTitle = Column(String(255))
    VendorName = Column(String(255))
    VendorNameEng = Column(String(255))
    ShortName = Column(String(255))
    VendorCode = Column(String(255))
    VendorType = Column(String(255))
    VendorAddr1 = Column(String(255))
    VendorAddr2 = Column(String(255))
    District = Column(String(255))
    Amphur = Column(String(255))
    Province = Column(String(255))
    PostCode = Column(String(255))
    TaxId = Column(String(25))
    ContTel = Column(String(25))
    ContFax = Column(String(25))
