import sqlite3
import sys
from pathlib import Path


query = Path(sys.argv[1]).read_text(encoding="utf-8")
connection = sqlite3.connect(":memory:")
connection.execute("CREATE TABLE orders (price INTEGER NOT NULL)")
connection.execute("INSERT INTO orders (price) VALUES (2499)")
cursor = connection.execute(query)
row = cursor.fetchone()

assert row == (2499,)
assert cursor.description[0][0] == "price_in_cents"
stored_columns = [column[1] for column in connection.execute("PRAGMA table_info(orders)")]
assert stored_columns == ["price"]
