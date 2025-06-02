from myapp import create_app
from myapp.database import db, Message, ChatMessage
from flask_socketio import emit, join_room, leave_room

app, socket = create_app()


# COMMUNICATION ARCHITECTURE

# Join-chat event. Emit online message to other users and join the room
@socket.on("join-chat")
def join_private_chat(data):
    room = data["rid"]
    join_room(room)
    socket.emit(
        "joined-chat",
        {"msg": f"{room} is now online."},
        room=room,
        # include_self=False,  # Uncomment if you want to exclude sender
    )


# Outgoing message event handler
@socket.on("outgoing")
def chatting_event(json, methods=["GET", "POST"]):
    """
    Handles saving messages and sending messages to all clients in the room.
    """
    room_id = json.get("rid")
    timestamp = json.get("timestamp")
    message = json.get("message")
    sender_id = json.get("sender_id")
    sender_username = json.get("sender_username")

    if not all([room_id, timestamp, message, sender_id, sender_username]):
        # Missing data; you can handle this more gracefully
        print("Missing fields in incoming message")
        return

    # Get the message entry for the chat room, or create if not exists
    message_entry = Message.query.filter_by(room_id=room_id).first()
    if not message_entry:
        message_entry = Message(room_id=room_id)
        db.session.add(message_entry)
        db.session.commit()

    # Create new ChatMessage object
    chat_message = ChatMessage(
        content=message,
        timestamp=timestamp,
        sender_id=sender_id,
        sender_username=sender_username,
        room_id=room_id,
    )

    # Add new message to the conversation
    message_entry.messages.append(chat_message)

    # Save changes to the database
    try:
        db.session.add(chat_message)
        db.session.commit()
    except Exception as e:
        print(f"Error saving message to the database: {str(e)}")
        db.session.rollback()
        return

    # Emit the message to all clients in the room except the sender
    socket.emit(
        "message",
        json,
        room=room_id,
        include_self=False,
    )


if __name__ == "__main__":
    socket.run(app, allow_unsafe_werkzeug=True, debug=True)
