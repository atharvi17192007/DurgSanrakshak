# =====================================================
# add_reply_column.py — help_tickets table मध्ये
# 'admin_reply' नावाचा नवीन column टाकण्यासाठी (एकदाच चालवायचं)
# =====================================================

from db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(help_tickets)")
existing_columns = [row['name'] for row in cursor.fetchall()]

if 'admin_reply' not in existing_columns:
    cursor.execute("ALTER TABLE help_tickets ADD COLUMN admin_reply TEXT")
    conn.commit()
    print("SUCCESS: 'admin_reply' column takla!")
else:
    print("INFO: 'admin_reply' column aadhich ahe, kahi karaychi garaj nahi.")

conn.close()
