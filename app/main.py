from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app import models, schemas, crud

from app.auth import (
    create_access_token,
    get_current_user,
    get_current_admin,
    get_current_student
)

from app.database import engine, SessionLocal, Base

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles


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
    current_user = Depends(get_current_admin)
):

    # Check book exists
    book = crud.get_book(
        db,
        issued_book.book_id
    )

    if not book:

        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    # Check user exists
    user = db.query(
        models.User
    ).filter(
        models.User.id == issued_book.user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check if book is already issued
    existing_issue = db.query(
        models.IssuedBook
    ).filter(
        models.IssuedBook.book_id == issued_book.book_id,
        models.IssuedBook.status == "issued"
    ).first()

    if existing_issue:

        raise HTTPException(
            status_code=400,
            detail="Book is already issued"
        )

    try:

        return crud.issue_book(
            db,
            issued_book
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ===========================
# ALL ISSUED BOOKS
# ADMIN ONLY
# ===========================

@app.get(
    "/issued-books",
    response_model=list[schemas.IssuedBookResponse],
    tags=["Library"]
)
def get_issued_books(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):

    return crud.get_issued_books(db)


# ===========================
# MY ISSUED BOOKS
# STUDENT
# ===========================

@app.get(
    "/my-issued-books",
    response_model=list[schemas.IssuedBookResponse],
    tags=["Library"]
)
def get_my_issued_books(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # Find logged-in user
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

    return crud.get_user_issued_books(
        db,
        user.id
    )


# ===========================
# RETURN BOOK
# ADMIN ONLY
# ===========================

@app.put(
    "/return-book/{issued_book_id}",
    response_model=schemas.IssuedBookResponse,
    tags=["Library"]
)
def return_book(
    issued_book_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):

    issued_book = crud.return_book(
        db,
        issued_book_id
    )

    if not issued_book:

        raise HTTPException(
            status_code=404,
            detail="Issued book record not found"
        )

    return issued_book