# 🗳️ Online Poll System

A web-based polling app built with Flask that allows registered users to create polls, vote, and view results in real time.

---

## 🚀 Features

- User registration & login (Flask-Login)
- Create, edit, and delete polls (CRUD)
- Vote with protection from multiple voting
- Live vote result updates with JavaScript fetch API
- Light/Dark mode toggle
- Random number trivia using Numbers API

---

## 📦 Tech Stack

- Python (Flask, Flask-Login, Flask-WTF, Flask-SQLAlchemy)
- HTML + Jinja2
- CSS
- JavaScript (fetch for live updates)
- SQLite
- NumbersAPI (external integration)



---

## 🛠️ Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/online-poll-system.git
   cd online-poll-system
   
2- Create a Virtual Environment
-
- python3 -m venv venv
- source venv/bin/activate    # On Windows: venv\Scripts\activate

2- Install Dependencies
-
- pip install -r requirements.txt

3- Run the Application
- python app.py

🔌 Dependencies
-
- Flask
- Flask-Login
- Flask-WTF
- Flask-SQLAlchemy
- requests
- WTForms
- Werkzeug

✨ Future Improvements
- 
- Real-time voting updates via WebSockets (Flask-SocketIO)
- Admin dashboard for managing users and polls
- Poll result charts with Chart.js


