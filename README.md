# Introduction
This is my submission for CST1510 Coursework 2.

# Week 7: Secure Authentication System

Student Name: JUGGOO Nardev
Student ID: M01100508
Course: CST1510 - CW2 - Multi-DomainIntelligencePlatform

## Project Description
A command-line authentication system implementing secure password hashing.  This system allows users to register accounts and log-in with proper password

## Features
- Secure password hashing using bcrypt with automatic salt generation
- User registration with duplicate username prevention
- Userlogin wit hpassword verification
- Input validation for usernames and passwords
- File
- based user data persistence
- Password Strength Indicator
- Assign user role
- Account lockout on login attempt exceeding 3
- Session Duration of max 5 mins

## Technical Implementation
- Hashing Algorithm: bcrypt with automatic salting
- DataStorage: Plain text file (`users.txt`) with comma-separated values(csv)
- Password Security: One-way hashing, no plain text storage
- Validation: Username (3-20 alpha numeric characters), Password (6-50 characters)
- Password Strength Indicator: Using a score which is incremented for 1, length greater than 8; 2, has upper case char; 3, has lower case; 4, has digit; 5, has special character; 6, is not part of a list of common passwords
- Assign user role: user, admin or analyst
- Account lockout on login attempt exceeding 3 for a user, using dict of list
- Session Duration: 5 mins, on until enter key presses, using sys stdin
