#!/usr/bin/python
from pathlib import Path
import sys, select
import secrets
import os
import re
import time
import bcrypt

def hash_password(plain_password):
    # Encode the password to bytes
    plain_byte = plain_password.encode("utf-8")
    # [X] TODO: Generate a salt using bcrypt.gensalt()
    salt = bcrypt.gensalt()
    # [X] TODO: Hash the password using bcrypt.hashpw()
    hashed_byte = bcrypt.hashpw(plain_byte, salt)
    # [x] TODO: Decode the hash back to a string to store in a text filereturn
    hashed_password = hashed_byte.decode("utf-8")
    return hashed_password

def verify_password(plain_password, hashed_password):
    # [] TODO: Encode both the plaintext password and the stored hash to byte
    plain_byte = plain_password.encode("utf-8")
    hashed_byte = hashed_password.encode("utf-8")
    # [] TODO: Use bcrypt.checkpw() to verify the password
    # This function extracts the salt from the hash and compares
    is_password_correct = bcrypt.checkpw(plain_byte, hashed_byte)
    return is_password_correct

USER_DATA_FILE = "users.txt"

def register_user(username,password, role="user"):
    if user_exists(username):
        print(f"ERROR!!  Username {username} is already in use!!")
        return False
    hashed_password = hash_password(password)
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username},{hashed_password},{role}\n")
        print(f"User {username} has been successfully registered!!\nYou may now login using credentials of user {username}")
    return True

def user_exists(username):
    if not Path(USER_DATA_FILE).exists():
        Path(USER_DATA_FILE).touch()
        return False
    with open(USER_DATA_FILE, "r") as lines:
        for line in lines:
            if line.strip().split(",")[0] == username:
                return True
    return False

def login_user(username,password):
    # TODO: Handle the case where no users are registered yet
    # TODO: Search for the username in the file
    # TODO: If username matches, verify the password
    # TODO: If we reach here, the username was not found
    if not Path(USER_DATA_FILE).exists():
        Path(USER_DATA_FILE).touch()
        print(f"ERROR!!  USER CREDENTIALS DO NOT MATH!!!")
        return (False, "")

    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            f_username = line.strip().split(",")[0]
            if f_username == username:
                f_password = line.strip().split(",")[1]
                f_role = line.strip().split(",")[2]
                if verify_password(password, f_password):
                    print(f"User {username} has successfully logged in!!\n")
                    return (True, f"{f_role}")
                else:
                    break
    print(f"ERROR!!  USER CREDENTIALS DO NOT MATH!!!")
    return (False, "")

def create_session():
    MAX_SESSION_DURATION = 5 # in minutes
    token = secrets.token_hex(16)
    # Store token with timestamp
    created_at = time.time()
    expires_at = created_at + (MAX_SESSION_DURATION * 60)
    created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created_at))
    expires_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires_at))
    return (token, created_at, expires_at, MAX_SESSION_DURATION)


def validate_username(username):
    min_len = 4
    max_len = 20
    if not username:
        return (False, "Username cannot be empty")
    if username[0].isdigit():
        return (False, "Username cannot start with digit value")
    if len(username) < min_len:
        return (False, f"Username should at least be {min_len} characters long")
    if len(username) > max_len:
        return (False, f"Username can at most be {max_len} characters long")
    if " " in username:
        return (False, "Username should not contain spaces")
    for c in username:
        if not c.isalnum():
            return (False, "Username should not contain special characters")
    # TODO: add rejection for characters like $ % & and so on using regex
    return (True, "SUCCESS")

def validate_password(password):
    common_passwords = ["123456",
                        "password",
                        "123456789",
                        "12345678",
                        "12345",
                        "111111",
                        "1234567",
                        "sunshine",
                        "qwerty",
                        "iloveyou",
                        "princess",
                        "admin",
                        "welcome",
                        "666666",
                        "abc123",
                        "football",
                        "123123",
                        "monkey",
                        "654321",
                        "!@#$%^&*"]
    min_len = 6
    max_len = 50
    pwdlen = len(password)
    lower = upper = digit = special_char = score = 0
    if not password:
        return (False, "Password cannot be empty")
    if pwdlen < min_len:
        return (False, f"Password should at least be {min_len} characters long")
    if pwdlen > max_len:
        return (False, f"Password can at most be {max_len} characters long")
    if password[0].isspace() or password[-1].isspace():
        return (False, "Password can neither start nor end with spaces")
    for c in password:
        if not c.isalnum():
            special_char += 1
        elif c.islower():
            lower += 1
        elif c.isupper():
            upper += 1
        elif c.isdigit():
            digit += 1
        if lower and upper and digit:
            break
    if not lower and not upper and not digit:
        return (False, f"Password should contain both lower and upper case characters")
    if pwdlen > 8:
        score += 1
    if lower > 1:
        score += 1
    if upper > 1:
        score += 1
    if digit > 1:
        score += 1
    if special_char > 1:
        score += 1
    if password.lower() not in [pwd.lower() for pwd in common_passwords]:
        score += 1
    
    pwd_stren = "PASSWORD STRENGTH UNDETERMINED"
    if score < 2:
        pwd_stren = "WEAK!!  YOUR PASSWORD IS VERY WEAK"
    elif score < 4:
        pwd_stren = "MEDIUM.  YOUR PASSWORD IS OF MEDIUM STRENGTH"
    else:
        pwd_stren = "STRONG.  YOUR PASSWORD IS STRONG!"

    return (True, pwd_stren)

def display_menu():
    """Displays the main menu options."""
    print("\n"+"="*50)
    print("  MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print("  Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    """Main program loop."""
    ACCOUNT_ROLES = ["user",
                     "admin",
                     "analyst"]
    LOCKOUT_DURATION = 5
    print("\nWelcome to the Week 7 Authentication System!")

    # Here is the format of the data structure, attemps.
    # attempts will be a list of dictionaries
    login_moderator = {"Username": [], "Attempts_Left": [], "Inital_Time_Locked": []}
    while True:
        display_menu()
        choice=input("\nPlease select an option (1-3): ").strip()
        if choice=='1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username=input("Enter a username: ").strip()
            # Validate username
            is_valid,error_msg=validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            password=input("Enter a password: ").strip()
            # Validate password
            is_valid,pwd_msg=validate_password(password)
            if not is_valid:
                print(f"Error: {pwd_msg}")
                continue
            print(f"PASSWORD RATING: {pwd_msg}")
            # Confirm password
            password_confirm=input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue
            print("USER ROLES:")
            for role_index,role_value in enumerate(ACCOUNT_ROLES,1):
                print(f"\t[{role_index}]\t{role_value}")
            role_choice=input("Select a role (1-3): ").strip()
            if role_choice == "1":
                role = ACCOUNT_ROLES[0]
            elif role_choice == "2":
                role = ACCOUNT_ROLES[1]
            elif role_choice == "3":
                role = ACCOUNT_ROLES[2]
            else:
                print("Error: Role chosen is invalid")
                continue
            # Register the user
            register_user(username,password,role)
        elif choice=='2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username=input("Enter your username: ").strip()
            if username not in login_moderator["Username"]:
                login_moderator["Username"].append(username)
                login_moderator["Attempts_Left"].append(3)
                login_moderator["Inital_Time_Locked"].append(0)
                log_mod_i = login_moderator["Username"].index(username)
            elif login_moderator["Inital_Time_Locked"][log_mod_i] != 0:
                log_mod_i = login_moderator["Username"].index(username)
                if time.time() < (login_moderator["Inital_Time_Locked"][log_mod_i] + (LOCKOUT_DURATION * 60)):
                    print("You are currently locked out")
                    continue
                else:
                    print("The lockout duraction has ended!! You may attempt to log in again (max attemps 3)")

            password=input("Enter your password: ").strip()
            # Attempt login
            is_valid, role = login_user(username,password)
            if is_valid:
                _token,_created_at,_expires_at, session_duration = create_session()
                print("\nYou are logged-in as:")
                print(f"\tUSER: {username}")
                print(f"\tROLE: {role}")
                print("\nSession Info")
                print(f"\tSession Token: {_token}")
                print(f"\tCreated at: {_created_at}")
                print(f"\tExpires at: {_expires_at}")
                print("(In a real application, you would now access the dashboard)")
                # GO TO https://stackoverflow.com/questions/1335507/keyboard-input-with-timeout to re read
                print("\nPress Enter to return to main menu... or wait duration of session expiration")
                i, o, e = select.select( [sys.stdin], [], [], (session_duration * 60))
                print("Session ended")
                login_moderator["Username"].pop(log_mod_i)
                login_moderator["Attempts_Left"].pop(log_mod_i)
                login_moderator["Inital_Time_Locked"].pop(log_mod_i)
            else:
                login_moderator["Attempts_Left"][log_mod_i] -= 1
                attempt_left = login_moderator["Attempts_Left"][log_mod_i]
                print(f"You have {attempt_left} atemps left")
                if attempt_left == 0:
                    login_moderator["Inital_Time_Locked"][log_mod_i] = time.time()
                    print("You have been locked out for the duration of 5 minutes")
        elif choice=='3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__== "__main__":
    main()




"""
# TEMPORARY TEST CODE - Remove after testing
test_password="SecurePassword123"
# Test hashing
hashed=hash_password(test_password)
print(f"Original password: {test_password}")
print(f"Hashed password: {hashed}")
print(f"Hash length: {len(hashed)} characters")
# Test verification with correct password
is_valid=verify_password(test_password,hashed)
print(f"\nVerification with correct password: {is_valid}")
# Test verification with incorrect password
is_invalid=verify_password("WrongPassword",hashed)
print(f"Verification with incorrect password: {is_invalid}")
"""
