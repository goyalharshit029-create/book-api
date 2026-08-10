from sqlalchemy.orm import Session
from datetime import datetime

from app import models, schemas
from app.security import hash_password, verify_password


# ==========================
# USER CRUD
# ==========================

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_pwd = hash_password(user.password)

    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


# ==========================
# BOOK CRUD
# ==========================

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.model_dump())

    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book


def get_books(
    db: Session,
    title: str = None,
    author: str = None,
    genre: str = None,
    sort_by: str = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(models.Book)

    # Search by title
    if title:
        query = query.filter(
            models.Book.title.ilike(f"%{title}%")
        )

    # Search by author
    if author:
        query = query.filter(
            models.Book.author.ilike(f"%{author}%")
        )

    # Search by genre
    if genre:
        query = query.filter(
            models.Book.genre.ilike(f"%{genre}%")
        )

    # Sorting
    if sort_by == "title":
        query = query.order_by(models.Book.title)

    elif sort_by == "price":
        query = query.order_by(models.Book.price)

    elif sort_by == "year":
        query = query.order_by(models.Book.published_year)

    # Pagination
    total = query.count()

    books = query.offset(skip).limit(limit).all()

    return total, books


def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def update_book(db: Session, book_id: int, book: schemas.BookCreate):

    db_book = get_book(db, book_id)

    if not db_book:
        return None

    for key, value in book.model_dump().items():
        setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)

    return db_book


def delete_book(db: Session, book_id: int):

    db_book = get_book(db, book_id)

    if not db_book:
        return None

    db.delete(db_book)
    db.commit()

    return db_book


# ==========================
# CONTACT CRUD
# ==========================

def create_contact(db: Session, contact: schemas.ContactCreate):

    db_contact = models.Contact(**contact.model_dump())

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return db_contact


def get_contacts(db: Session):

    return db.query(models.Contact).order_by(
        models.Contact.created_at.desc()
    ).all()


# ==========================
# DASHBOARD STATS
# ==========================

def total_books(db: Session):
    return db.query(models.Book).count()


def total_users(db: Session):
    return db.query(models.User).count()


def total_contacts(db: Session):
    return db.query(models.Contact).count()

# ==========================
# ISSUED BOOK CRUD
# ==========================

def issue_book(
    db: Session,
    issued_book: schemas.IssuedBookCreate
):

    issue_date = datetime.utcnow()

    # Due date must be after issue date
    if issued_book.due_date <= issue_date:
        raise ValueError("Due date must be after issue date")

    # Get book details
    book = db.query(
        models.Book
    ).filter(
        models.Book.id == issued_book.book_id
    ).first()

    if not book:
        return None

    db_issued_book = models.IssuedBook(
        book_id=issued_book.book_id,
        user_id=issued_book.user_id,
        due_date=issued_book.due_date,
        issue_date=issue_date,
        fine=0.0,
        status="issued"
    )

    db.add(db_issued_book)
    db.commit()
    db.refresh(db_issued_book)

    # Add book information for response
    db_issued_book.book_title = book.title
    db_issued_book.author = book.author

    return db_issued_book


def get_issued_books(db: Session):

    results = db.query(
        models.IssuedBook,
        models.Book.title,
        models.Book.author,
        models.User.username
    ).join(
        models.Book,
        models.IssuedBook.book_id == models.Book.id
    ).join(
        models.User,
        models.IssuedBook.user_id == models.User.id
    ).order_by(
        models.IssuedBook.issue_date.desc()
    ).all()

    issued_books = []

    now = datetime.utcnow()

    for issued_book, title, author, username in results:

        # Calculate current fine for overdue books
        if (
            issued_book.status == "issued"
            and now > issued_book.due_date
        ):

            late_seconds = (
                now - issued_book.due_date
            ).total_seconds()

            late_days = int(
                late_seconds // (24 * 60 * 60)
            )

            issued_book.fine = late_days * 10

        # Currently issued but not overdue
        elif issued_book.status == "issued":

            issued_book.fine = 0.0

        issued_books.append({
            "id": issued_book.id,
            "book_id": issued_book.book_id,
            "user_id": issued_book.user_id,

            "book_title": title,
            "author": author,
            "student_name": username,

            "issue_date": issued_book.issue_date,
            "due_date": issued_book.due_date,
            "return_date": issued_book.return_date,

            "fine": issued_book.fine,
            "status": issued_book.status
        })

    db.commit()

    return issued_books


def get_user_issued_books(
    db: Session,
    user_id: int
):

    results = db.query(
        models.IssuedBook,
        models.Book.title,
        models.Book.author,
        models.User.username
    ).join(
        models.Book,
        models.IssuedBook.book_id == models.Book.id
    ).join(
        models.User,
        models.IssuedBook.user_id == models.User.id
    ).filter(
        models.IssuedBook.user_id == user_id
    ).order_by(
        models.IssuedBook.issue_date.desc()
    ).all()

    issued_books = []

    now = datetime.utcnow()

    for issued_book, title, author, username in results:

        # Calculate current fine for overdue active books
        if (
            issued_book.status == "issued"
            and now > issued_book.due_date
        ):

            late_seconds = (
                now - issued_book.due_date
            ).total_seconds()

            late_days = int(
                late_seconds // (24 * 60 * 60)
            )

            issued_book.fine = late_days * 10

        # Active but not overdue
        elif issued_book.status == "issued":

            issued_book.fine = 0.0

        issued_books.append({
            "id": issued_book.id,
            "book_id": issued_book.book_id,
            "user_id": issued_book.user_id,

            "book_title": title,
            "author": author,
            "student_name": username,

            "issue_date": issued_book.issue_date,
            "due_date": issued_book.due_date,
            "return_date": issued_book.return_date,

            "fine": issued_book.fine,
            "status": issued_book.status
        })

    db.commit()

    return issued_books


def get_issued_book(
    db: Session,
    issued_book_id: int
):

    return db.query(
        models.IssuedBook
    ).filter(
        models.IssuedBook.id == issued_book_id
    ).first()


def return_book(
    db: Session,
    issued_book_id: int
):

    issued_book = get_issued_book(
        db,
        issued_book_id
    )

    if not issued_book:
        return None

    # Already returned
    if issued_book.status == "returned":
        return issued_book

    return_date = datetime.utcnow()

    issued_book.return_date = return_date

    # Calculate late days
    if return_date > issued_book.due_date:

        late_seconds = (
            return_date - issued_book.due_date
        ).total_seconds()

        late_days = int(
            late_seconds // (24 * 60 * 60)
        )

        # ₹10 per late day
        issued_book.fine = late_days * 10

    else:

        issued_book.fine = 0.0

    issued_book.status = "returned"

    db.commit()
    db.refresh(issued_book)

    return issued_book