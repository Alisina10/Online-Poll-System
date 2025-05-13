from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import requests  # Keep this at the top with other imports
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash


# Initialize app and extensions
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///polls.db')


db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ---------------- Models ---------------- #

# Model to store user info
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Model for poll questions and options
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=True)
    option4 = db.Column(db.String(100), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

# Model for storing user votes
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    selected_option = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- Forms ---------------- #

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class PollForm(FlaskForm):
    question = StringField("Question", validators=[InputRequired()])
    option1 = StringField("Option 1", validators=[InputRequired()])
    option2 = StringField("Option 2", validators=[InputRequired()])
    option3 = StringField("Option 3 (optional)")
    option4 = StringField("Option 4 (optional)")
    submit = SubmitField("Create Poll")

# ---------------- Routes ---------------- #

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check for existing username
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('Username already exists!', 'warning')
            return redirect(url_for('register'))

        # Check for existing email
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        # Create new user
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid username or password.", "danger")
    return render_template('login.html', form=form)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_polls = Poll.query.filter_by(created_by=current_user.id).all()

    # Fetch a fun number fact
    try:
        response = requests.get("http://numbersapi.com/random/trivia")
        number_fact = response.text
    except:
        number_fact = "Could not fetch a number fact right now."

    return render_template('dashboard.html', name=current_user.username, polls=user_polls, number_fact=number_fact)

@app.route('/create_poll', methods=['GET', 'POST'])
@login_required
def create_poll():
    form = PollForm()
    if form.validate_on_submit():
        poll = Poll(
            question=form.question.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            created_by=current_user.id
        )
        db.session.add(poll)
        db.session.commit()
        flash('Poll created!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_poll.html', form=form)

@app.route('/edit_poll/<int:poll_id>', methods=['GET', 'POST'])
@login_required
def edit_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)

    if poll.created_by != current_user.id:
        flash("You are not authorized to edit this poll.", "danger")
        return redirect(url_for('dashboard'))

    form = PollForm(obj=poll)
    if form.validate_on_submit():
        poll.question = form.question.data
        poll.option1 = form.option1.data
        poll.option2 = form.option2.data
        poll.option3 = form.option3.data
        poll.option4 = form.option4.data
        db.session.commit()
        flash("Poll updated!", "success")
        return redirect(url_for('dashboard'))

    return render_template('create_poll.html', form=form, edit=True)

@app.route('/delete_poll/<int:poll_id>')
@login_required
def delete_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)

    if poll.created_by != current_user.id:
        flash("You are not authorized to delete this poll.", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(poll)
    db.session.commit()
    flash("Poll deleted.", "info")
    return redirect(url_for('dashboard'))

# ---------------- Voting Routes ---------------- #

@app.route('/polls')
@login_required
def polls():
    all_polls = Poll.query.all()
    return render_template('polls.html', polls=all_polls)
@app.route('/vote/<int:poll_id>', methods=['GET', 'POST'])
@login_required
def vote(poll_id):
    poll = Poll.query.get_or_404(poll_id)

    # Only consider real (non-empty) votes
    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        poll_id=poll_id
    ).filter(Vote.selected_option.isnot(None)).first()

    if existing_vote:
        flash("You already voted on this poll.", "info")
        return redirect(url_for('results', poll_id=poll_id))

    if request.method == 'POST':
        selected = request.form.get('option')
        if selected:
            vote = Vote(user_id=current_user.id, poll_id=poll.id, selected_option=selected)
            db.session.add(vote)
            db.session.commit()
            flash("Vote submitted!", "success")
            return redirect(url_for('results', poll_id=poll.id))
        else:
            flash("Please select an option.", "warning")

    return render_template('vote.html', poll=poll)


@app.route('/results/<int:poll_id>')
@login_required
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    votes = Vote.query.filter_by(poll_id=poll_id).all()

    counts = {
        poll.option1: 0,
        poll.option2: 0,
        poll.option3: 0,
        poll.option4: 0
    }

    for vote in votes:
        if vote.selected_option in counts:
            counts[vote.selected_option] += 1

    total_votes = sum(counts.values())

    percentages = {}
    for option, count in counts.items():
        if option:
            percentages[option] = round((count / total_votes) * 100) if total_votes > 0 else 0

    return render_template('results.html', poll=poll, percentages=percentages, total_votes=total_votes)

@app.route('/api/results/<int:poll_id>')
@login_required
def api_results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    votes = Vote.query.filter_by(poll_id=poll_id).all()

    counts = {
        poll.option1: 0,
        poll.option2: 0,
        poll.option3: 0,
        poll.option4: 0
    }

    for vote in votes:
        if vote.selected_option in counts:
            counts[vote.selected_option] += 1

    total_votes = sum(counts.values())

    return jsonify({
        'counts': counts,
        'total_votes': total_votes
    })


# ---------------- Run App ---------------- #

if __name__ == '__main__':
    app.run(debug=True)
