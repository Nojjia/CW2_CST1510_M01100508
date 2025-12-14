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

