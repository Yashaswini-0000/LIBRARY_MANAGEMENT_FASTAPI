from fastapi import FastAPI
from app.database import Base, engine
from app.models import category, book, member, borrow
from app.routers import categories, books, members, borrow as borrow_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System",
    description="FastAPI backend for managing categories, books, members, and borrow/return transactions.",
    version="1.0.0"
)

app.include_router(categories.router)
app.include_router(books.router)
app.include_router(members.router)
app.include_router(borrow_router.router)


@app.get("/")
def root():
    return {"message": "Library Management System API is running"}
