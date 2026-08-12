import sqlite3
from sqlalchemy import text

from app.database import engine


# =====================================
# OLD SQLITE DATABASE PATH
# =====================================

SQLITE_DB = r"C:\Users\harsh\book-api-data\books.db"


def migrate():

    sqlite_conn = sqlite3.connect(SQLITE_DB)

    # Allows access using column names
    sqlite_conn.row_factory = sqlite3.Row

    sqlite_cursor = sqlite_conn.cursor()

    try:

        with engine.begin() as neon_conn:

            # =====================================
            # MIGRATE USERS
            # =====================================

            sqlite_cursor.execute("SELECT * FROM users")
            users = sqlite_cursor.fetchall()

            print(f"\nMigrating {len(users)} users...")

            for user in users:

                neon_conn.execute(
                    text("""
                        INSERT INTO users
                        (id, username, email, hashed_password, role)
                        VALUES
                        (:id, :username, :email, :hashed_password, :role)
                        ON CONFLICT (id) DO NOTHING
                    """),
                    {
                        "id": user["id"],
                        "username": user["username"],
                        "email": user["email"],
                        "hashed_password": user["hashed_password"],
                        "role": user["role"]
                    }
                )

            print("Users migrated successfully!")


            # =====================================
            # MIGRATE BOOKS
            # =====================================

            sqlite_cursor.execute("SELECT * FROM books")
            books = sqlite_cursor.fetchall()

            print(f"\nMigrating {len(books)} books...")

            for book in books:

                neon_conn.execute(
                    text("""
                        INSERT INTO books
                        (id, title, author, genre, price, published_year)
                        VALUES
                        (
                            :id,
                            :title,
                            :author,
                            :genre,
                            :price,
                            :published_year
                        )
                        ON CONFLICT (id) DO NOTHING
                    """),
                    {
                        "id": book["id"],
                        "title": book["title"],
                        "author": book["author"],
                        "genre": book["genre"],
                        "price": book["price"],
                        "published_year": book["published_year"]
                    }
                )

            print("Books migrated successfully!")


            # =====================================
            # MIGRATE CONTACTS
            # =====================================

            sqlite_cursor.execute("SELECT * FROM contacts")
            contacts = sqlite_cursor.fetchall()

            print(f"\nMigrating {len(contacts)} contacts...")

            for contact in contacts:

                neon_conn.execute(
                    text("""
                        INSERT INTO contacts
                        (id, name, email, subject, message, created_at)
                        VALUES
                        (
                            :id,
                            :name,
                            :email,
                            :subject,
                            :message,
                            :created_at
                        )
                        ON CONFLICT (id) DO NOTHING
                    """),
                    {
                        "id": contact["id"],
                        "name": contact["name"],
                        "email": contact["email"],
                        "subject": contact["subject"],
                        "message": contact["message"],
                        "created_at": contact["created_at"]
                    }
                )

            print("Contacts migrated successfully!")


            # =====================================
            # MIGRATE ISSUED BOOKS
            # =====================================

            sqlite_cursor.execute("SELECT * FROM issued_books")
            issued_books = sqlite_cursor.fetchall()

            print(
                f"\nMigrating {len(issued_books)} issued books..."
            )

            for issued in issued_books:

                neon_conn.execute(
                    text("""
                        INSERT INTO issued_books
                        (
                            id,
                            book_id,
                            user_id,
                            issue_date,
                            due_date,
                            return_date,
                            fine,
                            status
                        )
                        VALUES
                        (
                            :id,
                            :book_id,
                            :user_id,
                            :issue_date,
                            :due_date,
                            :return_date,
                            :fine,
                            :status
                        )
                        ON CONFLICT (id) DO NOTHING
                    """),
                    {
                        "id": issued["id"],
                        "book_id": issued["book_id"],
                        "user_id": issued["user_id"],
                        "issue_date": issued["issue_date"],
                        "due_date": issued["due_date"],
                        "return_date": issued["return_date"],
                        "fine": issued["fine"],
                        "status": issued["status"]
                    }
                )

            print("Issued books migrated successfully!")


        print("\n================================")
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("================================")

    except Exception as e:

        print("\nMIGRATION FAILED!")
        print(type(e).__name__)
        print(str(e))

    finally:

        sqlite_conn.close()


if __name__ == "__main__":
    migrate()