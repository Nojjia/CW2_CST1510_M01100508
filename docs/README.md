# Introduction

This is my submission for CST1510 Coursework 2.

# Week 8: Data Pipeline & CRUD (SQL)

Student Name: JUGGOO Nardev

Student ID: M01100508

Course: CST1510 - CW2 - Multi-DomainIntelligencePlatform

## Project Description

A command-line authentication system implementing secure password hashing.  This system allows users to register accounts and log-in with proper password, simillar to week 7, however it uses a database to store information

## Features

- Secure password hashing using bcrypt with automatic salt generation
- User registration with duplicate username prevention, and a validator
- Userlogin wit hpassword verification and a password validator that enforces strong password and don't allow common passwords to be chosen
- Databse storage of user information
- based user data persistence
- Password Strength Indicator
- Assign user role
- Account lockout on login attempt exceeding 3
- Session Duration of max 5 mins

## Technical Implementation

- Hashing Algorithm: bcrypt with automatic salting
- DataStorage: SQLite, with data loading of a `users.txt` file and loading of `{cyber_incidents,datasets_metadata,it_tickets}.csv` to gain access to those data
- Password Security: One-way hashing, no plain text storage
- Username Validation:  (3-20 alpha numeric characters)
- Password  (6-50 characters)
- Password Strength Indicator: Using a score which is incremented for 1, length greater than 8; 2, has upper case char; 3, has lower case; 4, has digit; 5, has special character; 6, is not part of a list of common passwords
- Assign user role: user, admin or analyst
- Account lockout on login attempt exceeding 3 for a user, using dict of list
- Session Duration: 5 mins, on until enter key presses, using sys and select

## Screenshots of project

### Using demo main function offered.

![Screenshot 1](screenshots/week_08-01.png)

### Using main function from week 7 to add interactivity and validations 
![Screenshot 1](screenshots/week_08-02.png)
![Screenshot 1](screenshots/week_08-03.png)
![Screenshot 1](screenshots/week_08-04.png)
![Screenshot 1](screenshots/week_08-05.png)