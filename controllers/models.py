from .database import db

class User(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(), nullable=False, unique = True)
    password = db.Column(db.String(), nullable = False)
    fullname = db.Column(db.String(), nullable=False)
    qualification = db.Column(db.String(), nullable=False)
    dob = db.Column(db.Date(),nullable = False)
    type = db.Column(db.String(), default="user")
    score = db.relationship('Score', backref='User')
    userdata = db.relationship('Userdata', backref='User')

class Subject(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    description = db.Column(db.String(), nullable=True)
    chapters = db.relationship('Chapter', backref='subject')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=True)
    quizzes = db.relationship('Quiz', backref='chapter')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False) 
    date = db.Column(db.Date(), nullable=False)
    time = db.Column(db.String(10), nullable=False)  
    questions = db.relationship('Question', backref='quiz')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_id = db.Column(db.String(), nullable=False)
    title = db.Column(db.String(), nullable=False)
    question_statement = db.Column(db.String(), nullable=False)
    option1 = db.Column(db.String(), nullable=False)
    option2 = db.Column(db.String(), nullable=False)
    option3 = db.Column(db.String(), nullable=False)
    option4 = db.Column(db.String(), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer)
    chapter_name = db.Column(db.String())
    noq = db.Column(db.Integer)
    qdate = db.Column(db.Date())
    total_score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time_taken = db.Column(db.String())
    selected_answers = db.Column(db.String())

class Userdata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer)
    chapter_name = db.Column(db.String())
    score_id = db.Column(db.Integer)
    question_id = db.Column(db.Integer)
    title = db.Column(db.String())
    question_statement = db.Column(db.String())
    option1 = db.Column(db.String())
    option2 = db.Column(db.String())
    option3 = db.Column(db.String())
    option4 = db.Column(db.String())
    correct_option = db.Column(db.Integer)
