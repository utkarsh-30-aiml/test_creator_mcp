from database import get_connection

connection = get_connection()

print("=" * 70)
print("DATABASE CONNECTION TEST")
print("=" * 70)

print("✓ Connected to PostgreSQL")

connection.close()

print("✓ Connection closed")