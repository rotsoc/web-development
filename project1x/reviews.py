from DB import *

from books import get_book_id, get_book_isbn, get_book_data
from users import get_user_id, get_username, get_user_fullname

#-------------------------------------------------------------------------------------------#

def add_review(isbn, username, rating, review):
    book_id = get_book_id(isbn)
    user_id = get_user_id(username)

    db.execute("INSERT INTO reviews (book_id, user_id, rating, reviews) VALUES (:book_id, :user_id, :rating, :review)",
               {"book_id": book_id, "user_id": user_id, "rating": rating, "review": review})

    db.commit()

def get_book_reviews(isbn):
    book_id = get_book_id(isbn)

    reviews_query = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()

    if reviews_query == []:
        return None

    reviews = []
    for review in reviews_query:
        reviews.append({
            "id": review.id,
            "reviewer_name": get_user_fullname(get_username(review.user_id)),
            "rating": review.rating,
            "review_body": review.review,
            "pub_date": f"{review.pub_date.year}/{review.pub_date.month}/{review.pub_date.day}"
            })
    return reviews

def get_user_review(isbn, username):
    """
    Returns review(the first one) made by username to book(based on isbn).
    Returns None if username hasn't submitted any reviews to this particular book.
    """

    book_id = get_book_id(isbn)
    user_id = get_user_id(username)

    return db.execute("SELECT * FROM reviews WHERE (book_id = :book_id) AND (user_id = :user_id) LIMIT 1",
                      {"book_id": book_id, "user_id": user_id}).fetchone()

def get_user_reviews(username):
    """
    Returns a list of books that the username has submitted a review for.
    Returns None if username hasn't submitted any reviews.
    """

    user_id = get_user_id(username)

    books_search = db.execute("SELECT DISTINCT isbn, title, author_id, year FROM books INNER JOIN reviews ON reviews.book_id = books.id WHERE user_id = :user_id",
                              {"user_id": user_id}).fetchall()

    books = []
    reviews_ids = []

    for book in books_search:
        books.append(get_book_data(book.isbn, cover_size = "medium", get_description = False))
        reviews_ids.append(get_user_review(book.isbn, username).id)

    return {"books": books, "reviews_ids": reviews_ids}

