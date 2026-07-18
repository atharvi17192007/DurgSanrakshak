# =====================================================
# add_ticket_moderation_columns.py — help_tickets मध्ये
# 'is_hidden' column टाकण्यासाठी (एकदाच चालवायचं)
# =====================================================

from db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(help_tickets)")
existing_columns = [row['name'] for row in cursor.fetchall()]

if 'is_hidden' not in existing_columns:
    cursor.execute("ALTER TABLE help_tickets ADD COLUMN is_hidden INTEGER DEFAULT 0")
    conn.commit()
    print("SUCCESS: 'is_hidden' column takla!")
else:
    print("INFO: 'is_hidden' column aadhich ahe, kahi karaychi garaj nahi.")

conn.close()
