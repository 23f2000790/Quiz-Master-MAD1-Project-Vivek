from .database import db

#class Admin(db.Model):
 #   __tablename__ = 'admin'
  #  id = db.Column(db.Integer, primary_key=True)
   # username = db.Column(db.String(100), nullable=False, unique=True,)
    #password = db.Column(db.String(100), nullable=False)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(), nullable=False, unique = True)
    password = db.Column(db.String(), nullable = False)
    fullname = db.Column(db.String(), nullable=False)
    qualification = db.Column(db.String(), nullable=False)
    dob = db.Column(db.Date(),nullable = False)
    type = db.Column(db.String(), default="user")
    scores = db.relationship('Score', backref='user')

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    description = db.Column(db.String(), nullable=True)
    chapters = db.relationship('Chapter', backref='subject')

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=True)
    quizzes = db.relationship('Quiz', backref='chapter')

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False) 
    date = db.Column(db.Date(), nullable=False)
    time = db.Column(db.String(10), nullable=False)  
    remarks = db.Column(db.String(), nullable=True)
    questions = db.relationship('Question', backref='quiz')
    scores = db.relationship('Score', backref='quiz')

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_id = db.Column(db.String(), nullable=False, unique=True)
    title = db.Column(db.String(), nullable=False)
    question_statement = db.Column(db.String(), nullable=False)
    option1 = db.Column(db.String(), nullable=False)
    option2 = db.Column(db.String(), nullable=False)
    option3 = db.Column(db.String(), nullable=False)
    option4 = db.Column(db.String(), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_score = db.Column(db.Integer, nullable=False)