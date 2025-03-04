import os
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Login manager configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import User, Question, Quiz, UserProgress, Event
from forms import LoginForm, RegistrationForm, ContributionForm, AdminLoginForm, EventForm

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Existing routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('homepage'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.username.data == "admin" and form.password.data == "admin123":
            user = User.query.filter_by(username="admin").first()
            if not user:
                user = User(
                    username="admin",
                    email="admin@example.com",
                    password_hash=generate_password_hash("admin123"),
                    is_admin=True
                )
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin/login.html', form=form)

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    pending_questions = Question.query.filter_by(approved=False).count()
    approved_questions = Question.query.filter_by(approved=True).count()

    # Get statistics for different periods
    today = datetime.utcnow().date()
    new_users_today = User.query.filter(db.func.date(User.created_at) == today).count()

    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         pending_questions=pending_questions,
                         approved_questions=approved_questions,
                         new_users_today=new_users_today)

@app.route('/admin/questions')
@login_required
@admin_required
def admin_questions():
    pending_questions = Question.query.filter_by(approved=False).all()
    return render_template('admin/questions.html', questions=pending_questions)

@app.route('/admin/questions/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_question(id):
    question = Question.query.get_or_404(id)
    question.approved = True
    contributor = User.query.get(question.contributor_id)
    contributor.coins += 20  # Reward for approved question
    db.session.commit()
    flash('Question approved and contributor rewarded')
    return redirect(url_for('admin_questions'))

@app.route('/admin/questions/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    flash('Question rejected')
    return redirect(url_for('admin_questions'))

@app.route('/admin/events', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_events():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            max_participants=form.max_participants.data,
            subject=form.subject.data,
            difficulty=form.difficulty.data,
            prize_pool=form.prize_pool.data,
            created_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully')
        return redirect(url_for('admin_events'))

    events = Event.query.all()
    return render_template('admin/events.html', form=form, events=events)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered')
            return render_template('register.html', form=form)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            coins=0
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/homepage')
@login_required
def homepage():
    top_users = User.query.order_by(User.coins.desc()).limit(10).all()
    return render_template('homepage.html', top_users=top_users)

@app.route('/mainquiz')
@login_required
def mainquiz():
    subjects = ['Math', 'Literature', 'Physics', 'Chemistry', 'Biology', 'History', 'Geography']
    return render_template('mainquiz.html', subjects=subjects)

@app.route('/contribute', methods=['GET', 'POST'])
@login_required
def contribute():
    form = ContributionForm()
    if form.validate_on_submit():
        question = Question(
            subject=form.subject.data,
            grade=form.grade.data,
            question_text=form.question.data,
            option_a=form.option_a.data,
            option_b=form.option_b.data,
            option_c=form.option_c.data,
            option_d=form.option_d.data,
            correct_answer=form.correct_answer.data,
            explanation=form.explanation.data,
            contributor_id=current_user.id,
            approved=False
        )
        db.session.add(question)
        db.session.commit()
        flash('Question submitted for review')
        return redirect(url_for('contribute'))
    return render_template('contribute.html', form=form)

@app.route('/shop')
@login_required
def shop():
    return render_template('shop.html')

@app.route('/event')
@login_required
def event():
    return render_template('event.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)