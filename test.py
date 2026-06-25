from auth import get_password_hash, verify_password

password = "admin123"

# Hash the password
hashed_password = get_password_hash(password)

print("Original Password:", password)
print("Hashed Password:", hashed_password)

# Verify the password
is_valid = verify_password(password, hashed_password)

print("Password Match:", is_valid)