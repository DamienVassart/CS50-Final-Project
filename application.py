import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cryptography.fernet import Fernet

from helpers import login_required, strength, error, uname_hash, generate_pb_key, generate_key, update_key, load_key, cipher, decrypt_entry, find_duplicates, db_connect

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///users.db")


# Main Page:

@app.route("/")
@login_required
def index():
    # Load encryption key:
    f = Fernet(session.get('key'))
    # Connect to user's database:
    user_db = db_connect(session.get('username'))
    # Counting all the entries in user's database:
    row_count = user_db.execute("SELECT COUNT(id) AS count FROM data")[0]['count']
    # Select a specific folder:
    selected = request.args.get("folder")
    # Load all entries or only the entries in the selected folder:
    q = "SELECT * FROM data" if selected == None or selected == "*" else f"SELECT * FROM data WHERE folder ='{selected}'"
    data = user_db.execute(q)

    # Decrypt the loaded data:
    for entry in data:
        decrypt_entry(entry, f)
    # List all the existing folders and count the number of entries in each one:
    folders = user_db.execute("SELECT folder AS name, COUNT(*) AS count FROM data GROUP BY folder")
    # Find entries with duplicates passwords:
    duplicates = find_duplicates(data, 'password')
    # Find entries with a weak password:
    weak = user_db.execute(
        "SELECT id, title, password FROM data WHERE LENGTH(password) > 0 AND strength < 50")

    return render_template("index.html", row_count=row_count, data=data, folders=folders, duplicates=duplicates, weak=weak)


# Add a new entry:

@app.route("/add", methods = ["GET", "POST"])
@login_required
def add():
    # Load encryption key:
    f = Fernet(session.get('key'))
    # Connect to user's database:
    user_db = db_connect(session.get('username'))
    #  List all the existing folders:
    folders = user_db.execute("SELECT DISTINCT folder AS name FROM data")

    # Get user input:
    if request.method == "POST":
        title = request.form.get("title")
        url = request.form.get("url")
        login = request.form.get("login")
        password = request.form.get("password")
        note = request.form.get("note")
        folder = request.form.get("folder")
        new_folder = request.form.get("new-folder")

        # Insert the new entry in user's database:
        try:
            user_db.execute(
                "INSERT INTO data (title, url, login, password, strength, note, folder) VALUES(?, ?, ?, ?, ?, ?, ?)",
                cipher(title, f), cipher(url, f), cipher(login, f), cipher(password, f), strength(password) if password else 0, cipher(note, f), folder if folder else new_folder)

            return redirect("/")

        except:
            return error("The new entry could not be added")

    else:
        # Load password generator settings:
        pwdSettings = db.execute("SELECT pwlength, usedigits, uselower, useupper, usesymbols FROM users WHERE id = ?", session.get('user_id'))
        return render_template("add.html", folders=folders, pwdSettings=pwdSettings[0])


# Create an account:

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get input for username and password:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Check that username does not already exists:
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not username:
            message = "Username is required"
            return render_template("register.html", message=message)
        if len(rows) != 0:
            message = "Username already exists"
            return render_template("register.html", message=message)
        if not password:
            message = "Password is required"
            return render_template("register.html", message=message)
        if not confirmation or password != confirmation:
            message = "Password needs to be confirmed"
            return render_template("register.html", message=message)

        # Inserting new user:
        try:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))

            open(f"user_dbs/{uname_hash(username).decode('utf-8')}.db", "w+").close()
            user_db = db_connect(username)
            user_db.execute(
                "CREATE TABLE data (id INTEGER, title TEXT NOT NULL, url TEXT, login TEXT, password TEXT, strength INTEGER, note TEXT, folder TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(id))"
                )
            # Generate encryption key:
            masterkey = generate_pb_key(username, password)
            generate_key(username, masterkey)

            return redirect("/")

        except:
            return error("The registration process could not be completed")

    else:
        return render_template("register.html")


# Log in:

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        # Get input for username and password:
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            message = "Username is required"
            return render_template("login.html", message=message)
        if not password:
            message = "Password is required"
            return render_template("login.html", message=message)

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) == 0 or not check_password_hash(user[0]["hash"], password):
            message = "Invalid username and/or password"
            return render_template("login.html", message=message)

        # Create session data:
        session["user_id"] = user[0]["id"]
        session["username"] = user[0]["username"]
        session["key"] = load_key(user[0]["username"], generate_pb_key(username, password))

        return redirect("/")

    else:
        return render_template("login.html")



# Account Settings:

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user = db.execute("SELECT * FROM users WHERE id = ?", session.get("user_id"))
    username = user[0]["username"]

    if request.method == "POST":
        # User's master password required:
        current_password = request.form.get("current-password")
        if check_password_hash(user[0]["hash"], current_password):
            # Change master password:
            if request.form["action"] == "update-password":
                # Get user input:
                new_password = request.form.get("new-password")
                confirmation = request.form.get("confirmation")

                if not new_password:
                    message = "New password is needed"
                    return render_template("account.html", message=message, user=user[0])
                if not confirmation or new_password != confirmation:
                    message = "Password must be confirmed"
                    return render_template("account.html", message=message, user=user[0])

                db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(new_password), user[0]["id"])
                update_key(session.get('username'), session.get('key'), generate_pb_key(session.get('username'), new_password))

                return redirect("/")
            # Change password generator settings:
            elif request.form["action"] == "update-pw-settings":
                # Get user input:
                pwLength = request.form.get("pw-length")
                useDigits = request.form.get("use-digits")
                useLower = request.form.get("use-lower")
                useUpper = request.form.get("use-upper")
                useSymbols = request.form.get("use-symbols")

                if not pwLength:
                    message = "You must specify a password length"
                    return render_template("account.html", message=message, user=user[0])
                if not useDigits and not useLower and not useUpper and not useSymbols:
                    message = "You must select at least one character range"
                    return render_template("account.html", message=message, user=user[0])
                # Update settings in users database:
                db.execute(
                    "UPDATE users SET pwlength = ?, usedigits = ?, uselower = ?, useupper = ?, usesymbols = ? WHERE id = ?",
                    pwLength, 1 if useDigits else 0, 1 if useLower else 0, 1 if useUpper else 0, 1 if useSymbols else 0, user[0]["id"])

                return redirect("/")
            # Delete user account:
            elif request.form["action"] == "delete":
                os.remove(f"user_dbs/{uname_hash(username).decode('utf-8')}.db")
                os.remove(f"user_keys/{uname_hash(username).decode('utf-8')}.key")
                db.execute("DELETE FROM users WHERE id = ?", user[0]["id"])
                session.clear()
                return redirect("/")

        else:
            message = "Invalid password"
            return render_template("account.html", message=message, user=user[0])

    else:
        return render_template("account.html", user=user[0])



# Display an entry:

@app.route("/view")
@login_required
def entry():
    # Load encryption key:
    f = Fernet(session.get('key'))
    # Connect to users's database:
    user_db = db_connect(session.get('username'))
    # Load and decrypt entry data:
    entry = user_db.execute("SELECT * FROM data WHERE id = ?", request.args.get("id"))[0]
    decrypt_entry(entry, f)

    return render_template("view.html", entry=entry)


# Edit an entry:

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    # Load encryption key:
    f = Fernet(session.get('key'))
    # Connect to user's database:
    user_db = db_connect(session.get('username'))
    # List existing folders:
    folders = user_db.execute("SELECT DISTINCT folder AS name FROM data")

    if request.method == "POST":
        # Get user input:
        entry_id = request.form.get("id")
        title = request.form.get("title")
        url = request.form.get("url")
        login = request.form.get("login")
        password = request.form.get("password")
        note = request.form.get("note")
        folder = request.form.get("folder")
        new_folder = request.form.get("new-folder")
        # Update entry data in user's database:
        try:
            user_db.execute("UPDATE data SET title = ?, url = ?, login = ?, password = ?, strength = ?, note = ?, folder = ?, timestamp = CURRENT_TIMESTAMP WHERE id = ?",
                            cipher(title, f), cipher(url, f), cipher(login, f), cipher(password, f), strength(password) if password else 0, cipher(note, f), folder if folder else new_folder, entry_id)

            return redirect("/")

        except:
            return error("The entry could not be updated")

    else:
        # Load password generator settings
        pwdSettings = db.execute("SELECT pwlength, usedigits, uselower, useupper, usesymbols FROM users WHERE id = ?", session.get('user_id'))

        entry = user_db.execute("SELECT * FROM data WHERE id = ?", request.args.get("id"))[0]
        decrypt_entry(entry, f)

        return render_template("edit.html", entry=entry, folders=folders, pwdSettings=pwdSettings[0])



# Delete an entry:

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    # Load encryption key:
    f = Fernet(session.get('key'))
    # Connect to user's database:
    user_db = db_connect(session.get('username'))

    if request.method == "POST":
        # Delete the entry from user's database:
        try:
            user_db.execute("DELETE FROM data WHERE id = ?", request.form.get("id"))
            return redirect("/")
        except:
            return error("The entry could not be deleted")

    else:
        # Load and decrypt entry data:
        entry = user_db.execute("SELECT * FROM data WHERE id = ?", request.args.get("id"))[0]
        decrypt_entry(entry, f)
        return render_template("delete.html", entry=entry)


# Log out:

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")