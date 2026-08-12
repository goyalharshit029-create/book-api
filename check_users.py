from app.database import SessionLocal
from app.models import User

db = SessionLocal()

users = db.query(User).all()

for user in users:
    print(
        user.username,
        "|",
        user.email,
        "|",
        user.role
    )

db.close()
