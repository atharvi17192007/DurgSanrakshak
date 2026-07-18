# =====================================================
# app.py — DurgSanrakshak Main Flask Application
# =====================================================
#
# या टप्प्यात Signup आणि Login खऱ्या database शी जोडलेले आहेत.
# Password hashing (werkzeug) आणि Session (Flask cha built-in) वापरलंय.

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate(
    json.loads(os.environ.get("FIREBASE_KEY"))
)
firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)

# Session cha data encrypt karnyasathi ek secret key lagते.
# (हे project college submission साठी आहे — production मध्ये हे environment
# variable मध्ये ठेवायला हवं, पण आत्ता सोपं ठेवूया)
app.secret_key = 'durgsanrakshak_secret_key_2026'


@app.context_processor
def inject_is_admin():

    is_admin = False

    if 'user_id' in session:

        user_ref = db.collection("users").document(
            str(session['user_id'])
        )

        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            is_admin = user_data.get("is_admin", False)

    return dict(is_admin=is_admin)


# =====================================================
# PUBLIC PAGES (login/signup — login न करताच बघता येतात)
# =====================================================

@app.route('/')
def login_page():
    return render_template('login.html')


@app.route('/signup')
def signup_page():
    return render_template('signup.html')


# =====================================================
# SIGNUP — form submit झाल्यावर इथे data येतो
# =====================================================

@app.route('/api/signup', methods=['POST'])
def api_signup():

    full_name = request.form.get('fullName', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '').strip()


    # ---- Basic server-side validation ----
    if not full_name or not email or not password:
        return jsonify({
            "success": False,
            "message": "सगळे आवश्यक fields भरा."
        }), 400


    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "पासवर्ड किमान 6 अक्षरांचा हवा."
        }), 400



    # =====================================
    # Firebase मधे email check
    # =====================================

    existing_users = db.collection("users")\
        .where("email", "==", email)\
        .stream()
        

    for user in existing_users:
        return jsonify({
            "success": False,
            "message": "हा ईमेल आधीच नोंदणीकृत आहे."
        }), 409



    # =====================================
    # Password Hash
    # =====================================

    hashed_password = generate_password_hash(password)



    # =====================================
    # New User ID तयार करणे
    # =====================================

    user_docs = db.collection("users").stream()

    max_id = 0

    for doc in user_docs:
        try:
            doc_id = int(doc.id)

            if doc_id > max_id:
                max_id = doc_id

        except:
            pass


    new_user_id = str(max_id + 1)



    # =====================================
    # Save User in Firebase
    # =====================================

    db.collection("users")\
    .document(new_user_id)\
    .set({

        "full_name": full_name,
        "email": email,
        "phone": phone,
        "password": hashed_password,

        "total_points": 0,
        "volunteer_level": "Beginner",
        "is_admin": 0,

        "created_at": firestore.SERVER_TIMESTAMP
    })



    return jsonify({
        "success": True,
        "message": "नोंदणी यशस्वी झाली!"
    }), 201


# =====================================================
# LOGIN — form submit झाल्यावर इथे data येतो
# =====================================================

@app.route('/api/login', methods=['POST'])
def api_login():

    email = request.form.get('loginId', '').strip().lower()
    password = request.form.get('loginPass', '').strip()


    if not email or not password:
        return jsonify({
            "success": False,
            "message": "ईमेल आणि पासवर्ड टाका."
        }), 400



    # =====================================
    # Firebase मधून User शोधणे
    # =====================================
    print("Entered Email:", email)

    all_users = db.collection("users").stream()

    for u in all_users:
        print("Firebase Data:", u.to_dict())


    users = db.collection("users")\
        .where("email", "==", email)\
        .stream()


    user = None
    user_id = None


    for doc in users:
        user = doc.to_dict()
        user_id = doc.id
        break



    if user is None:
        return jsonify({
            "success": False,
            "message": "हा ईमेल नोंदणीकृत नाही."
        }), 404



    # =====================================
    # Password Check
    # =====================================

    if not check_password_hash(user["password"], password):
        return jsonify({
            "success": False,
            "message": "पासवर्ड चुकीचा आहे."
        }), 401



    # =====================================
    # Session Save
    # =====================================

    session['user_id'] = user_id
    session['full_name'] = user['full_name']


    return jsonify({
        "success": True,
        "message": "लॉगिन यशस्वी!",
        "redirect": url_for('home_page')
    }), 200


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# =====================================================
# PROTECTED PAGES (login केल्याशिवाय बघता येणार नाहीत)
# =====================================================

def login_required_redirect():
    """Login झालेला नसेल तर login page कडे पाठवण्यासाठी helper."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return None


@app.route('/home')
def home_page():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user_id = session['user_id']


    # =========================
    # Firebase Events Count
    # =========================
    event_docs = list(db.collection("events").stream())
    total_events = len(event_docs)


    # =========================
    # My Joined Events Count Firebase
    # =========================
    my_events_joined = 0

    for doc in event_docs:
        participant = db.collection("events")\
            .document(doc.id)\
            .collection("participants")\
            .document(str(user_id))\
            .get()

        if participant.exists:
            my_events_joined += 1



    # =========================
    # User Points & Level Firebase
    # =========================
    user_doc = db.collection("users").document(str(user_id)).get()

    if user_doc.exists:
        user_data = user_doc.to_dict()

        my_points = user_data.get("total_points", 0)
        my_points = int(my_points)
        my_level = user_data.get("volunteer_level", "Beginner")

    else:
        my_points = 0
        my_level = "Beginner"



    # =========================
    # Visited Forts Count Firebase
    # =========================
    visited_docs = db.collection("visited_forts")\
        .where("user_id", "==", user_id)\
        .stream()

    forts_visited = len(list(visited_docs))



    # =========================
    # Upcoming Events Firebase
    # =========================
    upcoming_events = []

    for doc in event_docs:

        event = doc.to_dict()

        if event.get("status") == "Upcoming":

            event["event_id"] = doc.id


            # Fort Name
            fort_name = "Unknown Fort"

            if event.get("fort_id"):

                fort_doc = db.collection("forts")\
                    .document(str(event["fort_id"]))\
                    .get()

                if fort_doc.exists:
                    fort_name = fort_doc.to_dict().get("fort_name")


            event["fort_name"] = fort_name

            upcoming_events.append(event)



    upcoming_events = sorted(
        upcoming_events,
        key=lambda x: x.get("event_date", "")
    )[:3]



    # =========================
    # Nearby Forts Firebase
    # =========================
    nearby_forts = []

    fort_docs = db.collection("forts").limit(3).stream()

    for doc in fort_docs:

        fort = doc.to_dict()

        fort["fort_id"] = doc.id

        nearby_forts.append(fort)



    # =========================
    # Leaderboard Firebase
    # =========================
    leaderboard = []

    user_docs = db.collection("users").stream()

    for doc in user_docs:

        user = doc.to_dict()

        leaderboard.append({
            "user_id": doc.id,
            "full_name": user.get("full_name"),
            "total_points": user.get("total_points", 0),
            "volunteer_level": user.get("volunteer_level", "Beginner")
        })



    leaderboard = sorted(
        leaderboard,
        key=lambda x: x.get("total_points", 0),
        reverse=True
    )[:5]



    return render_template(
        'home.html',
        full_name=session.get('full_name'),
        total_events=total_events,
        my_events_joined=my_events_joined,
        my_points=my_points,
        my_level=my_level,
        forts_visited=forts_visited,
        upcoming_events=upcoming_events,
        nearby_forts=nearby_forts,
        leaderboard=leaderboard,
        current_user_id=user_id
    )

@app.route('/event')
def event_page():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user_id = session['user_id']

    # =========================
    # Firebase मधून Forts आणणे
    # =========================
    forts = []

    fort_docs = db.collection("forts").stream()

    for doc in fort_docs:
        fort = doc.to_dict()
        fort["fort_id"] = int(doc.id)
        forts.append(fort)


    # =========================
    # Firebase मधून Events आणणे
    # =========================
    events = []

    event_docs = db.collection("events")\
                   .order_by("event_date")\
                   .stream()

    for doc in event_docs:
        print("EVENT:", doc.id, doc.to_dict())

        event = doc.to_dict()
        event["event_id"] = doc.id


        # Fort name शोधणे
        fort_doc = db.collection("forts")\
                     .document(str(event["fort_id"]))\
                     .get()

        if fort_doc.exists:
            event["fort_name"] = fort_doc.to_dict()["fort_name"]
        else:
            event["fort_name"] = "Unknown"


        # Participant count
        participants = db.collection("events")\
                         .document(doc.id)\
                         .collection("participants")\
                         .stream()

        participant_list = list(participants)

        event["participant_count"] = len(participant_list)


        # User ने join केलंय का?
        joined = db.collection("events")\
                   .document(doc.id)\
                   .collection("participants")\
                   .document(str(user_id))\
                   .get()

        event["already_joined"] = 1 if joined.exists else 0


        events.append(event)


    return render_template(
        'event.html',
        forts=forts,
        events=events,
        full_name=session.get('full_name')
    )

@app.route('/api/events/<event_id>/details')
def api_event_details(event_id):

    if 'user_id' not in session:
        return jsonify({
            "success": False,
            "message": "आधी लॉगिन करा."
        }), 401


    # Event
    event_doc = db.collection("events").document(str(event_id)).get()


    if not event_doc.exists:
        return jsonify({
            "success": False,
            "message": "Event सापडला नाही."
        }), 404


    event = event_doc.to_dict()



    # Fort name
    fort_name = "Unknown Fort"

    if event.get("fort_id"):

        fort_doc = db.collection("forts").document(
            str(event["fort_id"])
        ).get()

        if fort_doc.exists:
            fort_name = fort_doc.to_dict().get("fort_name")



    # Organizer
    organizer_name = "Unknown User"

    if event.get("created_by"):

        user_doc = db.collection("users").document(
            str(event["created_by"])
        ).get()

        if user_doc.exists:
            organizer_name = user_doc.to_dict().get("full_name")



    # Participants
    participants = []


    participant_docs = (
        db.collection("events")
        .document(str(event_id))
        .collection("participants")
        .stream()
    )


    for p in participant_docs:

        p_data = p.to_dict()

        participants.append(
            p_data.get("full_name")
        )



    return jsonify({

        "success": True,
        "event_name": event.get("event_name"),
        "fort_name": fort_name,
        "event_date": event.get("event_date"),
        "event_time": event.get("event_time"),
        "status": event.get("status"),
        "organizer_name": organizer_name,
        "participants": participants,
        "participant_count": len(participants)

    })

@app.route('/api/events/create', methods=['POST'])
def api_create_event():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    event_name = request.form.get('event_name', '').strip()
    description = request.form.get('description', '').strip()
    fort_id = request.form.get('fort_id')
    event_date = request.form.get('event_date')
    event_time = request.form.get('event_time')
    max_participants = request.form.get('max_participants') or None

    # पुढचा Event ID शोधा
    event_docs = db.collection("events").stream()

    max_id = 0

    for doc in event_docs:
        try:
            doc_id = int(doc.id)
            if doc_id > max_id:
                max_id = doc_id
        except ValueError:
            pass

    new_event_id = str(max_id + 1)

    event_ref = db.collection("events").document(new_event_id)

    event_ref.set({
        "event_name": event_name,
        "description": description,
        "fort_id": int(fort_id),
        "created_by": session['user_id'],
        "event_date": event_date,
        "event_time": event_time,
        "status": "Upcoming",
        "max_participants": int(max_participants) if max_participants else None,
        "qr_code": None,
        "community_id": None,
        "created_at": firestore.SERVER_TIMESTAMP
    })

    return redirect(url_for('event_page'))



@app.route('/api/events/<event_id>/delete', methods=['POST'])
def api_delete_event(event_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    # Firebase मधून event घ्या
    event_ref = db.collection("events").document(str(event_id))
    event_doc = event_ref.get()

    if not event_doc.exists:
        return redirect(url_for('event_page'))

    event = event_doc.to_dict()

    # फक्त organizer किंवा admin delete करू शकतो
    is_owner = event.get("created_by") == session['user_id']

    if not is_owner and not current_user_is_admin():
        return redirect(url_for('event_page'))


    # ✅ आधी participants subcollection delete करा
    participants_ref = event_ref.collection("participants")

    participants = participants_ref.stream()

    for participant in participants:
        participant.reference.delete()


    # ✅ मग event delete करा
    event_ref.delete()

    return redirect(url_for('event_page'))

@app.route('/api/events/<event_id>/join', methods=['POST'])
def api_join_event(event_id):

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']

    event_ref = db.collection("events").document(str(event_id))

    # event आहे का check
    event_doc = event_ref.get()

    if not event_doc.exists:
        return "Event not found", 404


    # already joined check
    participant_ref = event_ref.collection("participants").document(str(user_id))

    if participant_ref.get().exists:
        return redirect(url_for('event_page'))


    # user details Firebase users मधून घ्या
    user_doc = db.collection("users").document(str(user_id)).get()

    if user_doc.exists:
        user = user_doc.to_dict()

        participant_ref.set({
            "user_id": user_id,
            "full_name": user.get("full_name"),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "joined_at": firestore.SERVER_TIMESTAMP,
            "checkin_status": "Not Checked"
        })


    return redirect(url_for('event_page'))



# ---- Volunteer Level thresholds (points) ----
LEVEL_THRESHOLDS = [
    (500, 'Heritage Hero'),
    (200, 'Guardian'),
    (50, 'Explorer'),
    (0, 'Beginner'),
]

# ---- Redeem Catalog (आत्ता code मध्येच ठेवलंय, पुढे हवं तर वेगळं table बनवता येईल) ----
REDEEM_CATALOG = [
    {"key": "certificate", "name": "Participation Certificate", "cost": 50, "icon": "cert"},
    {"key": "badge", "name": "Special Badge", "cost": 100, "icon": "badge"},
    {"key": "tshirt", "name": "DurgSanrakshak T-Shirt", "cost": 250, "icon": "tshirt"},
    {"key": "coupon", "name": "Trekking Gear Coupon", "cost": 400, "icon": "coupon"},
]


def calculate_level(points):
    for threshold, level_name in LEVEL_THRESHOLDS:
        if points >= threshold:
            return level_name
    return 'Beginner'


@app.route('/wallet')
def wallet_page():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user_id = session['user_id']


    # -------- User points --------
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()

    if not user_doc.exists:
        return redirect(url_for('login_page'))

    user_data = user_doc.to_dict()

    my_points = user_data.get("total_points", 0)

    my_level = calculate_level(my_points)

    user_ref.update({
        "volunteer_level": my_level
    })


    # -------- Next level --------
    next_level_name = None
    points_needed = 0

    for threshold, level_name in reversed(LEVEL_THRESHOLDS):
        if my_points < threshold:
            next_level_name = level_name
            points_needed = threshold - my_points
            break



    # -------- Badges --------
    badges_display = []


    badges_docs = db.collection("badges").order_by(
        "points_required"
    ).stream()


    earned_docs = db.collection("user_badges").where(
        "user_id",
        "==",
        user_id
    ).stream()


    already_earned_ids = set()

    for doc in earned_docs:
        already_earned_ids.add(
            doc.to_dict().get("badge_id")
        )


    for doc in badges_docs:

        badge = doc.to_dict()

        badge_id = doc.id

        earned = my_points >= badge.get(
            "points_required",
            0
        )


        if earned and badge_id not in already_earned_ids:

            db.collection("user_badges").add({

                "user_id": user_id,
                "badge_id": badge_id,
                "created_at": firestore.SERVER_TIMESTAMP

            })


        badges_display.append({

            "badge_name": badge.get("badge_name"),
            "badge_type": badge.get("badge_type"),
            "points_required": badge.get("points_required"),
            "earned": earned

        })



    # -------- Wallet History --------
    transactions = []

    transaction_docs = db.collection(
        "wallet_transactions"
    ).where(
        "user_id",
        "==",
        user_id
    ).stream()


    for doc in transaction_docs:

        transaction = doc.to_dict()

        transaction["id"] = doc.id

        transactions.append(transaction)



    transactions.sort(
        key=lambda x: x.get("created_at"),
        reverse=True
    )
    print("MY POINTS:", my_points)
    print("REDEEM:", REDEEM_CATALOG)

    return render_template(
        "wallet.html",
        my_points=my_points,
        my_level=my_level,
        badges=badges_display,
        transactions=transactions,
        redeem_catalog=REDEEM_CATALOG,
        full_name=session.get("full_name")
    )

@app.route('/api/wallet/redeem', methods=['POST'])
def api_wallet_redeem():

    if 'user_id' not in session:
        return jsonify({
            "success": False,
            "message": "आधी लॉगिन करा."
        }), 401


    item_key = request.form.get('item_key')

    item = next(
        (i for i in REDEEM_CATALOG if i['key'] == item_key),
        None
    )


    if item is None:
        return jsonify({
            "success": False,
            "message": "अवैध item."
        }), 400



    user_id = str(session['user_id'])


    # Firebase user
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()


    if not user_doc.exists:
        return jsonify({
            "success": False,
            "message": "User सापडला नाही."
        }), 400



    user_data = user_doc.to_dict()

    current_points = user_data.get(
        "total_points",
        0
    )


    if current_points < item['cost']:

        return jsonify({
            "success": False,
            "message": "पुरेसे पॉईंट्स नाहीत."
        }), 400



    # Points कमी करा
    user_ref.update({

        "total_points": current_points - item['cost']

    })



    # Transaction Firebase मध्ये save

    db.collection("wallet_transactions").add({

        "user_id": user_id,
        "points": -item['cost'],
        "transaction_type": "Redeemed",
        "reason": item['name'] + " Redeem केलं",
        "created_at": firestore.SERVER_TIMESTAMP

    })



    return jsonify({

        "success": True,
        "message": item['name'] + " यशस्वीरित्या Redeem झालं!"

    })
@app.route('/community')
def community_page():

    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user_id = session['user_id']

    # ==========================
    # My Communities Firebase
    # ==========================

    my_communities = []


    all_communities = db.collection("communities").stream()


    for doc in all_communities:


        community_id = doc.id


        member_docs = db.collection("communities")\
                        .document(community_id)\
                        .collection("members")\
                        .where("user_id", "==", user_id)\
                        .stream()


        member_list = list(member_docs)


        if member_list:

            community = doc.to_dict()

            community["community_id"] = community_id


            all_members = db.collection("communities")\
                            .document(community_id)\
                            .collection("members")\
                            .stream()


            community["member_count"] = len(list(all_members))


            my_communities.append(community)



       # ==========================
    # Discover Communities
    # ==========================

    discover_communities = []


    all_communities = db.collection("communities").stream()


    for doc in all_communities:

        community_id = doc.id

        community = doc.to_dict()

        community["community_id"] = community_id



        # Members fetch

        member_docs = db.collection("communities")\
                        .document(community_id)\
                        .collection("members")\
                        .stream()


        member_list = list(member_docs)


        community["member_count"] = len(member_list)



        # Current user joined आहे का?

        joined = False

        for member in member_list:

            if str(member.to_dict().get("user_id")) == str(user_id):
                joined = True
                break



        # फक्त ज्या community मध्ये user नाही ती दाखवा

        if not joined:

            discover_communities.append(community)


    # ==========================
    # Active Community
    # ==========================

    active_id = request.args.get("community_id")


    if active_id is None and my_communities:
        active_id = my_communities[0]["community_id"]



    active_community = None
    posts = []


    if active_id:


        community_doc = db.collection("communities")\
                          .document(str(active_id))\
                          .get()


        if community_doc.exists:

            active_community = community_doc.to_dict()
            active_community["community_id"] = active_id
                        # Active community member count

            members = db.collection("communities")\
                        .document(str(active_id))\
                        .collection("members")\
                        .stream()


            active_community["member_count"] = len(list(members))


        # ==========================
        # Posts Firebase
        # ==========================

        post_docs = db.collection("communities")\
                      .document(str(active_id))\
                      .collection("posts")\
                      .stream()


        for post_doc in post_docs:

            post = post_doc.to_dict()

            post["post_id"] = post_doc.id


            # Author name

            user_doc = db.collection("users")\
                         .document(str(post.get("user_id")))\
                         .get()


            if user_doc.exists:
                post["author_name"] = user_doc.to_dict().get("full_name")
            else:
                post["author_name"] = "Unknown"


            posts.append(post)

 # ==========================
    # Return Community Page
    # ==========================

    return render_template(
        "community.html",
        full_name=session.get("full_name"),
        my_communities=my_communities,
        discover_communities=discover_communities,
        active_community=active_community,
        posts=posts,
        active_id=active_id
    )

@app.route('/api/community/create', methods=['POST'])
def api_create_community():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    user_id = session['user_id']


    if not name:
        return redirect(url_for('community_page'))


    # New community ID
    community_docs = db.collection("communities").stream()

    max_id = 0

    for doc in community_docs:
        try:
            if int(doc.id) > max_id:
                max_id = int(doc.id)
        except:
            pass


    new_id = str(max_id + 1)



    # Create community

    db.collection("communities").document(new_id).set({

        "community_name": name,
        "description": description,
        "created_by": user_id,
        "created_at": firestore.SERVER_TIMESTAMP

    })



       # Add creator as member inside community subcollection

    db.collection("communities")\
        .document(new_id)\
        .collection("members")\
        .document()\
        .set({

            "user_id": user_id,
            "joined_at": firestore.SERVER_TIMESTAMP

        })


    return redirect(url_for(
        'community_page',
        community_id=new_id
    ))


@app.route('/api/community/join/<int:community_id>', methods=['POST'])
def api_join_community(community_id):

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']


    community_ref = db.collection("communities")\
                     .document(str(community_id))


    # already joined check

    existing = community_ref.collection("members")\
                            .where("user_id","==",user_id)\
                            .stream()


    if len(list(existing)) == 0:

        community_ref.collection("members")\
        .document()\
        .set({

            "user_id": user_id,
            "joined_at": firestore.SERVER_TIMESTAMP

        })


    return redirect(url_for(
        'community_page',
        community_id=community_id
    ))


@app.route('/api/community/<int:community_id>/post', methods=['POST'])
def api_community_post(community_id):

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    content = request.form.get('content', '').strip()
    post_type = request.form.get('post_type', 'Discussion')

    if content:

        user_id = session['user_id']

        # Get user details from Firebase
        user_doc = db.collection("users").document(str(user_id)).get()

        user_name = "User"

        if user_doc.exists:
            user_name = user_doc.to_dict().get("full_name", "User")


        # Save post in Firebase
        db.collection("communities")\
          .document(str(community_id))\
          .collection("posts")\
          .add({
                "user_id": user_id,
                "user_name": user_name,
                "post_type": post_type,
                "content": content,
                "likes": [],
                "created_at": firestore.SERVER_TIMESTAMP
          })


    return redirect(url_for('community_page', community_id=community_id))

@app.route('/api/community/post/<post_id>/like', methods=['POST'])
def api_like_post(post_id):

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    community_id = request.form.get('community_id')
    user_id = str(session['user_id'])


    post_ref = db.collection("communities")\
        .document(str(community_id))\
        .collection("posts")\
        .document(post_id)


    post_doc = post_ref.get()


    if post_doc.exists:

        data = post_doc.to_dict()

        likes = data.get("likes", [])


        if user_id in likes:
            likes.remove(user_id)
        else:
            likes.append(user_id)


        post_ref.update({
            "likes": likes
        })


    return redirect(url_for(
        'community_page',
        community_id=community_id
    ))


@app.route('/api/community/post/<post_id>/comment', methods=['POST'])
def api_comment_post(post_id):

    if 'user_id' not in session:
        return redirect(url_for('login_page'))


    community_id = request.form.get("community_id")

    comment_text = request.form.get(
        "comment_text",
        ""
    ).strip()


    if comment_text:

        user_id = str(session['user_id'])


        user_doc = db.collection("users")\
            .document(user_id)\
            .get()


        user_name = "User"

        if user_doc.exists:
            user_name = user_doc.to_dict().get(
                "full_name",
                "User"
            )


        db.collection("communities")\
        .document(str(community_id))\
        .collection("posts")\
        .document(post_id)\
        .collection("comments")\
        .add({

            "user_id": user_id,
            "user_name": user_name,
            "comment_text": comment_text,
            "created_at": firestore.SERVER_TIMESTAMP

        })


    return redirect(url_for(
        'community_page',
        community_id=community_id
    ))

def current_user_is_admin():
    """सध्याचा logged-in user Admin आहे का, हे तपासण्यासाठी."""

    if 'user_id' not in session:
        return False

    user_doc = db.collection("users").document(
        str(session['user_id'])
    ).get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data.get("is_admin", False)

    return False


@app.route('/api/community/post/<post_id>/delete', methods=['POST'])
def api_delete_post(post_id):

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    if not current_user_is_admin():
        return redirect(url_for('community_page'))


    community_id = request.form.get('community_id')


    # Firebase post delete
    post_ref = (
        db.collection("communities")
        .document(str(community_id))
        .collection("posts")
        .document(str(post_id))
    )


    post_doc = post_ref.get()


    if post_doc.exists:
        post_ref.delete()


    return redirect(
        url_for(
            'community_page',
            community_id=community_id
        )
    )




@app.route('/location')
def location_page():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    user_id = session['user_id']

    forts_raw = []

    forts_docs = db.collection("forts").stream()

    for doc in forts_docs:
        fort = doc.to_dict()

        fort["fort_id"] = doc.id

        # visited check
        visited = False

        visited_docs = db.collection("visited_forts").where(
            "fort_id",
            "==",
            doc.id
        ).where(
            "user_id",
            "==",
            user_id
        ).stream()

        for v in visited_docs:
            visited = True
            break


        # event count
        event_count = 0

        events_docs = db.collection("events").where(
            "fort_id",
            "==",
            doc.id
        ).stream()

        for e in events_docs:
            event_count += 1


        fort["visited"] = 1 if visited else 0
        fort["event_count"] = event_count

        forts_raw.append(fort)



    position_slots = [
        (30,35),
        (55,20),
        (70,55),
        (25,70),
        (80,80),
        (45,45),
        (60,15),
        (15,60)
    ]


    forts = []

    for i, fort in enumerate(forts_raw):
        fort["map_top"], fort["map_left"] = position_slots[i % len(position_slots)]
        forts.append(fort)


    return render_template(
        'location.html',
        full_name=session.get('full_name'),
        forts=forts
    )


@app.route('/api/forts/mark-visited/<fort_id>', methods=['POST'])
def api_mark_visited(fort_id):

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']

    # आधी check करा already visited आहे का
    existing = db.collection("visited_forts").where(
        "fort_id",
        "==",
        fort_id
    ).where(
        "user_id",
        "==",
        user_id
    ).stream()


    already_exists = False

    for doc in existing:
        already_exists = True
        break


    # नवीन visit add
    if not already_exists:

        db.collection("visited_forts").add({

            "fort_id": fort_id,
            "user_id": user_id,
            "visited": True,
            "created_at": firestore.SERVER_TIMESTAMP

        })


    return redirect(url_for('location_page'))


@app.route('/help')
def help_page():
    redirect_response = login_required_redirect()
    if redirect_response:
        return redirect_response

    submitted = request.args.get("submitted")

    tickets = []

    docs = (
        db.collection("help_tickets")
        .where("user_id", "==", session["user_id"])
        .where("is_hidden", "==", False)
        .stream()
    )

    for doc in docs:
        ticket = doc.to_dict()
        ticket["id"] = doc.id
        tickets.append(ticket)

    tickets.sort(
        key=lambda x: x.get("created_at", firestore.SERVER_TIMESTAMP),
        reverse=True
    )

    return render_template(
        "help.html",
        full_name=session.get("full_name"),
        submitted=submitted,
        my_tickets=tickets
    )


@app.route('/api/help/report', methods=['POST'])
def api_help_report():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    subject = request.form.get('subject', '').strip()
    description = request.form.get('description', '').strip()

    if subject and description:

        db.collection("help_tickets").add({

            "user_id": session["user_id"],
            "full_name": session.get("full_name"),
            "email": session.get("email"),
            "subject": subject,
            "description": description,
            "status": "Pending",
            "is_hidden": False,
            "created_at": firestore.SERVER_TIMESTAMP

        })

    return redirect(url_for("help_page", submitted="report"))


@app.route('/api/help/feedback', methods=['POST'])
def api_help_feedback():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    rating = request.form.get("rating", "0")
    text = request.form.get("feedback_text", "").strip()

    db.collection("help_tickets").add({

        "user_id": session["user_id"],
        "full_name": session.get("full_name"),
        "email": session.get("email"),
        "subject": f"Feedback ({rating}/5 stars)",
        "description": text if text else "कुठलाही मजकूर लिहिला नाही.",
        "status": "Completed",
        "is_hidden": False,
        "created_at": firestore.SERVER_TIMESTAMP

    })

    return redirect(url_for("help_page", submitted="feedback"))

@app.route('/api/help/contact-admin', methods=['POST'])
def api_help_contact_admin():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    message = request.form.get("message", "").strip()

    if message:

        db.collection("help_tickets").add({

            "user_id": session["user_id"],
            "full_name": session.get("full_name"),
            "email": session.get("email"),
            "subject": "Admin शी संपर्क",
            "description": message,
            "status": "Pending",
            "is_hidden": False,
            "created_at": firestore.SERVER_TIMESTAMP

        })

    return redirect(url_for("help_page", submitted="contact"))


def admin_required_redirect():
    """Admin नसेल तर Home कडे redirect."""

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_doc = db.collection("users").document(
        str(session['user_id'])
    ).get()

    if not user_doc.exists:
        return redirect(url_for('home_page'))

    user_data = user_doc.to_dict()

    if not user_data.get("is_admin", False):
        return redirect(url_for('home_page'))

    return None


@app.route('/admin')
def admin_dashboard():
    redirect_response = admin_required_redirect()
    if redirect_response:
        return redirect_response


    # Total Users
    users_docs = db.collection("users").stream()
    total_users = sum(1 for _ in users_docs)


    # Total Events
    events_docs = db.collection("events").stream()
    total_events = sum(1 for _ in events_docs)


    # Open/Pending Tickets
    open_tickets = 0

    tickets_docs = db.collection("help_tickets").stream()

    for doc in tickets_docs:
        ticket = doc.to_dict()

        if ticket.get("status") in ["Pending", "Open"]:
            open_tickets += 1


    # Pending Gallery Photos
    pending_photos = 0

    gallery_docs = db.collection("event_gallery").where(
        "verification_status",
        "==",
        "Pending"
    ).stream()

    for doc in gallery_docs:
        pending_photos += 1


    return render_template(
        'admin/dashboard.html',
        full_name=session.get('full_name'),
        total_users=total_users,
        total_events=total_events,
        open_tickets=open_tickets,
        pending_photos=pending_photos
    )

@app.route('/admin/tickets')
def admin_tickets():
    redirect_response = admin_required_redirect()
    if redirect_response:
        return redirect_response

    feedback_tickets = []
    contact_tickets = []
    report_tickets = []

    docs = db.collection("help_tickets").stream()

    for doc in docs:
        ticket = doc.to_dict()

        # Firestore document id
        ticket["ticket_id"] = doc.id

        subject = ticket.get("subject", "")

        if subject.startswith("Feedback ("):
            feedback_tickets.append(ticket)

        elif subject == "Admin शी संपर्क":
            contact_tickets.append(ticket)

        else:
            report_tickets.append(ticket)


    # नवीन tickets वर ठेवण्यासाठी sorting
    feedback_tickets.sort(
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )

    contact_tickets.sort(
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )

    report_tickets.sort(
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )


    return render_template(
        'admin/tickets.html',
        full_name=session.get('full_name'),
        report_tickets=report_tickets,
        feedback_tickets=feedback_tickets,
        contact_tickets=contact_tickets
    )

@app.route('/api/admin/tickets/<ticket_id>/resolve', methods=['POST'])
def api_admin_resolve_ticket(ticket_id):

    redirect_response = admin_required_redirect()
    if redirect_response:
        return redirect_response

    reply_text = request.form.get('admin_reply','').strip()

    db.collection("help_tickets").document(ticket_id).update({
        "status": "Resolved",
        "admin_reply": reply_text
    })

    return redirect(url_for('admin_tickets'))

@app.route('/api/admin/tickets/<ticket_id>/edit', methods=['POST'])
def api_admin_edit_ticket(ticket_id):

    redirect_response = admin_required_redirect()
    if redirect_response:
        return redirect_response

    subject = request.form.get('subject', '').strip()
    description = request.form.get('description', '').strip()

    db.collection("help_tickets").document(ticket_id).update({
        "subject": subject,
        "description": description
    })

    return redirect(url_for('admin_tickets'))


@app.route('/api/admin/tickets/<ticket_id>/delete', methods=['POST'])
def api_admin_delete_ticket(ticket_id):

    redirect_response = admin_required_redirect()
    if redirect_response:
        return redirect_response

    db.collection("help_tickets").document(ticket_id).delete()

    return redirect(url_for('admin_tickets'))


@app.route('/api/admin/tickets/<ticket_id>/toggle-hide', methods=['POST'])
def api_admin_toggle_hide_ticket(ticket_id):

    redirect_response = admin_required_redirect()
    if redirect_response:
        return redirect_response

    doc_ref = db.collection("help_tickets").document(ticket_id)

    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()

        current_value = data.get("is_hidden", False)

        doc_ref.update({
            "is_hidden": not current_value
        })

    return redirect(url_for('admin_tickets'))


@app.route('/admin/events')
def admin_events():
    redirect_response = admin_required_redirect()
    if redirect_response:
        return redirect_response

    events = []

    event_docs = db.collection("events").stream()

    for doc in event_docs:
        event = doc.to_dict()

        # Firebase document id
        event["event_id"] = doc.id

        # Fort name मिळवणे
        fort_name = "Unknown Fort"

        if event.get("fort_id"):
            fort_doc = db.collection("forts").document(str(event["fort_id"])).get()

            if fort_doc.exists:
                fort_name = fort_doc.to_dict().get("fort_name")


        # Organizer name मिळवणे
        organizer_name = "Unknown User"

        if event.get("created_by"):
            user_doc = db.collection("users").document(str(event["created_by"])).get()

            if user_doc.exists:
                organizer_name = user_doc.to_dict().get("full_name")


                # Participants details Firebase मधून
        participants_list = []

        participant_docs = (
            db.collection("events")
            .document(doc.id)
            .collection("participants")
            .stream()
        )

        for p_doc in participant_docs:

            participant = p_doc.to_dict()

            participants_list.append({

                "user_id": participant.get("user_id"),
                "full_name": participant.get("full_name"),
                "email": participant.get("email"),
                "checkin_status": participant.get(
                    "checkin_status",
                    "Not Checked"
                )

            })


        event["participants"] = participants_list
        event["participant_count"] = len(participants_list)

        event["fort_name"] = fort_name
        event["organizer_name"] = organizer_name


        events.append(event)


    return render_template(
        'admin/events.html',
        full_name=session.get('full_name'),
        events=events
    )


@app.route('/api/admin/events/<int:event_id>/status', methods=['POST'])
def api_admin_update_event_status(event_id):

    redirect_response = admin_required_redirect()
    if redirect_response:
        return redirect_response

    new_status = request.form.get('status')

    if new_status not in ('Upcoming', 'Ongoing', 'Completed', 'Cancelled'):
        return redirect(url_for('admin_events'))


    # Event update
    event_ref = db.collection("events").document(str(event_id))
    event_doc = event_ref.get()

    if not event_doc.exists:
        return redirect(url_for('admin_events'))


    event_data = event_doc.to_dict()

    event_ref.update({
        "status": new_status
    })


    # ==============================
    # COMPLETED झाल्यावर points देणे
    # ==============================

    if new_status == "Completed":

        participants = (
            db.collection("events")
            .document(str(event_id))
            .collection("participants")
            .stream()
        )


        for participant_doc in participants:

            participant = participant_doc.to_dict()

            if participant.get("checkin_status") == "Checked":

                user_id = str(participant.get("user_id"))

                user_ref = db.collection("users").document(user_id)

                user_doc = user_ref.get()


                if user_doc.exists:

                    user_data = user_doc.to_dict()

                    current_points = user_data.get(
                        "total_points",
                        0
                    )


                    # duplicate transaction check
                    transaction_check = (
                        db.collection("wallet_transactions")
                        .where(
                            "user_id",
                            "==",
                            user_id
                        )
                        .where(
                            "event_id",
                            "==",
                            event_id
                        )
                        .stream()
                    )


                    already_added = False

                    for t in transaction_check:
                        already_added = True
                        break


                    if not already_added:

                        # add points
                        user_ref.update({
                            "total_points": current_points + 50
                        })


                        # wallet history
                        db.collection(
                            "wallet_transactions"
                        ).add({

                            "user_id": user_id,
                            "event_id": event_id,
                            "points": 50,
                            "transaction_type": "Earned",
                            "reason": event_data.get(
                                "event_name",
                                "Event Completed"
                            ),
                            "created_at": firestore.SERVER_TIMESTAMP

                        })


    return redirect(url_for('admin_events'))

@app.route('/api/admin/events/<event_id>/participant/<user_id>/checkin', methods=['POST'])
def api_admin_checkin(event_id, user_id):

    redirect_response = admin_required_redirect()
    if redirect_response:
        return redirect_response


    # participant document
    participant_ref = (
        db.collection("events")
        .document(str(event_id))
        .collection("participants")
        .document(str(user_id))
    )


    participant_doc = participant_ref.get()


    if participant_doc.exists:

        participant_data = participant_doc.to_dict()


        # आधीच checked नसेल तर status update
        if participant_data.get("checkin_status") != "Checked":

            participant_ref.update({
                "checkin_status": "Checked"
            })


    return redirect(url_for('admin_events'))

if __name__ == "__main__":
    import webbrowser
    from threading import Timer

    url = "http://127.0.0.1:5000"

    Timer(1, lambda: webbrowser.open(url)).start()

    app.run(debug=False)
