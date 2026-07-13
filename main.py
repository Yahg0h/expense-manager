import os
import jwt
import requests
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Configure application
app = FastAPI()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
load_dotenv()

# Get credentials from .env file
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Engine will allow to CRUD info to and from the MySQL database with SQLAlchemy instead of mysql.connector
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

# classes/Pydantic Models to use in the routes
class UserCreate(BaseModel):
    username: str = Field(min_length=4, max_length=50)
    password: str = Field(min_length=12, max_length=60)

class UserResponse(BaseModel):
    id : int
    username: str = Field(min_length=4, max_length=50)
    created_at: datetime

class CategoryCreate(BaseModel):
    name: str = Field(min_length=4, max_length=50)
    description: str = Field(min_length=1, max_length=255)

class CategoryResponse(BaseModel):
    id: int
    name: str = Field(min_length=4, max_length=50)
    description: str = Field(min_length=1, max_length=255)
    user_id: int
    created_at: datetime

class ExpensesCreate(BaseModel):
    category_id: int
    description: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(decimal_places=2, max_digits=10)
    expense_date: datetime

class ExpensesResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    description: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(decimal_places=2, max_digits=10)
    expense_date: datetime
    created_at: datetime

class BudgetCreate(BaseModel):
    category_id: int
    limit_amount: Decimal = Field(decimal_places=2, max_digits=10)
    month_year: str = Field(min_length=1, max_length=7)

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    limit_amount: Decimal = Field(decimal_places=2, max_digits=10)
    month_year: str = Field(min_length=1, max_length=7)
    created_at: datetime