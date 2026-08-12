import sqlite3
from sqlalchemy import text

from app.database import engine


# ==========================================
# OLD SQLITE DATABASE
# ==========================================

sqlite_conn = sqlite3.connect("books.db")
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()


# Maps old SQLite IDs to new Neon IDs
book_id_map = {}
user_id_map = {}


try:

    with engine.begin() as neon_conn:

        # ==========================================
        # 1. MIGRATE USERS
        # ==========================================

        print("\nMigrating users...")

        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()

        users_added = 0
        users_skipped = 0

        for user in users:

            existing = neon_conn.execute(
                text("""
                    SELECT id
                    FROM users
                    WHERE LOWER(email) = LOWER(:email)
                """),
                {
                    "email": user["email"]
                }
            ).fetchone()

            if existing:

                print(f"User already exists: {user['email']}")

                user_id_map[user["id"]] = existing[0]

                users_skipped += 1
                continue

            result = neon_conn.execute(
                text("""
                    INSERT INTO users
                    (username, email, hashed_password, role)
                    VALUES
                    (:username, :email, :hashed_password, :role)
                    RETURNING id
                """),
                {
                    "username": user["username"],
                    "email": user["email"],
                    "hashed_password": user["hashed_password"],
                    "role": user["role"]
                }
            )

            new_user_id = result.scalar()

            user_id_map[user["id"]] = new_user_id

            users_added += 1

            print(
                f"Added user: {user['username']}"
            )


        # ==========================================
        # 2. MIGRATE BOOKS
        # DUPLICATE CHECK: TITLE + AUTHOR
        # ==========================================

        print("\nMigrating books...")

        sqlite_cursor.execute("SELECT * FROM books")
        books = sqlite_cursor.fetchall()

        books_added = 0
        books_skipped = 0

        for book in books:

            existing = neon_conn.execute(
                text("""
                    SELECT id
                    FROM books
                    WHERE LOWER(title) = LOWER(:title)
                    AND LOWER(author) = LOWER(:author)
                """),
                {
                    "title": book["title"],
                    "author": book["author"]
                }
            ).fetchone()

            if existing:

                print(
                    f"Skipping duplicate: "
                    f"{book['title']} - {book['author']}"
                )

                book_id_map[book["id"]] = existing[0]

                books_skipped += 1
                continue

            result = neon_conn.execute(
                text("""
                    INSERT INTO books
                    (title, author, genre, price, published_year)
                    VALUES
                    (
                        :title,
                        :author,
                        :genre,
                        :price,
                        :published_year
                    )
                    RETURNING id
                """),
                {
                    "title": book["title"],
                    "author": book["author"],
                    "genre": book["genre"],
                    "price": book["price"],
                    "published_year": book["published_year"]
                }
            )

            new_book_id = result.scalar()

            book_id_map[book["id"]] = new_book_id

            books_added += 1

            print(
                f"Added book: {book['title']}"
            )


        # ==========================================
        # 3. MIGRATE CONTACTS
        # ==========================================

        print("\nMigrating contacts...")

        sqlite_cursor.execute("SELECT * FROM contacts")
        contacts = sqlite_cursor.fetchall()

        contacts_added = 0

        for contact in contacts:

            existing = neon_conn.execute(
                text("""
                    SELECT id
                    FROM contacts
                    WHERE email = :email
                    AND message = :message
                """),
                {
                    "email": contact["email"],
                    "message": contact["message"]
                }
            ).fetchone()

            if existing:
                continue

            neon_conn.execute(
                text("""
                    INSERT INTO contacts
                    (
                        name,
                        email,
                        subject,
                        message,
                        created_at
                    )
                    VALUES
                    (
                        :name,
                        :email,
                        :subject,
                        :message,
                        :created_at
                    )
                """),
                {
                    "name": contact["name"],
                    "email": contact["email"],
                    "subject": contact["subject"],
                    "message": contact["message"],
                    "created_at": contact["created_at"]
                }
            )

            contacts_added += 1


        # ==========================================
        # 4. MIGRATE ISSUED BOOKS
        # ==========================================

        print("\nMigrating issued books...")

        sqlite_cursor.execute("SELECT * FROM issued_books")
        issued_books = sqlite_cursor.fetchall()

        issued_added = 0
        issued_skipped = 0

        for issue in issued_books:

            # Get corresponding new IDs
            new_book_id = book_id_map.get(
                issue["book_id"]
            )

            new_user_id = user_id_map.get(
                issue["user_id"]
            )

            if not new_book_id or not new_user_id:

                print(
                    f"Skipping issued record {issue['id']} "
                    f"- book/user mapping not found"
                )

                issued_skipped += 1
                continue

            # Prevent duplicate issued record
            existing = neon_conn.execute(
                text("""
                    SELECT id
                    FROM issued_books
                    WHERE book_id = :book_id
                    AND user_id = :user_id
                    AND issue_date = :issue_date
                """),
                {
                    "book_id": new_book_id,
                    "user_id": new_user_id,
                    "issue_date": issue["issue_date"]
                }
            ).fetchone()

            if existing:

                issued_skipped += 1
                continue

            neon_conn.execute(
                text("""
                    INSERT INTO issued_books
                    (
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
                        :book_id,
                        :user_id,
                        :issue_date,
                        :due_date,
                        :return_date,
                        :fine,
                        :status
                    )
                """),
                {
                    "book_id": new_book_id,
                    "user_id": new_user_id,
                    "issue_date": issue["issue_date"],
                    "due_date": issue["due_date"],
                    "return_date": issue["return_date"],
                    "fine": issue["fine"],
                    "status": issue["status"]
                }
            )

            issued_added += 1


    # ==========================================
    # MIGRATION SUCCESS
    # ==========================================

    print("\n=================================")
    print("MIGRATION COMPLETED SUCCESSFULLY")
    print("=================================")

    print(f"Users added: {users_added}")
    print(f"Users skipped: {users_skipped}")

    print(f"Books added: {books_added}")
    print(f"Books skipped: {books_skipped}")

    print(f"Contacts added: {contacts_added}")

    print(f"Issued books added: {issued_added}")
    print(f"Issued books skipped: {issued_skipped}")


except Exception as e:

    print("\n=================================")
    print("MIGRATION FAILED")
    print("=================================")

    print(type(e).__name__)
    print(e)


finally:

    sqlite_conn.close()