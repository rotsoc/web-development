from DB import *

from re import search as regex_search

from passlib.hash import argon2

#-------------------------------------------------------------------------------#
# Queries

def get_user_id(username):
    """
    Returns id number that matches username.
    Returns None if no matches found.
    """

    user_id = db.execute("SELECT id FROM users WHERE username = :username LIMIT 1", {"username": str(username)}).fetchone()

    if user_id is None:
        return None

    return user_id[0]

def get_username(user_id):
    """
    Returns username that matches user_id.
    Returns None if no matches found.
    """

    username = db.execute("SELECT username FROM users WHERE id = :user_id LIMIT 1", {"user_id": user_id}).fetchone()

    if username is None:
        return None

    return username[0]

def get_user_fullname(username):
    """
    Returns fullname that matches username.
    Returns None if no matches found.
    """

    user_fullname = db.execute("SELECT fullname FROM users WHERE username = :username LIMIT 1", {"username": str(username)}).fetchone()

    if user_fullname is None:
        return None

    return user_fullname[0]

#------------------------------------------------------------------------------#

def username_exists(username):
    username_query = db.execute("SELECT * FROM users WHERE username = :username LIMIT 1", {"username": str(username)}).fetchone()

    if username_query is None:
        return False

    return True

def valid_password(password):
    """
    Check the strength of "password".
    Returns a dict indicating the wrong criteria.
    A password is considered strong if:
        8 characters length or more;
        1 digit or more;
        1 symbol or more;
        1 uppercase letter or more;
        1 lowercase letter or more;
    """

    # Checking password length and searching for digits, uppercase, lowercase and symbols, respectively
    length_error = len(password) < 8
    digit_error = regex_search(r"\d", password) is None
    uppercase_error = regex_search(r"[A-Z]", password) is None
    lowercase_error = regex_search(r"[a-z]", password) is None
    symbol_error = regex_search(r"\W", password) is None

    if length_error or digit_error or uppercase_error or lowercase_error or symbol_error:
        return False

    return True

def authorize_user(username, password):
    """
    Returns True if username and password are correct.
    Returns False otherwise.
    """

    user = db.execute("SELECT password FROM users WHERE username = :username LIMIT 1", {"username": str(username)}).fetchone()

    if user is None:
        return None

    try:
        if argon2.verify(str(password), user.password):
            return True

        return False
    except:
        return False



#---------------------------------------------------------------------------------------------------------------#
# Fake User (temp)
class User:
    def __init__(self, user_id, name, username, password):
        self.user_id = user_id
        self.name = name
        self.username = username
        self.password = password

# NOTES:
# When deleting a user, make sure to delete their reviews before because user_id is referenced in the reviews table.
