import bcrypt
import csv

# Define your users and plain passwords here
users = [
    {"username": "alice", "password": "MySecret123"},
    {"username": "bob", "password": "BobPassword456"},
    {"username": "charlie", "password": "Charlie789"},
]

# Output CSV file
output_file = "users.csv"

with open(output_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["username", "password_hash"])  # Write header

    for user in users:
        username = user["username"]
        plain_password = user["password"]
        # Hash the password with bcrypt
        hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode()
        # Write to CSV
        writer.writerow([username, hashed_password])
        print(f"✅ Added user: {username} with hashed password.")

print(f"\n🎉 Done! File saved as '{output_file}'")
