from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models


SECRET_KEY = "your_secret_key_here_change_this_to_a_long_random_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ==========================
# DATABASE DEPENDENCY
# ==========================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================
# CREATE JWT TOKEN
# ==========================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==========================
# GET CURRENT USER
# ==========================

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid Token",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

        return email

    except JWTError:

        raise credentials_exception


# ==========================
# GET CURRENT USER FROM DB
# ==========================

def get_current_user_db(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


# ==========================
# ADMIN ONLY
# ==========================

def get_current_admin(
    current_user = Depends(get_current_user_db)
):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user


# ==========================
# STUDENT ONLY
# ==========================

def get_current_student(
    current_user = Depends(get_current_user_db)
):

    if current_user.role != "student":

        raise HTTPException(
            status_code=403,
            detail="Student access required"
        )

    return current_user