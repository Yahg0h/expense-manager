# Expense Manager API
 
A full-featured expense management system built with FastAPI, MySQL, and pandas. Track expenses, categorize spending, and analyze financial patterns with detailed reports.
 
## About
 
Expense Manager is a modern REST API designed for personal finance tracking and analysis. It provides comprehensive expense management capabilities with role-based access control, JWT authentication, and advanced analytics using pandas.
 
The project demonstrates production-ready backend development practices including:
- Secure authentication and authorization
- Database design with MySQL
- RESTful API design principles
- Comprehensive test coverage with pytest
- Docker containerization and CI/CD integration
- Data analysis with pandas
## Features
 
- **User Authentication**: Secure JWT-based authentication with password hashing (Argon2)
- **Expense Management**: Full CRUD operations for expenses and categories
- **Advanced Analytics**: 
  - Monthly expense reports with category breakdown
  - Category-specific spending analysis
  - Month-to-month comparison with percentage changes
- **Data Security**: User isolation, secure token validation, authorization checks
- **Containerization**: Docker and Docker Compose for easy deployment
- **Automated Testing**: Comprehensive pytest suite with 35+ test cases
- **CI/CD Pipeline**: GitHub Actions for automated testing and Docker image publishing
## Tech Stack
 
| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.104.1+ |
| Language | Python 3.14 |
| Database | MySQL 8.0+ |
| ORM/Query | SQLAlchemy Core + `text()` |
| Validation | Pydantic v2 |
| Authentication | PyJWT (HS256) |
| Password Hashing | Argon2 (argon2-cffi) |
| Data Analysis | pandas |
| Testing | pytest + httpx |
| Server | Uvicorn (ASGI) |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Environment | python-dotenv |
| API Documentation | Swagger UI (built-in) |
 
## Project Structure
 
```
expense-manager/
├── .github/
│   └── workflows/
│       └── ci.yaml                 # GitHub Actions CI/CD pipeline
├── main.py                         # FastAPI application entry point
├── test_main.py                    # Comprehensive test suite
├── swagger_schemas.py              # Swagger documentation schemas
├── schema.sql                      # Database schema and initialization
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container image definition
├── compose.yaml                    # Docker Compose configuration
├── .env                           # Environment variables (not committed)
├── .dockerignore                  # Docker build exclusions
├── .gitignore                     # Git exclusions
└── README.md                      # This file
```
 
## Database Schema
 
### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
 
### Categories Table
```sql
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```
 
### Expenses Table
```sql
CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    expense_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```
 
## Setup & Installation
 
### Prerequisites

- **Python 3.14+** — Required for running the application
- **MySQL 8.0+** — Database server (local or via Docker)
- **Docker & Docker Compose** — For containerized deployment (optional but recommended)
- **Git** — For version control

### Key Requirements

The project requires the following Python packages:

- FastAPI (web framework)
- SQLAlchemy (database queries)
- PyJWT (authentication)
- Argon2 (password hashing)
- pandas (data analysis)
- pytest (testing)
- MySQL connector (database driver)
- python-dotenv (environment variables)

See `requirements.txt` for all dependencies with specific versions.

### Steps

#### Option 1: Local Setup (without Docker)

1. **Clone the repository**
```bash
   git clone https://github.com/Yahg0h/expense-manager.git
   cd expense-manager
```

2. **Create and activate virtual environment**
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
   # Create a `.env` file in the root directory with the following content:
   SECRET_KEY=your_secret_key_here
   DB_HOST=localhost
   DB_USER=your_mysql_user
   DB_PASSWORD=your_mysql_password
   DB_NAME=expenses_db
```
   
   To generate a secure `SECRET_KEY`, run:
```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
```

5. **Setup MySQL database**
```bash
   # Create database and import schema
   mysql -u root -p < schema.sql
```

6. **Run the application**
```bash
   python -m uvicorn main:app --reload
```

   API will be available at `http://localhost:8000`

7. **Run tests**
```bash
   pytest test_main.py -v
```

#### Option 2: Docker Setup (Recommended)

1. **Clone the repository**
```bash
   git clone https://github.com/Yahg0h/expense-manager.git
   cd expense-manager
```

2. **Configure environment variables**
```bash
   # Create a `.env` file in the root directory with the following content:
   SECRET_KEY=your_secret_key_here
   DB_HOST=db
   DB_USER=root
   DB_PASSWORD=your_password_here
   DB_NAME=expenses_db
```
3. **Build and start containers**
```bash
   docker compose up --build
```

   API will be available at `http://localhost:8080`

4. **Run tests in container**
```bash
   docker compose exec server pytest test_main.py -v
```

5. **Stop containers**
```bash
   docker compose down
```
 
## Routes
 
### Authentication
 
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/register` | No | Register a new user |
| POST | `/login` | No | Login and receive JWT token |
 
### Categories
 
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/categories` | Yes | Create a new expense category |
| GET | `/categories` | Yes | List all user's categories |
| PUT | `/categories/{category_id}` | Yes | Update a category |
| DELETE | `/categories/{category_id}` | Yes | Delete a category |
 
### Expenses
 
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/expenses` | Yes | Create a new expense |
| GET | `/expenses` | Yes | List all user's expenses |
| PUT | `/expenses/{expense_id}` | Yes | Update an expense |
| DELETE | `/expenses/{expense_id}` | Yes | Delete an expense |
 
### Reports
 
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/report/month/{month}` | Yes | Get monthly expense report |
| GET | `/report/category/{category_id}` | Yes | Get category-specific report |
| GET | `/report/comparison/{month}` | Yes | Compare current vs previous month |
 
**For detailed request/response examples, please visit the Swagger UI documentation at `/docs` when the server is running.**
 
## Authentication Header
 
All protected routes require a JWT token in the Authorization header:
 
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
 
**Example with curl**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://localhost:8000/categories
```
 
**Token Lifetime**: 1 hour from issuance
 
## Security
 
### Implementation Details
 
1. **Password Hashing**: All passwords are hashed using Argon2 before storage
   - Algorithm: Argon2id
   - Salt generation: Automatic (via argon2-cffi)
2. **JWT Authentication**: Stateless token-based authentication
   - Algorithm: HS256
   - Secret key: Stored in `.env` (SECRET_KEY)
   - Token expiration: 1 hour
3. **User Isolation**: 
   - All queries filtered by user_id from JWT token
   - Users cannot access other users' categories or expenses
   - Returns 403 Forbidden for unauthorized access attempts
4. **SQL Injection Prevention**:
   - All queries use parameterized statements with named parameters
   - SQLAlchemy text() with bound parameters
5. **Rate Limiting**: Consider implementing for production deployments
### Best Practices
 
- Never commit `.env` file to version control
- Rotate SECRET_KEY periodically
- Use HTTPS in production
- Keep dependencies updated
- Monitor logs for suspicious activity
## Troubleshooting
 
### Database Connection Error
**Error**: `Connection refused` or `Access denied`
**Solution**:
- Verify MySQL is running
- Check `.env` credentials (DB_HOST, DB_USER, DB_PASSWORD)
- Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`
### Port Already in Use
**Error**: `Address already in use :8000` or `:8080`
**Solution**:
- Kill process on port: `lsof -i :8000` → `kill -9 PID`
- Or change port in uvicorn command: `--port 8001`
### Docker Build Fails
**Error**: `docker: command not found`
**Solution**:
- Install Docker Desktop from [here](https://www.docker.com/products/docker-desktop)
- Restart terminal after installation
### Tests Fail with 422 Validation Error
**Error**: `assert 422 == 201`
**Solution**:
- Verify password is 12+ characters
- Verify `amount` values are sent as strings: `"50.00"` not `50.00`
- Check Pydantic model validation rules in main.py
### Expense Cannot Access Another User's Category
**Error**: `404 Not Found`
**Solution**:
- This is expected behavior for security
- Ensure you're using the correct category_id for your account
- Verify you created the category yourself (you are the owner)
### Token Expired Error
**Error**: `401 Unauthorized: Invalid token`
**Solution**:
- Tokens expire after 1 hour
- Login again to receive a new token
- Copy the new access_token to Authorization header
## License
 
This project is licensed under the MIT License — see the LICENSE file for details.
 
## Author
 
**Yahg0h** — Backend Developer
- GitHub: [@yahg0h](https://github.com/yahg0h)
- Docker Hub: [yahg0h](https://hub.docker.com/u/yahg0h)
---

For questions or issues, please open an issue.