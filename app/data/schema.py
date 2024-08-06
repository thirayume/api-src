from pydantic import BaseModel


### Company ###
# Create Schema (Pydantic Model)
class CompanyBase(BaseModel):
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


class CompanyCreate(CompanyBase):
    pass


class Company(CompanyBase):
    CompID: int

    # Orm Mode is used to support models that map to ORM objects (sqlAlchemy)
    class Config:
        from_attributes = True


### Branch ###
# Create Schema (Pydantic Model)
class BranchBase(BaseModel):
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


class BranchCreate(BranchBase):
    pass


class Branch(BranchBase):
    BrchID: int

    # Orm Mode is used to support models that map to ORM objects (sqlAlchemy)
    class Config:
        from_attributes = True


### Vendor ###
# Create Schema (Pydantic Model)
class VendorBase(BaseModel):
    VendorTitle: str | None = None
    VendorName: str | None = None
    VendorNameEng: str | None = None
    ShortName: str | None = None
    VendorAddr1: str | None = None
    VendorAddr2: str | None = None
    District: str | None = None
    Amphur: str | None = None
    Province: str | None = None
    PostCode: str | None = None
    TaxId: str | None = None
    ContTel: str | None = None
    ContFax: str | None = None


class VendorCreate(VendorBase):
    pass


class Vendor(VendorBase):
    VendorID: int

    # Orm Mode is used to support models that map to ORM objects (sqlAlchemy)
    class Config:
        from_attributes = True
