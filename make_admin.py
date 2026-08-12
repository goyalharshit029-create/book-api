from app.database import SessionLocal
from app.models import User

db = SessionLocal()

user = db.query(User).filter(
    User.email == "goyalharshit029@gmail.com"
).first()

if user:
    user.role = "admin"
    db.commit()
    print(f"{user.username} is now an ADMIN")
else:
    print("User not found")

db.close()