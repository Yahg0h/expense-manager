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

# JWT Creation
def create_jwt_token(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# JWT Validation
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
# JWT Verification (for access in restricted areas)
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_id = verify_jwt_token(token)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token.")
    
    return user_id

# Password hasher
def hash_password(password: str):
    hashed_pass = pwd_context.hash(password)
    return hashed_pass

# Password verifier
def verify_password(password: str, hashed_password: str):
    pass_check = pwd_context.verify(password, hashed_password)
    return pass_check # Will return true to equality, and false to unequality

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

# Register Route
@app.post("/register", status_code=201)
def register(user: UserCreate):
    # Get use inputs (request info)
    username = user.username
    password = user.password

    # Connect to database
    with engine.connect() as conn:
        # Verify if username already exists
        query = conn.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username})
        existing_username = query.fetchone()

        # If it exists, return 400
        if existing_username is not None:
            raise HTTPException(status_code=400, detail="Username is already in use.")

        # Else, hash password..
        hashed_pass = hash_password(password)

        # ..and add to database
        conn.execute(text("INSERT INTO users (username, password) VALUES (:username, :password)"), {"username": username, "password": hashed_pass})
        conn.commit()

        # Get id from the recently added user
        query = conn.execute(text("SELECT username FROM users WHERE id = LAST_INSERT_ID()"))
        results = query.fetchone()

        # Reorganize the new dict with new user's username, and return it
        new_dict = {
            "username": results["username"],
            "message": "User created successfully."
        }
        return new_dict