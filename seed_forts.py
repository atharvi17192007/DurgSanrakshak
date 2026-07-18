# =====================================================
# seed_forts.py — Forts ची सुरुवातीची यादी DB मध्ये टाकण्यासाठी
# (हे फक्त एकदाच run करायचं — reference data, dummy demo data नाही)
# =====================================================

from db import get_db_connection

forts = [
    ("रायगड किल्ला", "छत्रपती शिवाजी महाराजांची राजधानी", 18.2360, 73.4400),
    ("सिंहगड किल्ला", "पुण्याजवळचा प्रसिद्ध ट्रेकिंग किल्ला", 18.3664, 73.7550),
    ("प्रतापगड किल्ला", "अफझलखान वधाच्या ऐतिहासिक प्रसंगाचा किल्ला", 17.9307, 73.5850),
    ("पन्हाळा किल्ला", "कोल्हापूर जवळचा ऐतिहासिक किल्ला", 16.8080, 74.1130),
    ("विशाळगड", "कोल्हापूर जिल्ह्यातील किल्ला", 16.1500, 73.9600),
    ("भूदरगड", "कोल्हापूर जिल्ह्यातील एक किल्ला", 16.4700, 74.0700),
]

conn = get_db_connection()
cursor = conn.cursor()

for name, desc, lat, lng in forts:
    cursor.execute("SELECT fort_id FROM forts WHERE fort_name = ?", (name,))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO forts (fort_name, description, latitude, longitude) VALUES (?, ?, ?, ?)",
            (name, desc, lat, lng)
        )

conn.commit()
conn.close()
print("SUCCESS: Forts data taken into database!")
