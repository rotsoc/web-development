import time
import timeit
import humanize

from flask import url_for

from DB import *

import requests

#-------------------------------------#
# Utilities

def friendly_numbers(number, short_form = True):
    if len(str(number)) > 3 and len(str(number)) < 7:
        number_plus_k = str(number)[:len(str(number)) - 3] + "k"
        return number_plus_k

    elif len(str(number)) > 6:
        if short_form:
            items = humanize.intword(number).split(" ")
            return f"{items[0]} {items[1][:2]}"

        else:
            return humanize.intword(number)

    elif len(str(number)) < 4:
        return str(number)

# Timer decorator

def timed(func):
    def func_wrapper(*args, **kwargs):
        start = timeit.default_timer()
        print(f"{func.__name__} Start Time: {start}")

        func(*args, **kwargs)

        end = timeit.default_timer()
        print(f"{func.__name__} End Time: {end}")

        print(f"{func.__name__} Elapsed Time: {end - start}")

    return func_wrapper

#------------------------------------#

def get_average_rating(isbn):
    book_id = get_book_id(isbn)

    average_rating = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id = :book_id",
                                {"book_id": book_id}).fetchall()[0][0]

    if average_rating == None:
        average_rating = 0.0

    return float(average_rating)

def get_ratings_count(isbn):
    book_id = get_book_id(isbn)

    ratings_count = db.execute("SELECT COUNT(review) FROM reviews WHERE book_id = :book_id",
                               {"book_id": book_id}).fetchall()[0][0]

    if ratings_count == None:
        ratings_count = 0

    return int(ratings_count)

def get_book_cover(isbn, size):
    """Possible 'size' values: "large", "medium", "small", "original" """
    print("(i) Sleeping for 0.05 seconds, to comply with OpenLibrary's Rate Limiting...")
    time.sleep(0.05)

    if requests.get(f"https://covers.openlibrary.org/b/isbn/{isbn}-S.jpg?default=false").status_code == 404:
        return url_for("static", filename = "images/no_cover_available.png")

    if size == "large":
        return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

    if size == "medium":
        return f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

    if size == "small":
        return f"https://covers.openlibrary.org/b/isbn/{isbn}-S.jpg"

    if size == "original":
        return f"https://covers.openlibrary.org/b/isbn/{isbn}.jpg"

# DESCRIPTION:
# get_description(isbn)-->"Description[...]."

# DB: user_reviewed(user_id, book_id)-->(True/False, review_id/None)



def get_book_data(isbn, cover_size = "large", get_cover = True, get_description = True, get_bookviews_data = True):
    """cover_size possible values: "large", "medium", "small", "original" """
    if get_bookviews_data:
        bookviews_book_data = db.execute("SELECT title, name, year FROM books INNER JOIN authors ON authors.id = books.author_id WHERE isbn = :isbn LIMIT 1", {"isbn": str(isbn)}).fetchone()

        if bookviews_book_data is None:
            return None

    print("(i) Sleeping for 1 second, to comply with Goodreads' Developer Terms of Service...")
    time.sleep(1)
    goodreads_book_request = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "jhs2tdeIK5gzSWexrQ6B3A", "isbns": isbn})

    if goodreads_book_request.status_code != 200:
        raise Exception("REQUEST ERROR: Goodreads API request unsuccessful.")

    goodreads_book_data = goodreads_book_request.json()["books"][0]

    if get_cover:
        book_cover = get_book_cover(isbn, size = cover_size)

    else:
        book_cover = None

    if get_description:
        book_description_request = requests.get(f"https://googleapis.com/books/v1/volumes?q=isbn:{isbn}")

        if book_description_request.status_code != 200:
            book_description = None
            # raise Exception("REQUEST ERROR: Book description API request unsuccessful.")

        try:
            book_description = book_description_request.json()["items"][0]["volumeInfo"]["description"]

            # Temporary solution for limiting the length of the description
            try:
                book_description = book_description[:250] + "..."

            except:
                pass

        except:
            book_description = None

    else:
        book_description = None

    return {
        "isbn": isbn,
        "title": bookviews_book_data.title,
        "bookviews_average_rating": round(get_average_rating(isbn), 2),
        "bookviews_rating_count": get_ratings_count(isbn),
        "goodreads_average_rating": float(goodreads_book_data["average_rating"]),
        "goodreads_rating_count": humanize.intcomma(int(goodreads_book_data["work_ratings_count"])),
        "author": bookviews_book_data.name,
        "year": bookviews_book_data.year,
        "description": book_description,
        "cover": book_cover
        }

def get_books(search_term, search_by = "title", get_descriptions = True):
    """search_by possible values: "title", "author", "year", "all" """

    books_search = []

    # Search by title
    if search_by == "title":
        books_search = db.execute("SELECT * FROM books WHERE (regexp_replace(title, '[[:punct:]]', '') ILIKE regexp_replace(:title, '[[:punct:]]', '') OR (title ILIKE :title)",
                                  {"title": f"%{search_term}%"}).fetchall()

    # Search by author
    elif search_by == "author":
        author_name = search_term

        author_id = get_author_id(author_name)

        if author_id is None:
            books_search = []

        else:
            books_search = db.execute("SELECT * FROM books WHERE author_id = :author_id", {"author_id": author_id}).fetchall()

    # Search by year
    elif search_by == "year":
        books_search = db.execute("SELECT * FROM books WHERE year = :year", {"year": search_term}).fetchall()

    if books_search is None:
        return None

    # Get book data for each book
    books = []

    for book in books_search:
        books.append(get_book_data(book.isbn, cover_size = "medium", get_description = get_descriptions))

    if books is []:
        return None

    return books

#---------------------------------------------------------------------------------------------------------#

def get_book_id(isbn):
    """
    Returns id number that matches isbn.
    Returns None if no matches found.
    """
    book_id = db.execute("SELECT id FROM books WHERE isbn = :isbn LIMIT 1", {"isbn": str(isbn)}).fetchone()

    if book_id is None:
        return None

    return book_id[0]

def get_book_isbn(book_id):
    """
    Returns isbn number that matches book_id.
    Returns None if no matches found.
    """
    book_isbn = db.execute("SELECT isbn FROM books WHERE id = :book_id LIMIT 1", {"book_id": str(book_id)}).fetchone()

    if book_isbn is None:
        return None

    return book_isbn[0]

def get_author_id(author_name):
    """
    Returns id number that matches author_name.
    Returns None if no matches found.
    """

    author_id = db.execute("SELECT id FROM authors WHERE name = :author_name LIMIT 1", {"author_name": str(author_name)}).fetchone()

    if author_id is None:
        return None

    return int(author_id[0])

def get_author_name(author_id):
    """
    Returns name that matches author_id.
    Returns None if no matches found.
    """

    author_name = db.execute("SELECT name FROM authors WHERE id = :author_id LIMIT 1", {"author_id": author_id}).fetchone()

    if author_name is None:
        return None

    return author_name[0]

def get_isbns(search_term):
    isbns_query = db.execute("SELECT isbn FROM books WHERE isbn ILIKE :search_term", {"search_term": f"{str(search_term)}%"}).fetchall()

    if isbns_query is None:
        return None

    return [isbn[0] for isbn in isbns_query]

def get_authors(search_term):
    authors_query = db.execute("SELECT * FROM authors WHERE name ILIKE :search_term", {"search_term": f"%{str(search_term)}%"}).fetchall()

    if authors_query is None:
        return None

    return [author[0] for author in authors_query]
   
