# Online-Poll-System

1. Clone the Repository
git clone https://github.com/your-username/online-poll-system.git
cd online-poll-system
2. Create and Activate a Virtual Environment 
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
3.Install Dependencies
pip install -r requirements.txt
4. Run the Application
python app.py


📦 Dependencies
Flask
Flask-Login
Flask-WTF
Flask-SQLAlchemy
requests
WTForms
Werkzeug


📚 Folder Structure
/templates          → HTML templates
/static/style.css   → Custom styles (supports dark mode)
app.py              → Main Flask app
requirements.txt    → Python dependencies
README.md           → Project documentation

✨ Future Improvements
WebSockets for real-time voting (Flask-SocketIO)
Admin panel for poll moderation
Result charts with Chart.js


