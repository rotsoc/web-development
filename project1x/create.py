import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#---------------------------------------------------------#

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#---------------------------------------------------------#

def main():
    # Creating "authors" table.
    db.execute("CREATE TABLE authors (id SERIAL PRIMARY KEY, name VARCHAR NOT NULL)")
    db.commit()
    print(f"Table 'authors' created.")

    # Creating "books" table.
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL UNIQUE, title VARCHAR NOT NULL, author_id INTEGER NOT NULL REFERENCES authors, year INTEGER)")
    db.commit()
    print(f"Table 'books' created.")

    # Creating 'users' table.
    db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL UNIQUE, fullname VARCHAR NOT NULL, password VARCHAR NOT NULL)")
    db.commit()
    print(f"Table 'users' created.")

    # Creating "reviews" table.
    db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, book_id INTEGER NOT NULL REFERENCES books, user_id INTEGER NOT NULL REFERENCES users, rating INTEGER NOT NULL, pub_date DATE DEFAULT CURRENT_DATE)")
    db.commit()
    print(f"Table 'reviews' created.")

#----------------------------------------------------------#

if __name__ == "__main__":
    main()
