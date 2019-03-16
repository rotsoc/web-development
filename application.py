from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session

from DB import *

import requests

from books import *
from users import *
from reviews import *

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#--------------------------------------------#
# Pages

@app.before_request
def redirect_unauthorized():
	redirect_conditions = [
			"username" not in session,
			request.endpoint != "index",
			request.endpoint != "user_login",
			(request.path != url_for("static", filename="css/BV_master.css")) and (request.path != url_for("static", filename="css/BV_index_page.css")) and (request.path != url_for("static", filename="images/background_home.jpg"))
	]
	
	if all(redirect_conditions):
		return redirect(url_for("index"))
		
		
# Misc.
@app.route("/")
def index():
	if "username" in session:
		return redirect(url_for("home"))
		
	return render_template("index.html")
	
@app.route("/Home")
def home():
	# if post-registration, notify user registered.
	
	return render_template("home.html")
	
@app.route("/Search", methods=["GET", "POST"])
def search():
	# TODO: Add authors container, to appear at the beginning of the search results if search term matches any authors
	# TODO: Add sorting capabilities and options
	
	if request.method != "POST":
		return redirect(url_for("home"))
		
	search_term = request.form.get("search-bar-input")
	
	if not search_term:
		return redirect(url_for("home"))
		
	if search_term.casefold().replace(" ", "") == "MyReviews".casefold():
		return redirect(url_for("user_reviews"))
		
	books = []
	
	isbns = get_isbns(search_term)
	
	for isbn in isbns:
		books.append(get_book_data(isbn, get_description=False))
		
	authors_ids = get_authors(search_term)
	
	for author_id in authors_ids:
		author_books_count = len(db.execute("SELECT * FROM books WHERE author_id = :author_id", {"author_id": author_id}).fetchall())
		
		books.append({"author": get_author_name(author_id), "number_of_books": author_books_count})
		
	books += get_books(search_term, search_by = "title", get_descriptions = False)
	
	return render_template("search_results.html", search_results = books, search_term = search_term)
	
@app.route("/Book/<string:isbn>", methods=["GET", "POST"])
def book(isbn):
	# TODO: Add option to delete a review
	
	book_data = get_book_data(isbn, cover_size = "large")
	
	if book_data is None:
		return render_template("error_404.html", info = {"type": "book", "message": isbn}, search_term = isbn)
		
	reviews = get_book_reviews(isbn)
	
	user_review = get_user_review(isbn, session["username"])
	
	return render_template("book.html", book = book_data, reviews = reviews, user_review = user_review, search_term = book_data["title"])
	
@app.route("/Book/<string:isbn>/NewReview")
def new_review(isbn, text_area = None):
	book_data = get_book_data(isbn, cover_size = "medium")
	
	if book_data is None:
		return render_template("error_404.html", info = {"type": "book", "message": isbn})
		
	session["submit_requests"] = 0
	
	return render_template("review_submission.html", book = book_data, search_term = book_data["title"])
	
@app.route("/Book/<string:isbn>/NewReview/submit", methods=["POST"])
def new_review_submit(isbn):
	if request.method != "POST":
		return "Method not allowed."
		
	if get_user_review(isbn, session["username"]) != None:
		return "You've already reviewed this book."
		
	session["submit_requests"] += 1
	
	if session.get("submit_requests") > 0:
		rating = request.form.get("rating-value")
		review = request.form.get("text-area")
		
		add_review(isbn, session.get("username"), rating, review)
		
		book_data = get_book_data(isbn, cover_size = "medium")
		
		reviews = get_book_reviews(isbn)
		
		return redirect(url_for("book", isbn = isbn, search_term = book_data["title"]))
		
	return redirect(url_for("book", isbn = isbn))
	
@app.route("/Author/<string:name>")
def author(name):
	books = get_books(name, search_by = "author")
	
	return render_template("search_results.html", search_results = books, search_term = name)
	
@app.route("/Year/<int:year>")
def year(year):
	books = get_books(year, search_by = "year")
	
	if books is None:
		return render_template("search_results.html", search_results = None)
		
	return render_template("search_results.html", search_results = books, search_term = year)
	
@app.route("/MyReviews")
def user_reviews():
	user_reviews = get_user_reviews(session.get("username"))
	
	return render_template("search_results.html", search_results=user_reviews["books"], user_reviews=user_reviews["reviews_ids"], search_term="MyReviews")
	
# @app.route("/Settings")
# def user_settings():
# 		return render_template("user_settings.html")

# Users
@app.route("/Login", methods=["POST"])
def user_login():
	if request.method != "POST":
		return redirect(url_for("index"))
		
	username = request.form.get("username_login")
	password = request.form.get("password_login")
	
	if not authorize_user(username, password):
		return "Username or Password incorrect. Try again, please!"
		
	session["username"] = username
	
	return  redirect(url_for("home"))
	
@app.route("/Register", methods=["POST"])
def user_register():
	if request.method != "POST":
		return redirect(url_for("index"))
		
	fullname = request.form.get("fullname_register")
	username = request.form.get("username_register")
	password = request.form.get("password_register")
	
	if username_exists(username):
		return "Username already taken. Choose a different one, please!"
		
	if not valid_password(password):
		return "Password must be at least 8 characters long and contain letters, numbers, uppercase, lowercase and symbols."
		
	register_user(username, fullname, password)
	
	
	session["username"] = username
	
	# TODO: send notification informing successful registration
	return redirect(url_for("home"))
	
@app.route("/Logout")
def user_logout():
	session.pop("username", None)
	
	return redirect(url_for("index"))
	
# Errors
@app.errorhandler(404)
def content_not_found(e):
	return render_template("error_404.html"), 404
	
#------------------------------------------------------------#
# API


	