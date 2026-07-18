import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase connect
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# SQLite connect
conn = sqlite3.connect("durgsanrakshak.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Users data घ्या
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

# Firebase मध्ये टाका
for user in users:
    db.collection("users").document(str(user["user_id"])).set({
        "full_name": user["full_name"],
        "email": user["email"],
        "phone": user["phone"],
        "password": user["password"],
        "is_admin": bool(user["is_admin"]),
        "volunteer_level": user["volunteer_level"],
        "total_points": user["total_points"]
    })

print("Users migrated successfully!")

# =========================
# Migrate Forts
# =========================

cursor.execute("SELECT * FROM forts")
forts = cursor.fetchall()

for fort in forts:
    db.collection("forts").document(str(fort["fort_id"])).set({
        "fort_name": fort["fort_name"],
        "description": fort["description"],
        "latitude": fort["latitude"],
        "longitude": fort["longitude"],
        "fort_image": fort["fort_image"],
        "created_at": str(fort["created_at"])
    })

print("Forts migrated successfully!")

# =========================
# Migrate Events
# =========================
cursor.execute("SELECT COUNT(*) FROM events")
count = cursor.fetchone()[0]

print("Total events in SQLite:", count)
cursor.execute("SELECT * FROM events")
events = cursor.fetchall()

for event in events:
    db.collection("events").document(str(event["event_id"])).set({
        "event_name": event["event_name"],
        "description": event["description"],
        "fort_id": event["fort_id"],
        "community_id": event["community_id"],
        "created_by": event["created_by"],
        "event_date": event["event_date"],
        "event_time": event["event_time"],
        "status": event["status"],
        "max_participants": event["max_participants"],
        "qr_code": event["qr_code"],
        "created_at": str(event["created_at"])
    })

print("Events migrated successfully!")

# ===========================
# Migrate Event Participants inside Events
# ===========================

cursor.execute("""
SELECT ep.*, u.full_name, u.email, u.phone
FROM event_participants ep
JOIN users u ON ep.user_id = u.user_id
""")

participants = cursor.fetchall()

print(f"Total participants in SQLite: {len(participants)}")

for participant in participants:

    db.collection("events") \
      .document(str(participant["event_id"])) \
      .collection("participants") \
      .document(str(participant["user_id"])) \
      .set({

        "user_id": participant["user_id"],
        "full_name": participant["full_name"],
        "email": participant["email"],
        "phone": participant["phone"],
        "checkin_status": participant["checkin_status"],
        "joined_at": str(participant["joined_at"])

      })

print("Event Participants migrated inside Events successfully!")

# =========================
# Migrate Communities
# =========================

cursor.execute("SELECT * FROM communities")
communities = cursor.fetchall()

print("Total communities in SQLite:", len(communities))

for community in communities:

    db.collection("communities") \
      .document(str(community["community_id"])) \
      .set({

        "community_id": community["community_id"],
        "community_name": community["community_name"],
        "description": community["description"],
        "cover_image": community["cover_image"],
        "created_by": community["created_by"],
        "created_at": str(community["created_at"])

      })

print("Communities migrated successfully!")

# =========================
# Migrate Community Members
# =========================

cursor.execute("SELECT * FROM community_members")
members = cursor.fetchall()

print("Total community members in SQLite:", len(members))

for member in members:

    db.collection("communities") \
      .document(str(member["community_id"])) \
      .collection("members") \
      .document(str(member["user_id"])) \
      .set({

        "user_id": member["user_id"],
        "community_id": member["community_id"]

    })

print("Community Members migrated successfully!")
conn.close()