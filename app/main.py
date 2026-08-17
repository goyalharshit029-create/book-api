from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app import models, schemas, crud

from app.services.recommendation_service import get_recommendations

from app.auth import (
    create_access_token,
    get_current_user,
    get_current_admin,
    get_current_student
)

from app.database import engine, SessionLocal, Base

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles

from datetime import datetime


# ===========================
# CREATE TABLES
# ===========================

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Management REST API",
    description="Book Management API with JWT Authentication",
    version="2.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ===========================
# CORS
# ===========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
# DATABASE DEPENDENCY
# ===========================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ===========================
# HOME
# ===========================

@app.get("/", response_class=HTMLResponse)
def home():

    with open(
        "templates/index.html",
        "r",
        encoding="utf-8"
    ) as f:

        return HTMLResponse(f.read())


# ===========================
# UI
# ===========================

@app.get(
    "/ui",
    response_class=HTMLResponse,
    tags=["UI"]
)
def ui():

    with open(
        "templates/index.html",
        "r",
        encoding="utf-8"
    ) as f:

        return HTMLResponse(f.read())


@app.get(
    "/login-page",
    response_class=HTMLResponse
)
def login_page():

    with open(
        "templates/login.html",
        "r",
        encoding="utf-8"
    ) as f:

        return HTMLResponse(f.read())


@app.get(
    "/register-page",
    response_class=HTMLResponse
)
def register_page():

    with open(
        "templates/register.html",
        "r",
        encoding="utf-8"
    ) as f:

        return HTMLResponse(f.read())


@app.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard():

    with open(
        "templates/dashboard.html",
        "r",
        encoding="utf-8"
    ) as f:

        return HTMLResponse(f.read())


@app.get(
    "/about",
    response_class=HTMLResponse
)
def about():

    with open(
        "templates/about.html",
        "r",
        encoding="utf-8"
    ) as f:

        return HTMLResponse(f.read())


@app.get(
    "/services",
    response_class=HTMLResponse
)
def services():

    with open(
        "templates/services.html",
        "r",
        encoding="utf-8"
    ) as f:

        return HTMLResponse(f.read())


@app.get(
    "/contact",
    response_class=HTMLResponse
)
def contact():

    with open(
        "templates/contact.html",
        "r",
        encoding="utf-8"
    ) as f:

        return HTMLResponse(f.read())


# ===========================
# REGISTER
# ===========================

@app.post(
    "/register",
    tags=["Authentication"]
)
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    existing = crud.get_user_by_email(
        db,
        user.email
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    crud.create_user(
        db,
        user
    )

    return {
        "message": "Registration Successful"
    }


# ===========================
# LOGIN
# ===========================

@app.post(
    "/login",
    response_model=schemas.Token,
    tags=["Authentication"]
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = crud.authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    token = create_access_token(
        {
            "sub": db_user.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role
    }


# ===========================
# CONTACT API
# ===========================

@app.post(
    "/contact",
    response_model=schemas.ContactResponse,
    tags=["Contact"]
)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db)
):

    return crud.create_contact(
        db,
        contact
    )


@app.get(
    "/contacts",
    response_model=list[schemas.ContactResponse],
    tags=["Contact"]
)
def get_contacts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):

    return crud.get_contacts(db)


# ===========================
# DASHBOARD STATISTICS
# ===========================

@app.get(
    "/stats",
    tags=["Dashboard"]
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):

    return {
        "total_books": crud.total_books(db),
        "total_users": crud.total_users(db),
        "total_contacts": crud.total_contacts(db)
    }


# ===========================
# CREATE BOOK
# ADMIN ONLY
# ===========================

@app.post(
    "/books",
    response_model=schemas.BookResponse,
    tags=["Books"]
)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):

    return crud.create_book(
        db,
        book
    )


# ===========================
# GET BOOKS
# ADMIN + STUDENT
# ===========================

# ===========================
# GET BOOKS WITH PAGINATION
# ADMIN + STUDENT
# ===========================

@app.get(
    "/books",
    response_model=schemas.PaginatedBooksResponse,
    tags=["Books"]
)
def get_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    genre: Optional[str] = None,
    sort_by: Optional[str] = None,

    page: int = 1,
    page_size: int = 10,

    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # Validate page
    if page < 1:

        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    # Validate page size
    if page_size < 1 or page_size > 100:

        raise HTTPException(
            status_code=400,
            detail="Page size must be between 1 and 100"
        )

    # Calculate skip
    skip = (page - 1) * page_size

    # Get books
    total, books = crud.get_books(
        db=db,
        title=title,
        author=author,
        genre=genre,
        sort_by=sort_by,
        skip=skip,
        limit=page_size
    )

    # Calculate total pages
    total_pages = (
        (total + page_size - 1) // page_size
        if total > 0
        else 0
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "books": books
    }


# ===========================
# GET BOOK BY ID
# ADMIN + STUDENT
# ===========================

@app.get(
    "/books/{book_id}",
    response_model=schemas.BookResponse,
    tags=["Books"]
)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    book = crud.get_book(
        db,
        book_id
    )

    if not book:

        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return book


# ===========================
# UPDATE BOOK
# ADMIN ONLY
# ===========================

@app.put(
    "/books/{book_id}",
    response_model=schemas.BookResponse,
    tags=["Books"]
)
def update_book(
    book_id: int,
    updated_book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):

    book = crud.update_book(
        db,
        book_id,
        updated_book
    )

    if not book:

        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return book


# ===========================
# DELETE BOOK
# ADMIN ONLY
# ===========================

@app.delete(
    "/books/{book_id}",
    tags=["Books"]
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):

    book = crud.delete_book(
        db,
        book_id
    )

    if not book:

        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return {
        "message": "Book deleted successfully"
    }

# ===========================
# GET STUDENTS
# ADMIN ONLY
# ===========================

@app.get(
    "/students",
    tags=["Users"]
)
def get_students(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    students = db.query(
        models.User
    ).filter(
        models.User.role == "student"
    ).all()

    return [
        {
            "id": student.id,
            "name": student.username,
            "email": student.email
        }
        for student in students
    ]

# ===========================
# GET ALL USERS
# ADMIN ONLY
# ===========================

@app.get(
    "/users",
    tags=["Users"]
)
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    users = db.query(
        models.User
    ).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]

# ===========================
# ISSUE BOOK
# ADMIN ONLY
# ===========================

@app.post(
    "/issue-book",
    response_model=schemas.IssuedBookResponse,
    tags=["Library"]
)
def issue_book(
    issued_book: schemas.IssuedBookCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    # Check book
    book = db.query(models.Book).filter(
        models.Book.id == issued_book.book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    # Check student
    user = db.query(models.User).filter(
        models.User.id == issued_book.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Check if already issued
    existing_issue = db.query(models.IssuedBook).filter(
        models.IssuedBook.book_id == issued_book.book_id,
        models.IssuedBook.status == "issued"
    ).first()

    if existing_issue:
        raise HTTPException(
            status_code=400,
            detail="Book is already issued"
        )

    # Due date validation
    issue_date = datetime.utcnow()

    if issued_book.due_date <= issue_date:
        raise HTTPException(
            status_code=400,
            detail="Due date must be after issue date"
        )

    # Create record DIRECTLY
    new_issue = models.IssuedBook(
        book_id=issued_book.book_id,
        user_id=issued_book.user_id,
        issue_date=issue_date,
        due_date=issued_book.due_date,
        return_date=None,
        fine=0.0,
        status="issued"
    )

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    # Return exactly what the response schema requires
    return {
        "id": new_issue.id,
        "book_id": new_issue.book_id,
        "user_id": new_issue.user_id,
        "book_title": book.title,
        "author": book.author,
        "student_name": user.username,
        "issue_date": new_issue.issue_date,
        "due_date": new_issue.due_date,
        "return_date": new_issue.return_date,
        "fine": new_issue.fine,
        "status": new_issue.status
    }


# ===========================
# ALL ISSUED BOOKS
# ADMIN ONLY
# ===========================

@app.get(
    "/issued-books",
    tags=["Library"]
)
def get_issued_books(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Page size must be between 1 and 100"
        )

    # Get all issued book records
    all_books = crud.get_issued_books(db)

    total = len(all_books)

    total_pages = (
        (total + page_size - 1) // page_size
        if total > 0
        else 0
    )

    start = (page - 1) * page_size
    end = start + page_size

    books = all_books[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "books": books
    }


# ===========================
# MY ISSUED BOOKS
# STUDENT
# ===========================

@app.get(
    "/my-issued-books",
    tags=["Library"]
)
def get_my_issued_books(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Page size must be between 1 and 100"
        )

    user = db.query(
        models.User
    ).filter(
        models.User.email == current_user
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Get only this student's issued books
    all_books = crud.get_user_issued_books(
        db,
        user.id
    )

    total = len(all_books)

    total_pages = (
        (total + page_size - 1) // page_size
        if total > 0
        else 0
    )

    start = (page - 1) * page_size
    end = start + page_size

    books = all_books[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "books": books
    }

# ===========================
# BOOK RECOMMENDATIONS
# STUDENT ONLY
# ===========================

@app.get(
    "/recommendations",
    tags=["Recommendations"]
)
def get_book_recommendations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_student)
):

    recommendations = get_recommendations(
        db=db,
        user_id=current_user.id,
        top_n=5
    )

    return {
        "recommendations": recommendations
    }


# ===========================
# RETURN BOOK
# ADMIN ONLY
# ===========================

@app.put(
    "/return-book/{issued_book_id}",
    response_model=None,
    tags=["Library"]
)
def return_book(
    issued_book_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    issued_book = (
        db.query(models.IssuedBook)
        .filter(
            models.IssuedBook.id == issued_book_id
        )
        .first()
    )

    if not issued_book:

        raise HTTPException(
            status_code=404,
            detail="Issued book record not found"
        )

    # Prevent returning an already returned book
    if issued_book.status == "returned":

        raise HTTPException(
            status_code=400,
            detail="This book has already been returned"
        )

    # Update issued book
    issued_book.status = "returned"

    issued_book.return_date = datetime.utcnow()

    # Optional: calculate fine
    fine = 0.0

    if (
        issued_book.due_date
        and issued_book.return_date > issued_book.due_date
    ):

        overdue_days = (
            issued_book.return_date.date()
            - issued_book.due_date.date()
        ).days

        # ₹10 fine per overdue day
        fine = overdue_days * 10

    issued_book.fine = fine

    db.commit()

    db.refresh(issued_book)

    # IMPORTANT:
    # Return only a normal dictionary.
    # Do NOT return issued_book directly.
    return {
        "message": "Book returned successfully",
        "id": issued_book.id,
        "book_id": issued_book.book_id,
        "user_id": issued_book.user_id,
        "status": issued_book.status,
        "return_date": issued_book.return_date,
        "fine": issued_book.fine
    }