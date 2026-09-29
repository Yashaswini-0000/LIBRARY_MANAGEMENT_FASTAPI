# Library Management System - FastAPI

## Objective
A complete backend system using FastAPI, Pydantic, SQLAlchemy and MySQL for managing library categories, books, members and borrow/return transactions.

## Tech Stack
- Python 3.9+
- FastAPI
- Pydantic
- SQLAlchemy
- MySQL
- Uvicorn

## Project Structure

```text
library_management_fastapi/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── services/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── library_schema.sql
└── README.md
```

## Setup

### 1. Create the MySQL database
Open MySQL Workbench and run `library_schema.sql`.

The script creates:
- library_db
- categories
- books
- members
- borrow_records

### 2. Configure .env
Open `.env` and replace `YOUR_MYSQL_PASSWORD` with your MySQL password.

Example:

```env
DATABASE_URL=mysql+pymysql://root:MyPassword@localhost/library_db
```

### 3. Create virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Start FastAPI

```powershell
uvicorn app.main:app --reload
```

### 6. Open Swagger

```text
http://127.0.0.1:8000/docs
```

## APIs

### Categories
- POST `/categories`
- GET `/categories`
- PUT `/categories/{category_id}`
- DELETE `/categories/{category_id}`

### Books
- POST `/books`
- GET `/books`
- GET `/books/{book_id}`
- PUT `/books/{book_id}`
- DELETE `/books/{book_id}`

Book filters:
```text
GET /books?title=guide
GET /books?author=narayan
GET /books?category_id=1
GET /books?author=narayan&category_id=1&skip=0&limit=10
```

### Members
- POST `/members`
- GET `/members`
- GET `/members/{member_id}`
- PUT `/members/{member_id}`
- DELETE `/members/{member_id}`

### Borrow / Return
- POST `/borrow`
- PUT `/return/{borrow_id}`
- GET `/members/{member_id}/books`
- GET `/books/{book_id}/borrow-history`
- GET `/borrow/overdue`

## Business Rules Implemented

1. Books cannot be borrowed when available copies are zero.
2. Available copies decrease by one after borrowing.
3. Available copies increase by one after returning.
4. A member can have a maximum of three active borrowed books.
5. A member cannot borrow the same book twice before returning it.
6. Inactive members cannot borrow books.
7. Due date is 14 days after the borrow date.
8. Late returns are marked `Overdue`.
9. Currently borrowed books cannot be deleted.
10. Category names are unique.
11. ISBN values are unique.
12. Member emails are unique.
13. Phone numbers are validated.
14. Available copies cannot exceed total copies.
15. Available copies cannot go below zero.

## HTTP Status Codes

- `200` - Successful GET/PUT
- `201` - Successful POST
- `400` - Business rule violation
- `404` - Resource not found
- `409` - Duplicate unique field
- `422` - Pydantic/input validation or invalid pagination

## Assumptions

- Borrow date is automatically set to today's date when a borrow transaction is created.
- Due date is automatically calculated as 14 days after borrow date.
- Return date is automatically set to today's date.
- A book is considered actively borrowed when `return_date` is NULL.
- The `Overdue` status is refreshed by the overdue endpoint and when a late return occurs.
- Pagination defaults to `skip=0` and `limit=10`.
- Maximum page size is 100.
- Book deletion is blocked only when there is an active borrow record.
- Category deletion is blocked when books still belong to that category.
