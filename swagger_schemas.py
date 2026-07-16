# Swagger/OpenAPI Response examples for Expense Manager API
# Response dictionaries with JSON examples for Swagger UI documentation
 
# ===== AUTHENTICATION RESPONSES =====
 
register_responses = {
    201: {
        "description": "User created successfully",
        "content": {
            "application/json": {
                "example": {
                    "username": "john_doe",
                    "message": "User created successfully."
                }
            }
        }
    },
    400: {
        "description": "Username already in use"
    },
    422: {
        "description": "Validation error (password too short, invalid username length)"
    }
}
 
login_responses = {
    200: {
        "description": "Login successful",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3ODM5OTg0MjR9.YgqlbWwmbzrQONbriWxBAROg_QwhutO37qp7WKIDPhk",
                    "token_type": "bearer"
                }
            }
        }
    },
    401: {
        "description": "Invalid username or password"
    },
    422: {
        "description": "Validation error"
    }
}
 
# ===== CATEGORY RESPONSES =====
 
create_category_responses = {
    201: {
        "description": "Category created successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "name": "Groceries",
                    "description": "Food and groceries expenses",
                    "user_id": 1,
                    "created_at": "2026-07-13T23:08:14"
                }
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    },
    422: {
        "description": "Validation error"
    }
}
 
get_categories_responses = {
    200: {
        "description": "List of user's categories",
        "content": {
            "application/json": {
                "example": [
                    {
                        "id": 1,
                        "name": "Groceries",
                        "description": "Food and groceries expenses",
                        "user_id": 1,
                        "created_at": "2026-07-13T23:08:14"
                    },
                    {
                        "id": 2,
                        "name": "Transport",
                        "description": "Transportation expenses",
                        "user_id": 1,
                        "created_at": "2026-07-13T23:09:00"
                    }
                ]
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    }
}
 
update_category_responses = {
    200: {
        "description": "Category updated successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "name": "Groceries Updated",
                    "description": "Updated description",
                    "user_id": 1,
                    "created_at": "2026-07-13T23:08:14"
                }
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    },
    403: {
        "description": "Access forbidden - category belongs to another user"
    },
    404: {
        "description": "Category not found"
    }
}
 
delete_category_responses = {
    200: {
        "description": "Category deleted successfully",
        "content": {
            "application/json": {
                "example": {
                    "message": "Category deleted successfully."
                }
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    },
    403: {
        "description": "Access forbidden - category belongs to another user"
    },
    404: {
        "description": "Category not found"
    }
}
 
# ===== EXPENSE RESPONSES =====
 
create_expense_responses = {
    201: {
        "description": "Expense created successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "user_id": 1,
                    "category_id": 1,
                    "description": "Weekly groceries",
                    "amount": "75.50",
                    "expense_date": "2026-07-20T00:00:00",
                    "created_at": "2026-07-13T23:16:09"
                }
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    },
    403: {
        "description": "Category belongs to another user"
    },
    404: {
        "description": "Category not found"
    },
    422: {
        "description": "Validation error"
    }
}
 
get_expenses_responses = {
    200: {
        "description": "List of user's expenses",
        "content": {
            "application/json": {
                "example": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "category_id": 1,
                        "description": "Almoço",
                        "amount": "50.50",
                        "expense_date": "2026-07-20T00:00:00",
                        "created_at": "2026-07-13T23:16:09"
                    },
                    {
                        "id": 2,
                        "user_id": 1,
                        "category_id": 1,
                        "description": "Café",
                        "amount": "15.00",
                        "expense_date": "2026-07-21T00:00:00",
                        "created_at": "2026-07-13T23:17:01"
                    }
                ]
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    }
}
 
update_expense_responses = {
    200: {
        "description": "Expense updated successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "user_id": 1,
                    "category_id": 2,
                    "description": "Updated expense",
                    "amount": "85.00",
                    "expense_date": "2026-07-25T00:00:00",
                    "created_at": "2026-07-13T23:16:09"
                }
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    },
    403: {
        "description": "Access forbidden or category belongs to another user"
    },
    404: {
        "description": "Expense not found"
    }
}
 
delete_expense_responses = {
    200: {
        "description": "Expense deleted successfully",
        "content": {
            "application/json": {
                "example": {
                    "message": "Expense deleted successfully."
                }
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    },
    403: {
        "description": "Access forbidden - expense belongs to another user"
    },
    404: {
        "description": "Expense not found"
    }
}
 
# ===== REPORT RESPONSES =====
 
monthly_report_responses = {
    200: {
        "description": "Monthly expense report",
        "content": {
            "application/json": {
                "example": {
                    "month": "2026-07",
                    "total_spent": 500.50,
                    "average_per_category": 166.83,
                    "top_category": {
                        "name": "Groceries",
                        "amount": 250.00
                    },
                    "by_category": [
                        {
                            "category": "Groceries",
                            "total": 250.00,
                            "count": 5
                        },
                        {
                            "category": "Transport",
                            "total": 150.00,
                            "count": 3
                        }
                    ]
                }
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    }
}
 
category_report_responses = {
    200: {
        "description": "Category-specific expense report",
        "content": {
            "application/json": {
                "example": {
                    "category_id": 1,
                    "category_name": "Groceries",
                    "total_spent": 250.00,
                    "max_expense": 75.50,
                    "min_expense": 35.00,
                    "average_per_expense": 50.00,
                    "expense_count": 5
                }
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    },
    403: {
        "description": "Access forbidden - category belongs to another user"
    },
    404: {
        "description": "Category not found or no data recorded"
    }
}
 
comparison_report_responses = {
    200: {
        "description": "Month-to-month expense comparison",
        "content": {
            "application/json": {
                "example": {
                    "current_month": "2026-07",
                    "previous_month": "2026-06",
                    "current_report": {
                        "month": "2026-07",
                        "total_spent": 500.50,
                        "average_per_category": 166.83,
                        "top_category": {
                            "name": "Groceries",
                            "amount": 250.00
                        },
                        "by_category": []
                    },
                    "previous_report": {
                        "month": "2026-06",
                        "total_spent": 450.00,
                        "average_per_category": 150.00,
                        "top_category": {
                            "name": "Groceries",
                            "amount": 225.00
                        },
                        "by_category": []
                    },
                    "difference": 50.50,
                    "percentage_change": 11.22
                }
            }
        }
    },
    401: {
        "description": "Invalid or missing token"
    }
}
 
root_responses = {
    200: {
        "description": "API metadata and status",
        "content": {
            "application/json": {
                "example": {
                    "name": "Expense Manager API",
                    "status": "operational",
                    "documentation": "/docs",
                    "openapi": "/openapi.json"
                }
            }
        }
    }
}
 
# ===== ROUTE DOCUMENTATION DICTIONARY =====
 
ROUTE_DOCS = {
    # Root
    "root": {
        "summary": "API root endpoint",
        "description": "Returns API metadata, status, and documentation links.",
        "responses": root_responses,
    },
    
    # Authentication Routes
    "register": {
        "summary": "Register a new user",
        "description": "Create a new user account with username and password. Password must be at least 12 characters long. Username must be unique and 4-50 characters.",
        "responses": register_responses,
    },
    "login": {
        "summary": "User login",
        "description": "Authenticate user with credentials. Returns JWT access token valid for 1 hour.",
        "responses": login_responses,
    },
    
    # Category Routes
    "create_category": {
        "summary": "Create a new expense category",
        "description": "Create a new category for organizing expenses. Requires authentication.",
        "responses": create_category_responses,
    },
    "get_categories": {
        "summary": "Get all user's categories",
        "description": "Retrieve all expense categories belonging to the authenticated user.",
        "responses": get_categories_responses,
    },
    "update_category": {
        "summary": "Update an existing category",
        "description": "Update category name and description. Only the category owner can update.",
        "responses": update_category_responses,
    },
    "delete_category": {
        "summary": "Delete a category",
        "description": "Delete an expense category. Only the category owner can delete. Returns success message.",
        "responses": delete_category_responses,
    },
    
    # Expense Routes
    "create_expense": {
        "summary": "Create a new expense",
        "description": "Record a new expense under a specific category. Category must belong to the authenticated user.",
        "responses": create_expense_responses,
    },
    "get_expenses": {
        "summary": "Get all user's expenses",
        "description": "Retrieve all expenses belonging to the authenticated user.",
        "responses": get_expenses_responses,
    },
    "update_expense": {
        "summary": "Update an existing expense",
        "description": "Update expense details including category, amount, description, and date. Only the expense owner can update.",
        "responses": update_expense_responses,
    },
    "delete_expense": {
        "summary": "Delete an expense",
        "description": "Delete an expense record. Only the expense owner can delete. Returns success message.",
        "responses": delete_expense_responses,
    },
    
    # Report Routes
    "monthly_report": {
        "summary": "Get monthly expense report",
        "description": "Generate comprehensive expense report for a specific month (format: YYYY-MM). Includes total spent, category breakdown, and top category.",
        "responses": monthly_report_responses,
    },
    "category_report": {
        "summary": "Get category-specific report",
        "description": "Analyze spending in a specific category. Returns min, max, average expenses and total spent.",
        "responses": category_report_responses,
    },
    "comparison_report": {
        "summary": "Compare expenses between months",
        "description": "Compare current month expenses with previous month. Shows difference and percentage change.",
        "responses": comparison_report_responses,
    },
}