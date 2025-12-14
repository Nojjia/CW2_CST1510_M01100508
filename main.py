#!/usr/bin/python
from app.utility.user_validations import validate_username, validate_password
from app.data.db import connect_database
from app.data.loaddata import load_csv_to_table_cyber_incident, load_csv_to_table_datasets_metadata, load_csv_to_table_it_tickets
from pathlib import Path
from app.data.db import DATA_DIR
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents
import sys, select, secrets, os, time
import pandas as pd
from app.data.db import DATA_DIR


def create_session():
    MAX_SESSION_DURATION = 5 # in minutes
    token = secrets.token_hex(16)
    # Store token with timestamp
    created_at = time.time()
    expires_at = created_at + (MAX_SESSION_DURATION * 60)
    created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created_at))
    expires_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires_at))
    return (token, created_at, expires_at, MAX_SESSION_DURATION)


def display_menu():

    print("\nWelcome to the Week 7 Authentication System!")
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
    # 1. Setup database
    conn = connect_database()


    create_all_tables(conn)
    migrate_users_from_file(conn)

    ACCOUNT_ROLES = ["user", "admin", "analyst"]
    LOCKOUT_DURATION = 5
    login_moderator = {"Username": [], "Attempts_Left": [], "Inital_Time_Locked": []}
    load_csv_to_table_cyber_incident(conn, DATA_DIR / "cyber_incident.csv", "cyber_incident")
    load_csv_to_table_datasets_metadata(conn, DATA_DIR / "datasets_metadata.csv", "datasets_metadata")
    load_csv_to_table_datasets_metadata(conn, DATA_DIR / "datasets_metadata.csv", "datasets_metadata")
    load_csv_to_table_it_tickets(conn, DATA_DIR / "it_tickets.csv", "it_tickets")

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
            success, msg = register_user(conn, username,password,role)
            print(msg)
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
            is_valid, role = login_user(conn, username,password)
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
                incident_id = insert_incident(conn,
                                              "2024-11-05",
                                              "Phishing",
                                              "High",
                                              "Open",
                                              "Suspicious email detected",
                                              "alice"
                                              )
                print(f"Created incident #{incident_id}")
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

    df = get_all_incidents(conn)
    conn.close()
    print(f"Total incidents: {len(df)}")

if __name__== "__main__":
    main()
