import os
import jwt
import pandas as pd
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from swagger_schemas import ROUTE_DOCS

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

# Get previous month function - for use in expense comparison report in "/report/comparison/{month}"
def get_previous_month(month_str):
    # e.g '2026-07' returns '2026-06'
    date_obj = datetime.strptime(f"{month_str}-01", "%Y-%m-%d")
    previous_date = date_obj - timedelta(days=1)
    return previous_date.strftime("%Y-%m")

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
@app.post("/register", status_code=201, **ROUTE_DOCS["register"])
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

        # Reorganize the new dict with new user's username (it's in a row, since its just one information (e.g "0")), and return it
        new_dict = {
            "username": results[0],
            "message": "User created successfully."
        }
        return new_dict

# Login route
@app.post("/login", status_code=200, **ROUTE_DOCS["login"])
def login(user: UserCreate):
    # Get user inputs (request info)
    username = user.username
    password = user.password

    # Connect to database
    with engine.connect() as conn:
        # Check if user is already registered
        query = conn.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username})
        existing_user = query.fetchone()

        # If not, return 401
        if existing_user is None:
            raise HTTPException(status_code=401, detail="User not found or doesn't exist.")
        
        # Convert row to dict
        cur_user = dict(existing_user._mapping)

        # Check if the password inputted match the password stored
        verify_pass = verify_password(password, cur_user['password'])

        # If it doesn't, return 401
        if not verify_pass:
            raise HTTPException(status_code=401, detail="Wrong password. Try Again.")
        
        # If it does, create a JWT for user access
        token = create_jwt_token(cur_user['id'])

        # Return token to the user
        return {"access_token": token, "token_type": "bearer"}

# CREATE category
@app.post("/categories", status_code=201, **ROUTE_DOCS["create_category"])
def create_category(category: CategoryCreate, user_id: int = Depends(verify_token)):
    # Get user inputs (request info)
    name = category.name
    description = category.description

    # Connect to database
    with engine.connect() as conn:
        # Check if a category of the same name already exists
        query = conn.execute(text("SELECT * FROM categories WHERE user_id = :user_id AND name = :name"), {"user_id": user_id, "name": name})
        existing_category = query.fetchone()

        # If it already exists, return 401
        if existing_category is not None:
            raise HTTPException(status_code=401, detail="A category with the same name already exists.")
        
        # Else, add it to the database
        conn.execute(text("INSERT INTO categories (name, description, user_id) VALUES (:name, :description, :user_id)"), {"name": name, "description": description, "user_id": user_id})
        conn.commit()

        # Get the recently added category
        query = conn.execute(text("SELECT * FROM categories WHERE id = LAST_INSERT_ID()"))
        results = query.fetchone()

        # Convert from row to dict
        recent_category = dict(results._mapping)

        # Create a new dict to organize the info
        new_dict = {
            "id": recent_category['id'],
            "name": recent_category['name'],
            "description": recent_category['description'],
            "user_id": user_id,
            "created_at": recent_category['created_at']
        }

        # Return the response in the correct Pydantic model
        response = CategoryResponse(**new_dict) # Add the dict info to a Pydantic model
        return response # Returns the model

# READ category information   
@app.get("/categories", status_code=200, **ROUTE_DOCS["get_categories"])
def get_category(user_id: int = Depends(verify_token)):
    # Connect to database
    with engine.connect() as conn:
        # Get all categories registered by the user
        query = conn.execute(text("SELECT * FROM categories WHERE user_id = :user_id"), {"user_id": user_id})
        results = query.fetchall()

        # If there isn't a category created, return a custom message
        if not results:
            return {"message": "You haven't created any categories yet."}
        
        # Else, create a list to keep all the categories created by the user
        registered_categories = []

        # For each registered category
        for category_row in results:
            # Convert from row to dict
            results_dict = dict(category_row._mapping)

            # Put all category info in a new dict
            category_dict = {
                "id": results_dict['id'],
                "name": results_dict['name'],
                "description": results_dict['description'],
                "user_id": user_id,
                "created_at": results_dict['created_at']
            }
            # Add the category info dict to a Pydantic model, then to the category list
            registered_categories.append(CategoryResponse(**category_dict))

        # Return the list of registered categories by the user
        return registered_categories

# UPDATE category information
@app.put("/categories/{category_id}", status_code=200, **ROUTE_DOCS["update_category"])
def update_category(category: CategoryCreate, category_id: int, user_id: int = Depends(verify_token)):
    # Get user inputs to update the category info (request info)
    name = category.name
    description = category.description

    # Connect to database
    with engine.connect() as conn:
        # Search for category
        query = conn.execute(text("SELECT * FROM categories WHERE id = :category_id"), {"category_id": category_id})
        results = query.fetchone()

        # Check if the category doesn't exist
        if not results:
            raise HTTPException(status_code=404, detail="Category not found or doesn't exist.") 

        # If it does, convert from row to dict
        results_dict = dict(results._mapping)

        # Check if the current user is the owner of the category, If not, return 403
        if results_dict['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You don't have access to do this action.")
        
        # Else, update the category info
        conn.execute(text("UPDATE categories SET name = :name, description = :description WHERE id = :category_id AND user_id = :user_id"), 
                     {"name": name, "description": description, "category_id": category_id, "user_id": user_id})
        conn.commit()

        # Get the data of recently updated category
        query = conn.execute(text("SELECT * FROM categories WHERE id = :category_id"), {"category_id": category_id})
        results = query.fetchone()

        # Convert from row to dict
        updated_category = dict(results._mapping)

        # Create a new dict to organize the info
        new_dict = {
            "id": updated_category['id'],
            "name": updated_category['name'],
            "description": updated_category['description'],
            "user_id": user_id,
            "created_at": updated_category['created_at']
        }

        # Return the response in the correct Pydantic model
        response = CategoryResponse(**new_dict) # Add the dict info to a Pydantic model
        return response # Returns the model

# DELETE category
@app.delete("/categories/{category_id}", status_code=200, **ROUTE_DOCS["delete_category"])
def delete_category(category_id: int, user_id: int = Depends(verify_token)):
    # Connect to database
    with engine.connect() as conn:
        # Search for the category
        query = conn.execute(text("SELECT * FROM categories WHERE id = :category_id"), {"category_id": category_id})
        results = query.fetchone()

        # Check if the category doesn't exist
        if not results:
            raise HTTPException(status_code=404, detail="Category not found or doesn't exist.") 

        # If it does, convert from row to dict
        results_dict = dict(results._mapping)

        # Check if the current user is the owner of the category, If not, return 403
        if results_dict['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You don't have access to do this action.")
        
        # Else, delete the category
        conn.execute(text("DELETE FROM categories WHERE id = :category_id AND user_id = :user_id"), {"category_id": category_id, "user_id": user_id})
        conn.commit()
        
        return {"message": "Category deleted successfully."}

# CREATE expenses
@app.post("/expenses", status_code=201, **ROUTE_DOCS["create_expense"])
def create_expenses(expenses: ExpensesCreate, user_id: int = Depends(verify_token)):
    # Get user input (request info)
    category_id = expenses.category_id
    description = expenses.description
    amount = expenses.amount
    expense_date = expenses.expense_date

    # Connect to database
    with engine.connect() as conn:
        # Check if the category chosen exists
        query = conn.execute(text("SELECT * FROM categories WHERE id = :category_id"), {"category_id": category_id})
        results = query.fetchone()

        # If it doesn't, return error 404
        if results is None:
            raise HTTPException(status_code=404, detail="Category not found or doesn't exist.")
        
        # Else, convert from row to dict
        existing_category = dict(results._mapping)

        # Check if the category was created by the current user trying to use it
        # If the category wasn't created by the current user, return 403
        if existing_category['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access Forbidden: You aren't allowed to use this category.")
        
        # Else, add it to the database
        conn.execute(text("INSERT INTO expenses (user_id, category_id, description, amount, expense_date) VALUES (:user_id, :category_id, :description, :amount, :expense_date)"), 
                     {"user_id": user_id, "category_id": category_id, "description": description, "amount": amount, "expense_date": expense_date})
        conn.commit()

        # Get the recently created expense
        query = conn.execute(text("SELECT * FROM expenses WHERE id = LAST_INSERT_ID()"))
        results = query.fetchone()

        # Convert from row to dict
        results_dict = dict(results._mapping)

        # Reorganize a new dict with all expense information
        expenses_dict = {
            "id": results_dict['id'],
            "user_id": user_id,
            "category_id": results_dict['category_id'],
            "description": results_dict['description'],
            "amount": results_dict['amount'],
            "expense_date": results_dict['expense_date'],
            "created_at": results_dict['created_at']
        }
        # Add dict to the Pydantic model
        response = ExpensesResponse(**expenses_dict)

        # Return the Pydantic model with all expenses info
        return response

# READ expenses information
@app.get("/expenses", status_code=200, **ROUTE_DOCS["get_expenses"])
def get_expenses(user_id: int = Depends(verify_token)):
    # Connect to database
    with engine.connect() as conn:
        # Get all expenses registered by the user
        query = conn.execute(text("SELECT * FROM expenses WHERE user_id = :user_id"), {"user_id": user_id})
        results = query.fetchall()

        # If the user doesn't have any expenses registered, return custom message
        if not results:
            return {"message": "You haven't registered any expenses yet."}
        
        # Else if it does, create a list to keep track of all of the expenses registered
        registered_expenses = []

        # For each expense registered
        for expense_row in results:
            # Convert from row to dict
            results_dict = dict(expense_row._mapping)

            # Put all expense info in a new dict
            expense_dict = {
                "id": results_dict['id'],
                "user_id": user_id,
                "category_id": results_dict['category_id'],
                "description": results_dict['description'],
                "amount": results_dict['amount'],
                "expense_date": results_dict['expense_date'],
                "created_at": results_dict['created_at']
            }
            # Add the expense dict info into the list
            registered_expenses.append(ExpensesResponse(**expense_dict))

        # Return the full expenses list
        return registered_expenses

# UPDATE expense information
@app.put("/expenses/{expense_id}", status_code=200, **ROUTE_DOCS["update_expense"])
def update_expense(expenses: ExpensesCreate, expense_id: int, user_id: int = Depends(verify_token)):
    # Get user inputs to update the expense
    category_id = expenses.category_id
    description = expenses.description
    amount = expenses.amount
    expense_date = expenses.expense_date

    # Connect to database
    with engine.connect() as conn:
        # Search for the expense to be updated
        query = conn.execute(text("SELECT * FROM expenses WHERE id = :expense_id"), {"expense_id": expense_id})
        existing_expense = query.fetchone()

        # Check if the expense doesn't exist
        if not existing_expense:
            raise HTTPException(status_code=404, detail="Expense not found or doesn't exist.") 

        # If it does, convert from row to dict
        results_dict = dict(existing_expense._mapping)

        # Check if the current user is the owner of the expense, If not, return 403
        if results_dict['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You don't have access to do this action.")
        
        # Check if the category registered in the expense exists
        query = conn.execute(text("SELECT * FROM categories WHERE id = :category_id"), {"category_id": category_id})
        existing_category = query.fetchone()

        # If it doesn't, return 404
        if existing_category is None:
            raise HTTPException(status_code=404, detail="Category not found or doesn't exist.")
        
        # Convert from row to dict
        category_dict = dict(existing_category._mapping)

        # Check if the current user is the creator of the category, If not, return 403
        if category_dict['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You don't have access to do this action.")

        # Else, update the expense info
        conn.execute(text("UPDATE expenses SET category_id = :category_id, description = :description, amount = :amount, expense_date = :expense_date WHERE id = :expense_id AND user_id = :user_id"), 
                     {"category_id": category_id, "description": description, "amount": amount, "expense_date": expense_date, "expense_id": expense_id, "user_id": user_id})
        conn.commit()        

        # Get the data of recently updated expense
        query = conn.execute(text("SELECT * FROM expenses WHERE id = :expense_id"), {"expense_id": expense_id})
        results = query.fetchone()

        # Convert from row to dict
        updated_expense = dict(results._mapping)

        # Create a new dict to organize the info
        new_dict = {
            "id": updated_expense['id'],
            "user_id": user_id,
            "category_id": updated_expense['category_id'],
            "description": updated_expense['description'],
            "amount": updated_expense['amount'],
            "expense_date": updated_expense['expense_date'],
            "created_at": updated_expense['created_at']
        }

        # Return the response in the correct Pydantic model
        response = ExpensesResponse(**new_dict) # Add the dict info to a Pydantic model
        return response # Returns the model

# DELETE expense
@app.delete("/expenses/{expense_id}", status_code=200, **ROUTE_DOCS["delete_expense"])
def delete_expense(expense_id: int, user_id: int = Depends(verify_token)):
    # Connect to database
    with engine.connect() as conn:
        # Search the database for the expense
        query = conn.execute(text("SELECT * FROM expenses WHERE id = :expense_id"), {"expense_id": expense_id})
        results = query.fetchone()

        # Check if the expense doesn't exist
        if not results:
            raise HTTPException(status_code=404, detail="Expense not found or doesn't exist.") 

        # If it does, convert from row to dict
        results_dict = dict(results._mapping)

        # Check if the current user is the owner of the expense, If not, return 403
        if results_dict['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You don't have access to do this action.")
        
        # Else, delete the category
        conn.execute(text("DELETE FROM expenses WHERE id = :expense_id AND user_id = :user_id"), {"expense_id": expense_id, "user_id": user_id})
        conn.commit()
        
        return {"message": "Expense deleted successfully."}

# Monthly report
@app.get("/report/month/{month}", status_code=200, **ROUTE_DOCS["monthly_report"])
def monthly_report(month: str, user_id: int = Depends(verify_token)):
    # Connect to db
    with engine.connect() as conn:
        # Get category, total spent and expense quantity from all expenses registered by the user
        query = conn.execute(text("SELECT c.name as category, SUM(e.amount) as total, COUNT(e.id) as count FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.user_id = :user_id AND DATE_FORMAT(e.expense_date, '%Y-%m') = :month GROUP BY c.id, c.name"), 
                             {"user_id": user_id, "month": month})
        results = query.fetchall()

        # If there isn't any data to report, return custom message
        if not results:
            return {"message": "No data recorded for the month. Data analysis is not possible."}
    
        # Convert row data to DataFrame
        df = pd.DataFrame([dict(row._mapping) for row in results])

        # Create a report dict with all info regarding the expenses in a month time-frame
        report = {
            "month": month,
            "total_spent": float(df['total'].sum()),
            "average_per_category": float(df['total'].mean()),
            "top_category": {
                "name": df.loc[df['total'].idxmax()]['category'],
                "amount": float(df.loc[df['total'].idxmax()]['total'])
            },
            "by_category": [
                {
                    "category": row['category'],
                    "total": float(row['total']),
                    "count": int(row['count'])
                }
                for _, row in df.iterrows()
            ]
        }

        # Return the report to be displayed to the user
        return report

# Category report
@app.get("/report/category/{category_id}", status_code=200, **ROUTE_DOCS["category_report"])
def category_report(category_id: int, user_id: int = Depends(verify_token)):
    # Connect to database
    with engine.connect() as conn:
        # Check if the category to be analyzed was created by the user
        query = conn.execute(text("SELECT * FROM categories WHERE id = :category_id AND user_id = :user_id"), {"category_id": category_id, "user_id": user_id})
        category = query.fetchone()

        # If it exist doesn't, return error 404
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found or doesn't exist.")
        
        # Else, convert from row to dict
        existing_category = dict(category._mapping)

        # Check if the category was created by the current user trying to use it
        # If the category wasn't created by the current user, return 403
        if existing_category['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access Forbidden: You aren't allowed to use this category.")
        
        # Get all expenses made under the category of id 'category_id'
        query = conn.execute(text("SELECT e.amount, e.expense_date FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.user_id = :user_id AND e.category_id = :category_id"), 
                             {"user_id": user_id, "category_id": category_id})
        results = query.fetchall()

        # If there isn't any data to report, return custom message
        if not results:
            return {"message": "No data recorded for the category. Data analysis is not possible."}
        
        # Convert row data to DataFrame
        df = pd.DataFrame([dict(row._mapping) for row in results])

        # Pandas calculations (do one by one so it can be easy to track, unlike before)
        # Total spent
        total = df['amount'].sum()

        # Biggest expense
        max_expense = df['amount'].max()

        # Lowest expense
        min_expense = df['amount'].min()

        # Average per expense
        average = df['amount'].mean()

        # Expense count
        count = len(df)

        # Create a report dict with all info regarding the expenses in a category
        report = {
            "category_id": category_id,
            "category_name": existing_category['name'],
            "total_spent": float(total),
            "max_expense": float(max_expense),
            "min_expense": float(min_expense),
            "average_per_expense": float(average),
            "expense_count": count
        }

        # Return the report to be displayed to the user
        return report

# Monthly comparison report   
@app.get("/report/comparison/{month}", status_code=200, **ROUTE_DOCS["comparison_report"])
def comparison_report(month: str, user_id: int = Depends(verify_token)):
    # Get the current month, and the previous month to compare
    current_month = month
    previous_month = get_previous_month(month)

    # Connect to database
    with engine.connect() as conn:
        # Get all total spent, average per category and expense quantity for the current_month
        query = conn.execute(text("SELECT c.name as category, SUM(e.amount) as total, COUNT(e.id) as count FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.user_id = :user_id AND DATE_FORMAT(e.expense_date, '%Y-%m') = :month GROUP BY c.id, c.name"), 
                             {"user_id": user_id, "month": current_month})
        current_results = query.fetchall()

        # If there isn't any data to report, return custom message
        if not current_results:
            return {"message": "No data recorded for the current month. Data analysis is not possible."}
    
        # Convert row data to DataFrame
        df = pd.DataFrame([dict(row._mapping) for row in current_results])

        # Create a report dict with all info regarding the expenses in a month time-frame
        current_report = {
            "month": month,
            "total_spent": float(df['total'].sum()),
            "average_per_category": float(df['total'].mean()),
            "top_category": {
                "name": df.loc[df['total'].idxmax()]['category'],
                "amount": float(df.loc[df['total'].idxmax()]['total'])
            },
            "by_category": [
                {
                    "category": row['category'],
                    "total": float(row['total']),
                    "count": int(row['count'])
                }
                for _, row in df.iterrows()
            ],
            "count": len(df)
        }

        # Get all total spent, average per category and expense quantity for the previous_month
        query = conn.execute(text("SELECT c.name as category, SUM(e.amount) as total, COUNT(e.id) as count FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.user_id = :user_id AND DATE_FORMAT(e.expense_date, '%Y-%m') = :month GROUP BY c.id, c.name"), 
                             {"user_id": user_id, "month": previous_month})
        previous_results = query.fetchall()

        # If there isn't any data to report, return custom message
        if not previous_results:
            return {"message": "No data recorded for the previous month. Data analysis is not possible."}
    
        # Convert row data to DataFrame
        df = pd.DataFrame([dict(row._mapping) for row in previous_results])

        # Create a report dict with all info regarding the expenses in a month time-frame
        previous_report = {
            "month": month,
            "total_spent": float(df['total'].sum()),
            "average_per_category": float(df['total'].mean()),
            "top_category": {
                "name": df.loc[df['total'].idxmax()]['category'],
                "amount": float(df.loc[df['total'].idxmax()]['total'])
            },
            "by_category": [
                {
                    "category": row['category'],
                    "total": float(row['total']),
                    "count": int(row['count'])
                }
                for _, row in df.iterrows()
            ],
            "count": len(df)
        }

        # Difference calculations between the two reports
        difference = current_report['total_spent'] - previous_report['total_spent']
        percentage_change = (difference / previous_report['total_spent']) * 100

        # Comparison dict between the current month and the previous month
        comparison = {
            "current_month": current_month,
            "previous_month": previous_month,
            "current_report": current_report,
            "previous_report": previous_report,
            "difference": difference,
            "percentage_change": percentage_change
        }

        return comparison