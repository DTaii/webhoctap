from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password', 
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Register')

class ContributionForm(FlaskForm):
    subject = SelectField(
        'Subject',
        choices=[
            ('Math', 'Mathematics'),
            ('Literature', 'Literature'),
            ('Physics', 'Physics'),
            ('Chemistry', 'Chemistry'),
            ('Biology', 'Biology'),
            ('History', 'History'),
            ('Geography', 'Geography')
        ],
        validators=[DataRequired()]
    )
    grade = SelectField(
        'Grade',
        choices=[(10, 'Grade 10'), (11, 'Grade 11'), (12, 'Grade 12')],
        coerce=int,
        validators=[DataRequired()]
    )
    question = TextAreaField('Question', validators=[DataRequired()])
    option_a = StringField('Option A', validators=[DataRequired()])
    option_b = StringField('Option B', validators=[DataRequired()])
    option_c = StringField('Option C', validators=[DataRequired()])
    option_d = StringField('Option D', validators=[DataRequired()])
    correct_answer = SelectField(
        'Correct Answer',
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        validators=[DataRequired()]
    )
    explanation = TextAreaField('Explanation', validators=[DataRequired()])
    submit = SubmitField('Submit Question')

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_time = DateTimeField('Start Time', validators=[DataRequired()])
    end_time = DateTimeField('End Time', validators=[DataRequired()])
    max_participants = IntegerField('Maximum Participants', validators=[Optional()])
    subject = SelectField(
        'Subject',
        choices=[
            ('Math', 'Mathematics'),
            ('Literature', 'Literature'),
            ('Physics', 'Physics'),
            ('Chemistry', 'Chemistry'),
            ('Biology', 'Biology'),
            ('History', 'History'),
            ('Geography', 'Geography')
        ],
        validators=[DataRequired()]
    )
    difficulty = SelectField(
        'Difficulty',
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard')
        ],
        validators=[DataRequired()]
    )
    prize_pool = IntegerField('Prize Pool (Coins)', validators=[DataRequired()])
    submit = SubmitField('Create Event')