from datetime import timedelta
from sqlite3 import IntegrityError
from typing import Annotated, Any, Dict, List
from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text, exc
from sqlalchemy.orm import Session
from app.auth.auth import (
    authenticate_user,
    create_access_token,
    fake_users_db,
    get_current_active_user,
    get_current_user,
)
from app.model import ACCESS_TOKEN_EXPIRE_MINUTES, Token, User, Vendor, VendorSchema
from app.utils.connection import get_session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Running api.py")
print(__name__)

apiApp = FastAPI(
    title="WinSpeed FastAPI", description="API for WinSpeed database", version="1.0.0"
)
# __all__ = ["app"]

# route handlers
@apiApp.get("/", tags=["App"])
async def read_root() -> dict:
    return {"message": "Welcome to " + apiApp.title}


@apiApp.get("/api/info", tags=["API"])
async def information() -> dict:
    return {"app_name": apiApp.title, "version": apiApp.version}


@apiApp.post("/token", tags=["Auth"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@apiApp.get("/users/me/", response_model=User, tags=["Auth"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


### Database ###
# GET Current Version
@apiApp.get(
    "/db/version/{dbNum}",
    tags=["Database"],
)
async def get_current_db_version(
    dbNum: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if dbNum is None:
        raise HTTPException(status_code=400, detail="dbNum is required")

    try:
        data = db.execute(text("""SELECT CHANGE_TRACKING_CURRENT_VERSION()"""))
        result = [int(row[0]) for row in data]
        return JSONResponse(content=jsonable_encoder({"version": sum(result), "database": dbNum})) 
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        # raise HTTPException(status_code=500, detail=f"This database does not allow change tracking")
        return JSONResponse(status_code=500, content={
            "error": f"This database does not allow change tracking",
            "version": None, 
            "database": dbNum
        })
    
def row_to_dict(row) -> Dict[str, Any]:
    return {column: value for column, value in row._mapping.items()}

def process_results(result) -> List[Dict[str, Any]]:
    return [row_to_dict(row) for row in result]

# GET Change Table Name
@apiApp.get(
    "/db/changed/{dbNum}/{version}",
    tags=["Database"],
)
async def get_changed_table(
    dbNum: int,
    version: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if dbNum is None:
        raise HTTPException(status_code=400, detail="dbNum is required")
    
    if version is None:
        raise HTTPException(status_code=400, detail="version is required")
    
    try:
        query = text("EXEC [api_getchangedtablename] @CurrentVersion = :version")
        result = db.execute(query, {"version": version})
        
        data = process_results(result)
        
        if not data:
            return {"data": None, "message": "No any chaged"}
        elif len(data) == 1:
            return {"data": data[0]}
        else:
            return {"data": data}

    except exc.SQLAlchemyError as db_error:
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
# GET Change dataset
@apiApp.get(
    "/db/changed/{dbNum}/{version}/detail",
    tags=["Database"],
)
async def get_changed_data(
    dbNum: int,
    version: int, 
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if dbNum is None:
        raise HTTPException(status_code=400, detail="dbNum is required")
    
    if version is None:
        raise HTTPException(status_code=400, detail="version is required")
    
    try:
        query = text("EXEC [api_getchangedset] @CurrentVersion = :version")
        result = db.execute(query, {"version": version})
        
        data = process_results(result)
        
        if not data:
            return {"data": None, "message": "No any chaged"}
        elif len(data) == 1:
            return {"data": data[0]}
        else:
            return {"data": data}

    except exc.SQLAlchemyError as db_error:
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


### Vendor ###
### CRUD #######
################


# GET ALL
# Response will be a LIST of data
@apiApp.get(
    "/vendors/all",
    response_model=List[VendorSchema],
    tags=["Vendors"],
)
async def get_data(
    dbNum: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    if dbNum is None:
        raise HTTPException(status_code=400, detail="dbNum is required")

    data = db.query(Vendor).all()
    return data


# GET Single
# Response will be a single data
@apiApp.get(
    "/vendors/{id}",
    response_model=VendorSchema,
    # dependencies=[Depends(JWTBearer())],
    tags=["Vendors"],
)
async def get_vendor_by_id(
    dbNum: int,
    id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    if dbNum is None:
        raise HTTPException(status_code=400, detail="dbNum is required")

    data = db.query(Vendor).filter(Vendor.VendorID == id).one_or_none()
    if not data:
        raise HTTPException(status_code=404, detail=f"Vendor with ID {id} not found")
    return data


# POST
# Response will be a single data after creation in the DB
@apiApp.post(
    "/vendors/new",
    response_model=VendorSchema,
    # dependencies=[Depends(JWTBearer())],
    tags=["Vendors"],
)
async def create_vendor(
    dbNum: int,
    data: VendorSchema,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    if dbNum is None:
        raise HTTPException(status_code=400, detail="dbNum is required")

    existing = db.query(Vendor).filter(Vendor.VendorID == data.VendorID).first()
    if existing:
        logger.warning(f"Vendor with ID {data.VendorID} already exists")
        raise HTTPException(
            status_code=400, detail="Vendor with this ID already exists"
        )

    try:
        new_data = Vendor(**data.dict())
        db.add(new_data)
        db.flush()
        db.commit()
        logger.info("Transaction committed")
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Database integrity error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred")

    return new_data


# PUT
# Response will be a single data after update in the DB
@apiApp.put(
    "/vendors/edit",
    response_model=VendorSchema,
    # dependencies=[Depends(JWTBearer())],
    tags=["Vendors"],
)
async def update_vendor(
    dbNum: int,
    dataUpd: VendorSchema,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    if dbNum is None:
        raise HTTPException(status_code=400, detail="dbNum is required")

    existing = db.query(Vendor).filter(Vendor.VendorID == dataUpd.VendorID).first()
    if not existing:
        logger.warning(f"Vendor with ID {id} not found")
        raise HTTPException(status_code=404, detail=f"Vendor with this ID not found")

    try:
        if existing:
            for key, value in dataUpd.dict(exclude_unset=True).items():
                setattr(existing, key, value)

            db.flush()
            db.commit()
            db.refresh(existing)
            logger.info("Transaction committed")
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Database integrity error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred")

    return existing


# DELETE
@apiApp.delete(
    "/vendors/del/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(JWTBearer())],
    tags=["Vendors"],
)
async def delete_vendor(
    dbNum: int,
    id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if dbNum is None:
        raise HTTPException(status_code=400, detail="dbNum is required")

    existing = db.query(Vendor).filter(Vendor.VendorID == id).first()
    if not existing:
        logger.warning(f"Vendor with ID {id} not found")
        raise HTTPException(status_code=404, detail=f"Vendor with this ID not found")

    try:
        if existing:
            db.delete(existing)
            db.flush()
            db.commit()
            logger.info("Transaction committed")
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Database integrity error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred")
