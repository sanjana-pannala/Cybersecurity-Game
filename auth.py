import json
import os
import hashlib
import re

# File to store user data
USER_DB_FILE = 'users.json'

# Initialize the users database if it doesn't exist
def init_user_db():
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'w') as f:
            json.dump({"users": []}, f)

# Hash password for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Validate username (alphanumeric, 3-20 characters)
def is_valid_username(username):
    return bool(re.match(r'^[a-zA-Z0-9]{3,20}$', username))

# Validate password (at least 6 characters)
def is_valid_password(password):
    return len(password) >= 6

# Create a new user account
def create_account(username, password):
    init_user_db()
    
    # Check if username is valid
    if not is_valid_username(username):
        return False, "Username must be 3-20 characters and contain only letters and numbers."
    
    # Check if password is valid
    if not is_valid_password(password):
        return False, "Password must be at least 6 characters long."
    
    # Load existing users
    with open(USER_DB_FILE, 'r') as f:
        user_data = json.load(f)
    
    # Check if username already exists
    for user in user_data["users"]:
        if user["username"] == username:
            return False, "Username already exists."
    
    # Add new user
    user_data["users"].append({
        "username": username,
        "password": hash_password(password),
        "high_score": 0
    })
    
    # Save updated user data
    with open(USER_DB_FILE, 'w') as f:
        json.dump(user_data, f, indent=4)
    
    return True, "Account created successfully!"

# Sign in with username and password
def sign_in(username, password):
    init_user_db()
    
    # Load user data
    with open(USER_DB_FILE, 'r') as f:
        user_data = json.load(f)
    
    # Check if username exists and password is correct
    for user in user_data["users"]:
        if user["username"] == username and user["password"] == hash_password(password):
            return True, user
    
    return False, "Invalid username or password."

# Update user's high score
def update_high_score(username, score):
    init_user_db()
    
    # Load user data
    with open(USER_DB_FILE, 'r') as f:
        user_data = json.load(f)
    
    # Update high score if new score is higher
    for user in user_data["users"]:
        if user["username"] == username and score > user["high_score"]:
            user["high_score"] = score
    
    # Save updated user data
    with open(USER_DB_FILE, 'w') as f:
        json.dump(user_data, f, indent=4) 