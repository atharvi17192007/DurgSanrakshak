import firebase_admin
from firebase_admin import credentials, firestore

# Firebase key load
cred = credentials.Certificate("firebase_key.json")

# Firebase initialize
firebase_admin.initialize_app(cred)

# Firestore database connection
db = firestore.client()

print("Firebase Connected Successfully!")