from database import get_connection

connection = get_connection()
cursor = connection.cursor()


cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")


tables = cursor.fetchall()


print("=" * 70)
print("DATABASE TABLES")
print("=" * 70)

for table in tables:
    print(f"✓ {table[0]}")


cursor.close()
connection.close()