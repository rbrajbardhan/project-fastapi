from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware  

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

#App
app=FastAPI(
    title="Employee Management Api",
    version="1.0",
)

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Need to be changed in future
    allow_creedentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Database
DATABASE_URL = "sqlite:///./app.db"

engine=create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal=sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base=declarative_base()

#Models
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname=Column(String)
    email = Column(String, unique=True)
    password = Column(String)

    employs=relationship("EmployDB", back_populates="owner") # establishing relationship with EmployDB

class EmployDB(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name=Column(String)
    email = Column(String, unique=True)
    isOnProject=Column(Boolean)
    experience=Column(Integer)
    completed=Column(Integer)
    description=Column(String)

    user_id=Column(Integer, ForeignKey("users.id"))
    owner=relationship("UserDB", back_populates="employs")

Base.metadata.create_all(bind=engine)

# Schemas
class UserCreate(BaseModel):
    id: int
    fullname:str
    email: str

    class config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    fullname:str
    email: str

    class config:
        orm_mode = True

class EmployCreate(BaseModel):
    fullname:str
    email: str
    isOnProject:bool
    experience:int
    completed:int
    description:str


class Token(BaseModel):
    access_token: str
    token_type: str


# security
SECRET_KEY = "SUPERSECRETS#####"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)

def hash_password(password:str) -> str:
    return pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token
    
def get_current_user(token:str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email=payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid Token",
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token error",
        )
    user=db.query(UserDB).filter(UserDB.email==email).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )
    return user


API_V1="/api/v1"

# Register
@app.post(API_V1 + "/register", response_model=UserResponse)
def register_user(user:UserCreate, db: Session=Depends(get_db)):
    existing=db.query(UserDB).filter(UserDB.email==user.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )
    new_user=UserDB(
        fullname=user.fullname,
        email=user.email,
        password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login
@app.post(API_V1 + "/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm=Depends(), 
    db: Session=Depends(get_db)
    ):
    user=db.query(UserDB).filter(UserDB.email==form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid Email",
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid Password",
        )
    access_token=create_access_token(data={"email": user.email})
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@app.get(API_V1 + "/dashboard")
def dashboard(current_user: UserDB=Depends(get_current_user)):
    return {
        "fullname": current_user.fullname,
        "email": current_user.email,
        "total_employees": len(current_user.employs),
    }

# creating employee
@app.post(API_V1 + "/employees")
def create_employ(
    employ: EmployCreate,
    current_user: UserDB=Depends(get_current_user), 
    db: Session=Depends(get_db)
    ):
    new_employ=EmployDB(
        name=employ.fullname,
        email=employ.email,
        isOnProject=employ.isOnProject,
        experience=employ.experience,
        completed=employ.completed,
        description=employ.description,
        owner=current_user
    )
    db.add(new_employ)
    db.commit()
    # db.refresh(new_employ)
    return {
        "message": "Employee created successfully"
        }

# get all users
@app.get(API_V1 + "/employs")
def get_employs(
    current_user: UserDB=Depends(get_current_user), 
    db: Session=Depends(get_db)
    ):
    return current_user.employs

#get single user
@app.get(API_V1 + "/employs/{id}")
def get_employ(
    id: int,
    current_user: UserDB=Depends(get_current_user), 
    db: Session=Depends(get_db)
    ):
    employ=db.query(EmployDB).filter(EmployDB.id==id).first()
    if not employ:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )
    return employ

# update employe
@app.put(API_V1 + "/employs/{id}")
def update_employ(
    id: int,
    employ: EmployCreate,
    current_user: UserDB=Depends(get_current_user), 
    db: Session=Depends(get_db)
    ):
    employ=db.query(EmployDB).filter(EmployDB.id==id).first()
    if not employ:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )
    employ.name=employ.fullname
    employ.email=employ.email
    employ.isOnProject=employ.isOnProject
    employ.experience=employ.experience
    employ.completed=employ.completed
    employ.description=employ.description

    db.commit()
    return {
        "message": "Employee updated successfully"
        }

# delete employee
@app.delete(API_V1 + "/employs/{id}")
def delete_employ(
    id: int,
    current_user: UserDB=Depends(get_current_user), 
    db: Session=Depends(get_db)
    ):
    employ=db.query(EmployDB).filter(EmployDB.id==id).first()
    if not employ:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )
    db.delete(employ)
    db.commit()
    return {
        "message": "Employee deleted successfully"
        }
