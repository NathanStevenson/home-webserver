# auth_utils.py
import bcrypt

# Generates a salted + hashed password; embeds the salt into final hash
# Final hash format: $<bcrypt_version>$<cost>$salt$hashed_pwd : public salt ensures hackers need to launch brute force dict attack on individual users to get (easier to ban) - no repeated hashes
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# verifies password against a hashed password
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())