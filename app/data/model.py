from sqlalchemy import Column, Integer, String, DateTime
from app.utils.connection import Base


### Company ###
# Base is coming from the SQL Alchemy Base class created in utils/connection.py
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
# Base is coming from the SQL Alchemy Base class created in utils/connection.py
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
# Base is coming from the SQL Alchemy Base class created in utils/connection.py
class Vendor(Base):
    __tablename__ = "EMVendor"

    VendorID = Column(Integer, primary_key=True)
    VendorTitle = Column(String(255))
    VendorName = Column(String(255))
    VendorNameEng = Column(String(255))
    ShortName = Column(String(255))
    VendorAddr1 = Column(String(255))
    VendorAddr2 = Column(String(255))
    District = Column(String(255))
    Amphur = Column(String(255))
    Province = Column(String(255))
    PostCode = Column(String(255))
    TaxId = Column(String(25))
    ContTel = Column(String(25))
    ContFax = Column(String(25))
