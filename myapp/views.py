from flask import Blueprint, render_template, request, url_for, redirect, session, flash, jsonify
from myapp.database import db, User, Chat, Message, ChatMessage
from functools import wraps
from datetime import datetime
from myapp import socket

import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

views = Blueprint('views', __name__, static_folder='static', template_folder='templates')


# ------------------ AUTHENTICATION DECORATOR ------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("views.login"))
        return f(*args, **kwargs)
    return decorated


# ------------------ INDEX ------------------
@views.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("views.login"))


# ------------------ REGISTER ------------------
@views.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        username = request.form["username"].strip().lower()
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("User already exists with that username.")
            return redirect(url_for("views.login"))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        new_chat = Chat(user_id=new_user.id, chat_list=[])
        db.session.add(new_chat)
        db.session.commit()

        flash("Registration successful.")
        return redirect(url_for("views.login"))

    return render_template("auth.html")


# ------------------ LOGIN ------------------
@views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user"] = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
            return redirect(url_for("views.chat"))
        else:
            flash("Invalid login credentials. Please try again.")
            return redirect(url_for("views.login"))

    return render_template("auth.html")


# ------------------ NEW CHAT ------------------
@views.route("/new-chat", methods=["POST"])
@login_required
def new_chat():
    user_id = session["user"]["id"]
    new_chat_email = request.form["email"].strip().lower()

    if new_chat_email == session["user"]["email"]:
        return redirect(url_for("views.chat"))

    recipient_user = User.query.filter_by(email=new_chat_email).first()
    if not recipient_user:
        return redirect(url_for("views.chat"))

    existing_chat = Chat.query.filter_by(user_id=user_id).first()

    if recipient_user.id not in [c["user_id"] for c in existing_chat.chat_list]:
        # Create a unique room_id based on user ids (ensure uniqueness)
        room_id = str(min(user_id, recipient_user.id)) + '_' + str(max(user_id, recipient_user.id))

        existing_chat.chat_list.append({"user_id": recipient_user.id, "room_id": room_id})
        existing_chat.save_to_db()

        recipient_chat = Chat.query.filter_by(user_id=recipient_user.id).first()
        if not recipient_chat:
            recipient_chat = Chat(user_id=recipient_user.id, chat_list=[])
            db.session.add(recipient_chat)
            db.session.commit()

        recipient_chat.chat_list.append({"user_id": user_id, "room_id": room_id})
        recipient_chat.save_to_db()

        # Create Message room if doesn't exist
        if not Message.query.filter_by(room_id=room_id).first():
            new_message = Message(room_id=room_id)
            db.session.add(new_message)
            db.session.commit()

    return redirect(url_for("views.chat"))


# ------------------ CHAT ------------------
@views.route("/chat/", methods=["GET", "POST"])
@login_required
def chat():
    room_id = request.args.get("rid", None)
    current_user_id = session["user"]["id"]

    current_user_chats = Chat.query.filter_by(user_id=current_user_id).first()
    chat_list = current_user_chats.chat_list if current_user_chats else []

    data = []
    for chat in chat_list:
        user = User.query.get(chat["user_id"])
        username = user.username if user else "Unknown"
        is_active = room_id == chat["room_id"]
        
        message = Message.query.filter_by(room_id=chat["room_id"]).first()
        last_message = (
            message.messages[-1].content if message and message.messages else "This place is empty."
        )

        data.append({
            "username": username,
            "room_id": chat["room_id"],
            "is_active": is_active,
            "last_message": last_message,
        })

    # Safely get messages for current room
    room_message = Message.query.filter_by(room_id=room_id).first() if room_id else None
    messages = room_message.messages if room_message else []

    return render_template("chat.html",
                           user_data=session["user"],
                           room_id=room_id,
                           data=data,
                           messages=messages)


# ------------------ TIME FILTER ------------------
@views.app_template_filter("ftime")
def ftime(date):
    dt = datetime.fromtimestamp(int(date))
    return dt.strftime("%I:%M %p | %m/%d")


# ------------------ VISUALIZATION (OPTIONAL) ------------------
@views.route('/visualize')
def visualize():
    users = User.query.all()
    if not users:
        flash("No users found.")
        return redirect(url_for("views.chat"))

    dates = [user.date.strftime('%Y-%m-%d') for user in users]
    df = pd.DataFrame(dates, columns=['date'])
    df['date'] = pd.to_datetime(df['date'])
    df['count'] = 1

    daily_counts = df.groupby(df['date'].dt.date).count()

    plt.figure(figsize=(8, 5))
    plt.plot(daily_counts.index, daily_counts['count'], marker='o')
    plt.title("User Registrations Over Time")
    plt.xlabel("Date")
    plt.ylabel("Registrations")
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')

    return render_template("visualize.html", graphic=graphic)


# ------------------ GET USERNAME ------------------
@views.route('/get_name')
def get_name():
    data = {'name': session["user"]["username"] if "user" in session else ''}
    return jsonify(data)


# ------------------ GET MESSAGES ------------------
@views.route('/get_messages')
def get_messages():
    room_id = request.args.get("room_id")
    if not room_id:
        return jsonify({"error": "Room ID not provided"}), 400

    message = Message.query.filter_by(room_id=room_id).first()
    if not message:
        return jsonify({"messages": []})

    messages = [{
        "content": msg.content,
        "timestamp": msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        "sender_id": msg.sender_id,
        "sender_username": msg.sender_username
    } for msg in message.messages]

    return jsonify({"messages": messages})


# ------------------ LOGOUT / LEAVE ------------------
@views.route('/leave')
def leave():
    session.clear()
    return redirect(url_for('views.login'))
