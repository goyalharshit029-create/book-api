from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# ==========================
# BOOK SCHEMAS
# ==========================

class BookCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    author: str = Field(..., min_length=2)
    genre: str
    price: float = Field(..., gt=0)
    published_year: int


class BookResponse(BookCreate):
    id: int

    class Config:
        from_attributes = True


# ==========================
# USER SCHEMAS
# ==========================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str


# ==========================
# CONTACT SCHEMAS
# ==========================

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


class ContactResponse(ContactCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================
# ISSUED BOOK SCHEMAS
# ==========================

class IssuedBookCreate(BaseModel):
    book_id: int
    user_id: int
    due_date: datetime


class IssuedBookResponse(BaseModel):

    id: int
    book_id: int
    user_id: int

    book_title: str
    author: str
    student_name: str | None = None

    issue_date: datetime
    due_date: datetime
    return_date: datetime | None = None

    fine: float
    status: str

    class Config:
        from_attributes = True

# ==========================
# PAGINATION SCHEMA
# ==========================

class PaginatedBooksResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    books: list[BookResponse]