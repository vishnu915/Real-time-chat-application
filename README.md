# Chat Web Application

iChat is a real-time web chat application built with Flask and Socket.IO. It provides a seamless and interactive platform for users to communicate with each other through individual chat rooms.

## Project Structure

```
Chat_Web_App/
    myapp/
        static/
            images/
            auth.css
            chat.css
            index.js
            styles.css
        templates/
            auth.html
            base.html
            chat.html
            visualize.html
        __init__.py
        config.py
        database.py
        views.py
    .gitignore
    gunicorn_config.py
    screenshots/
    README.md
    requirements.txt
    server.py
```

## Getting Started

To run the iChat web application locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/Chat_Web_App.git
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up the environment variables:

   - Create a `.env` file in the project root.
   - Add the following lines to the `.env` file:

     ```env
     SECRET_KEY=your_secret_key_here
     DATABASE_URL=sqlite:///database.db
     runt this quries
     CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    chat_list JSON NOT NULL DEFAULT (JSON_ARRAY()),
    FOREIGN KEY (user_id) REFERENCES user(id)
        ON DELETE CASCADE
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE chat_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content VARCHAR(400) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sender_id INT NOT NULL,
    sender_username VARCHAR(50) NOT NULL,
    room_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (room_id) REFERENCES messages(room_id)
        ON DELETE CASCADE
);

     ```

4. Run the server:

   ```bash
   python server.py
   ```
   or 
   ```bash
   gunicorn -c gunicorn_config.py server:app
   ```


Visit `http://localhost:5000` in your web browser to access iChat.

## Features

- **User Authentication:** Secure user registration and login with password hashing.
- **Real-time Chat:** Instant messaging in individual chat rooms.
- **Dynamic Chat List:** Automatically updates the chat list with new messages.
- **Responsive Design:** Works seamlessly on desktop and mobile devices.
- **Visualize User Registration Trends** Visualize the user registration data using Pandas and Matplotlib. This feature aims to analyze the number of users registered on the app over time and present the findings in a graphical format.

## Project Architecture

### `__init__.py`

Initialization of the Flask application, configuration, and extension setup.

### `config.py`

Configuration settings for the Flask application, including the secret key and database URI.

### `database.py`

Database models and schema definition using SQLAlchemy. Includes user, chat, and message models.

### `views.py`

Blueprint for route views, including login, registration, chat, and visualization routes.

### `gunicorn_config.py`

Gunicorn's configuration file for deployment settings.

### `server.py`

Entry point for running the server. Initializes the Flask application and Socket.IO communication events.

## ⛏️ Built With <a name = "tech_stack"></a>

<img alt="Flask" src="https://img.shields.io/badge/flask-%23000.svg?&style=for-the-badge&logo=flask&logoColor=white"/><img alt="HTML5" src="https://img.shields.io/badge/html5-%23E34F26.svg?&style=for-the-badge&logo=html5&logoColor=white"/><img alt="CSS3" src="https://img.shields.io/badge/css3-%231572B6.svg?&style=for-the-badge&logo=css3&logoColor=white"/><img alt="JavaScript" src="https://img.shields.io/badge/javascript-%23323330.svg?&style=for-the-badge&logo=javascript&logoColor=%23F7DF1E"/><img alt="Bootstrap" src="https://img.shields.io/badge/bootstrap-%23563D7C.svg?&style=for-the-badge&logo=bootstrap&logoColor=white"/><img alt="FlaskSqlalchemy" src ="https://img.shields.io/badge/FlaskSQLalchemy-%2307405e.svg?&style=for-the-badge&logo=sqlite&logoColor=white"/>
# Real-time-chat-application
