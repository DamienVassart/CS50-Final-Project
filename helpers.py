import re
import math
import base64
import hashlib
from flask import Flask, redirect, render_template, request, session
from functools import wraps
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cs50 import SQL

# Ensure we are logged in:
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Compute password strength:
def strength(s):
    hasDigits = 10 if re.search("[0-9]", s) else 0
    hasLower = 26 if re.search("[a-z]", s) else 0
    hasUpper = 26 if re.search("[A-Z]", s) else 0
    hasSymbols = 33 if re.search("[^A-Za-z0-9]", s) else 0

    alphabetLength = hasDigits + hasLower + hasUpper + hasSymbols

    entropy = len(s) * (math.log(alphabetLength) / math.log(2))
    return round(entropy)

# Display an error page with a message:
def error(message):
    return render_template("error.html", message=message)

# Calculate usersname hash:
def uname_hash(s):
    hash_object = hashlib.sha256(bytes(s, 'utf-8'))
    hex_dig = hash_object.hexdigest()
    return bytes(hex_dig, 'utf-8')

# Generate an encryption key with user's master password:
def generate_pb_key(name, password):
    salt = uname_hash(name)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(bytes(password, 'utf-8')))

# Generate an encryption key for user's data:
def generate_key(name, masterkey):
    key = Fernet.generate_key()
    f = Fernet(masterkey)
    with open(f"user_keys/{uname_hash(name).decode('utf-8')}.key", "wb") as key_file:
        key_file.write(f.encrypt(key))
    key_file.close()

# Update user's data encryption key when user changes master password:
def update_key(name, key, new_pw):
    f = Fernet(new_pw)
    with open(f"user_keys/{uname_hash(name).decode('utf-8')}.key", "wb") as key_file:
        key_file.write(f.encrypt(key))
    key_file.close()

# Load user's encryption key:
def load_key(name, masterkey):
    f = Fernet(masterkey)
    return f.decrypt(open(f"user_keys/{uname_hash(name).decode('utf-8')}.key", "rb").read())

# Encrypt data:
def cipher(item, f):
    return f.encrypt(bytes(item, 'utf-8'))

# Decrypt entry:
def decrypt_entry(entry, f):
    for col in entry:
        if isinstance(entry[col], bytes):
            entry[col] = f.decrypt(entry[col]).decode('utf-8')
    return entry

# Find duplicates passwords:
def find_duplicates(l, k):
    return list(filter(lambda item: list(map(lambda item: item[k], l)).count(item[k]) > 1, l))

# Connect to user's database:
def db_connect(username):
    return SQL(f"sqlite:///user_dbs/{uname_hash(username).decode('utf-8')}.db")