from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app import models


def get_recommendations(db, user_id, top_n=5):

    # ======================================
    # GET ALL BOOKS
    # ======================================

    books = db.query(
        models.Book
    ).all()

    if not books:
        return []


    # ======================================
    # GET STUDENT ISSUE HISTORY
    # ======================================

    issued_books = db.query(
        models.IssuedBook
    ).filter(
        models.IssuedBook.user_id == user_id
    ).all()


    # ======================================
    # GET ISSUED BOOK IDs
    # ======================================

    issued_book_ids = [
        issue.book_id
        for issue in issued_books
    ]


    # ======================================
    # COLD START
    # STUDENT HAS NO ISSUE HISTORY
    # ======================================

    if not issued_book_ids:

        recommendations = []

        for book in books[:top_n]:

            recommendations.append({
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "price": book.price,
                "published_year": book.published_year,
                "similarity_score": 0.0
            })

        return recommendations


    # ======================================
    # CREATE TEXT FEATURES
    # ======================================

    book_texts = []

    for book in books:

        text = " ".join([
            str(book.title or ""),
            str(book.author or ""),
            str(book.genre or "")
        ])

        book_texts.append(text)


    # ======================================
    # TF-IDF
    # ======================================

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(
        book_texts
    )


    # ======================================
    # FIND ISSUED BOOK INDEXES
    # ======================================

    issued_indexes = []

    for index, book in enumerate(books):

        if book.id in issued_book_ids:
            issued_indexes.append(index)


    # Safety fallback
    if not issued_indexes:

        return []


    # ======================================
    # CREATE STUDENT PROFILE
    # Average vectors of previously issued books
    # ======================================

    issued_vectors = tfidf_matrix[
        issued_indexes
    ]

    student_profile = issued_vectors.mean(
        axis=0
    )


    # Convert matrix to normal array
    student_profile = student_profile.A


    # ======================================
    # COSINE SIMILARITY
    # ======================================

    similarity_scores = cosine_similarity(
        student_profile,
        tfidf_matrix
    ).flatten()


    # ======================================
    # SORT BY SIMILARITY
    # ======================================

    recommended_indexes = (
        similarity_scores.argsort()[::-1]
    )


    recommendations = []

    for index in recommended_indexes:

        book = books[index]


        # Do not recommend books
        # already issued by this student
        if book.id in issued_book_ids:
            continue


        recommendations.append({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "price": book.price,
            "published_year": book.published_year,
            "similarity_score": round(
                float(similarity_scores[index]) * 100,
                2
            )
        })


        if len(recommendations) >= top_n:
            break


    return recommendations