# Swagger/OpenAPI Response examples for Expense Manager API
# These dicts are used for automatic API documentation in Swagger UI

# ===== ROUTE DOCUMENTATION DICTIONARY =====
 
ROUTE_DOCS = {
    # Authentication Routes
    "register": {
        "summary": "Register a new user",
        "description": "Create a new user account with username and password. Password must be at least 12 characters long. Username must be unique and 4-50 characters.",
        "tags": ["Authentication"],
    },
    "login": {
        "summary": "User login",
        "description": "Authenticate user with credentials. Returns JWT access token valid for 1 hour.",
        "tags": ["Authentication"],
    },
    
    # Category Routes
    "create_category": {
        "summary": "Create a new expense category",
        "description": "Create a new category for organizing expenses. Requires authentication.",
        "tags": ["Categories"],
    },
    "get_categories": {
        "summary": "Get all user's categories",
        "description": "Retrieve all expense categories belonging to the authenticated user.",
        "tags": ["Categories"],
    },
    "update_category": {
        "summary": "Update an existing category",
        "description": "Update category name and description. Only the category owner can update.",
        "tags": ["Categories"],
    },
    "delete_category": {
        "summary": "Delete a category",
        "description": "Delete an expense category. Only the category owner can delete. Returns success message.",
        "tags": ["Categories"],
    },
    
    # Expense Routes
    "create_expense": {
        "summary": "Create a new expense",
        "description": "Record a new expense under a specific category. Category must belong to the authenticated user.",
        "tags": ["Expenses"],
    },
    "get_expenses": {
        "summary": "Get all user's expenses",
        "description": "Retrieve all expenses belonging to the authenticated user.",
        "tags": ["Expenses"],
    },
    "update_expense": {
        "summary": "Update an existing expense",
        "description": "Update expense details including category, amount, description, and date. Only the expense owner can update.",
        "tags": ["Expenses"],
    },
    "delete_expense": {
        "summary": "Delete an expense",
        "description": "Delete an expense record. Only the expense owner can delete. Returns success message.",
        "tags": ["Expenses"],
    },
    
    # Report Routes
    "monthly_report": {
        "summary": "Get monthly expense report",
        "description": "Generate comprehensive expense report for a specific month (format: YYYY-MM). Includes total spent, category breakdown, and top category.",
        "tags": ["Reports"],
    },
    "category_report": {
        "summary": "Get category-specific report",
        "description": "Analyze spending in a specific category. Returns min, max, average expenses and total spent.",
        "tags": ["Reports"],
    },
    "comparison_report": {
        "summary": "Compare expenses between months",
        "description": "Compare current month expenses with previous month. Shows difference and percentage change.",
        "tags": ["Reports"],
    },
}