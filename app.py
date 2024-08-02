import os, datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SESSION_COOKIE_HTTPONLY'] = False
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tictactoe.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    if session.get("user_id"):
        username = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])[0]['username']
        return render_template("index.html", username = username)
    else:
        return render_template("index.html")

@app.route("/vs-player-local")
def vs_player_local():
    if session.get("user_id"):
        username = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])[0]['username']
        return render_template("vs-player-local.html", username = username)
    else:
        return render_template("vs-player-local.html")

@app.route("/profile-stats")
@login_required
def history():
    """Show player's wins, losses and win ratios"""
    user_scores = db.execute("SELECT pvc_easy_wins, pvc_easy_losses, pvc_easy_ties, pvc_normal_wins, pvc_normal_losses, pvc_normal_ties, pvc_hard_wins, pvc_hard_losses, pvc_hard_ties, pvp_wins, pvp_losses, pvp_ties FROM offline_scores WHERE user_id = ?;", session["user_id"])
    pvc_easy_ratio = "{:.2f}".format(db.execute("SELECT pvc_easy_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_easy_wins'] and (float(db.execute("SELECT pvc_easy_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_easy_wins']) / (float(db.execute("SELECT pvc_easy_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_easy_wins']) + float(db.execute("SELECT pvc_easy_losses FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_easy_losses']) + float(db.execute("SELECT pvc_easy_ties FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_easy_ties'])) or 0) * 100)+"%"
    pvc_normal_ratio = "{:.2f}".format(db.execute("SELECT pvc_normal_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_normal_wins'] and (float(db.execute("SELECT pvc_normal_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_normal_wins']) / (float(db.execute("SELECT pvc_normal_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_normal_wins']) + float(db.execute("SELECT pvc_normal_losses FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_normal_losses']) + float(db.execute("SELECT pvc_normal_ties FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_normal_ties'])) or 0) * 100)+"%"
    pvc_hard_ratio = "{:.2f}".format(db.execute("SELECT pvc_hard_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_hard_wins'] and (float(db.execute("SELECT pvc_hard_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_hard_wins']) / (float(db.execute("SELECT pvc_hard_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_hard_wins']) + float(db.execute("SELECT pvc_hard_losses FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_hard_losses']) + float(db.execute("SELECT pvc_hard_ties FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvc_hard_ties'])) or 0) * 100)+"%"
    pvp_offline_ratio = "{:.2f}".format(db.execute("SELECT pvp_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvp_wins'] and (float(db.execute("SELECT pvp_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvp_wins']) / (float(db.execute("SELECT pvp_wins FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvp_wins']) + float(db.execute("SELECT pvp_losses FROM offline_scores WHERE user_id = ?;", session["user_id"])[0]['pvp_losses'])) or 0) * 100)+"%"
    username = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])[0]['username']
    return render_template("profile-stats.html", user_scores = user_scores, pvc_easy_ratio = pvc_easy_ratio, pvc_normal_ratio = pvc_normal_ratio, pvc_hard_ratio = pvc_hard_ratio, pvp_offline_ratio = pvp_offline_ratio, username = username)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password is confirmed
        elif request.form.get("password") != request.form.get("confirmation") or not request.form.get("confirmation"):
            return apology("you typed two different passwords", 400)

        # Check database if username is already taken
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 0:
            return apology("username already taken", 400)

        # Add user info to database
        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password_hash)
        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)
        db.execute("INSERT INTO offline_scores (user_id, pvc_easy_wins, pvc_easy_losses, pvc_easy_ties, pvc_normal_wins, pvc_normal_losses, pvc_normal_ties, pvc_hard_wins, pvc_hard_losses, pvc_hard_ties, pvp_wins, pvp_losses, pvp_ties) VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)", user_id[0]["id"])

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route('/update-scores', methods = ['POST'])
@login_required
def get_scores_data():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        username = data.get('username')
        result = data.get('result')
        difficulty = data.get('difficulty')

        if difficulty == 'easy':
            if result == 'win':
                db.execute("UPDATE offline_scores SET pvc_easy_wins = pvc_easy_wins + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)
            elif result == 'lose':
                db.execute("UPDATE offline_scores SET pvc_easy_losses = pvc_easy_losses + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)
            elif result == 'tie':
                db.execute("UPDATE offline_scores SET pvc_easy_ties = pvc_easy_ties + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)

        elif difficulty == 'normal':
            if result == 'win':
                db.execute("UPDATE offline_scores SET pvc_normal_wins = pvc_normal_wins + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)
            elif result == 'lose':
                db.execute("UPDATE offline_scores SET pvc_normal_losses = pvc_normal_losses + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)
            elif result == 'tie':
                db.execute("UPDATE offline_scores SET pvc_normal_ties = pvc_normal_ties + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)

        elif difficulty == 'hard':
            if result == 'win':
                db.execute("UPDATE offline_scores SET pvc_hard_wins = pvc_hard_wins + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)
            elif result == 'lose':
                db.execute("UPDATE offline_scores SET pvc_hard_losses = pvc_hard_losses + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)
            elif result == 'tie':
                db.execute("UPDATE offline_scores SET pvc_hard_ties = pvc_hard_ties + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)

        elif difficulty == 'none - vs local player':
            if result == 'win':
                db.execute("UPDATE offline_scores SET pvp_wins = pvp_wins + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)
            elif result == 'lose':
                db.execute("UPDATE offline_scores SET pvp_losses = pvp_losses + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)
            elif result == 'tie':
                db.execute("UPDATE offline_scores SET pvp_ties = pvp_ties + 1 WHERE id = (SELECT id FROM users WHERE username = ?);", username)


        return '', 204
    except Exception as e:
        print(f"Error: {e}")
        return '', 500
