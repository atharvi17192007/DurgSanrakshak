# =====================================================
# make_admin.py — तुमचा स्वतःचा account Admin बनवण्यासाठी
# (हे एकदाच चालवायचं — तुमच्या signup केलेल्या email सकट)
# =====================================================

from db import get_db_connection

email = input("कोणता email Admin बनवायचा? ").strip().lower()

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT user_id, full_name FROM users WHERE email = ?", (email,))
user = cursor.fetchone()

if user is None:
    print("FAILED: हा email database मध्ये सापडला नाही.")
else:
    cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
    conn.commit()
    print("SUCCESS:", user['full_name'], "आता Admin आहे!")

conn.close()
