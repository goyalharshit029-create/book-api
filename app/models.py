from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database import Base


# ==========================
# BOOK MODEL
# ==========================

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String)
    price = Column(Float)
    published_year = Column(Integer)


# ==========================
# USER MODEL
# ==========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(String, default="student", nullable=False)


# ==========================
# CONTACT MODEL
# ==========================

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, nullable=False)

    subject = Column(String, nullable=False)

    message = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================
# ISSUED BOOK MODEL
# ==========================

class IssuedBook(Base):
    __tablename__ = "issued_books"

    id = Column(Integer, primary_key=True, index=True)

    book_id = Column(Integer, nullable=False)

    user_id = Column(Integer, nullable=False)

    issue_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    due_date = Column(DateTime, nullable=False)

    return_date = Column(DateTime, nullable=True)

    fine = Column(Float, default=0.0, nullable=False)

    status = Column(
        String,
        default="issued",
        nullable=False
    )