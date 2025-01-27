from flask import Flask, render_template, request, redirect, url_for
from flask import current_app as app
from .models import *
from datetime import datetime, timedelta

@app.route('/', methods=['GET','POST'])
def Welcome():
    return render_template('welcome.html')



@app.route('/userlogin', methods=['GET','POST'])
def user_login():
    if request.method == "POST":
        u_name = request.form.get("u_name")
        pwd = request.form.get("pwd")
        above_user = User.query.filter_by(username=u_name).first()
        if above_user:
            if above_user.password == pwd:
                if above_user.type == "admin":
                    return redirect('/admin')
                else:
                    return redirect(url_for('user_dashboard', u_name = u_name))
            else:
                return "Incorrect Password!"
        else:
            return "User Does not Exist!"
    return render_template('login.html')


@app.route('/register', methods=['GET','POST'])
def user_register():
    if request.method == "POST":
        u_name = request.form.get("username")
        pwd = request.form.get("pwd")
        fn = request.form.get("fullname")
        qfn = request.form.get("qualification")
        dob = request.form.get("dob")
        dobcon = datetime.strptime(dob, '%Y-%m-%d').date()
        above_user = User.query.filter_by(username=u_name).first()
        if above_user:
            return "User Already Exists :("
        else:
            new_user = User(username=u_name,password=pwd,fullname=fn,qualification=qfn,dob=dobcon)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('user_dashboard', u_name = u_name))

    return render_template('register.html')





@app.route('/view/<int:quiz_id>/<u_name>')
def view_quiz(quiz_id,u_name):
    quiz = Quiz.query.get(quiz_id)
    return render_template('user_viewquiz.html',quiz=quiz,u_name=u_name)

@app.route('/user_dashboard')
def user_dashboard():
    u_name = request.args.get('u_name')
    quizzes = Quiz.query.all()
    return render_template('user_dashboard.html',quizzes=quizzes,u_name=u_name)

@app.route('/scores/<u_name>')
def scores(u_name):
    user = User.query.filter_by(username=u_name).first()
    score = Score.query.filter_by(user_id=user.id)
    return render_template('user_scores.html', u_name=u_name, score=score)


@app.route('/admin',methods=['GET','POST'])
def admin_dashboard():
    subjects = Subject.query.all()
    if subjects:
        return render_template('admin_dashboard.html',subjects=subjects)
    else:
        return render_template('admin_dashboard.html',subjects=[])

@app.route('/addsubject')
def addsubject():
    return render_template('add_subject.html')

@app.route('/addsubject2',methods=['GET','POST'])
def add_subject():
    if request.method == "POST":
        if request.form.get('submit') == "Cancel":
            subjects = Subject.query.all()
            if subjects:
                return render_template('admin_dashboard.html',subjects=subjects)
            else:
                return render_template('admin_dashboard.html',subjects=[])
        elif request.form.get('submit') == "Add":
            name = request.form.get("name")
            desc = request.form.get("dsc")
            sub = Subject.query.filter_by(name=name).first()
            if not name:
                return "Please give name to the Subject before Adding!"
            if sub:
                return "Subject Already Exists :("
            else:
                subject = Subject(name=name,description=desc)
                db.session.add(subject)
                db.session.commit() 
            subjects = Subject.query.all()
            return render_template('admin_dashboard.html',subjects=subjects)
    return redirect('/admin')

@app.route('/addchapter/<int:subject_id>',methods=['GET'])
def addchapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('add_chapter.html',subject=subject)

@app.route('/addchapter2/<int:subject_id>',methods=['POST'])
def add_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.form.get('submit') == "Cancel":
        return redirect(url_for('admin_dashboard'))
    name = request.form.get('name')
    description = request.form.get('dsc')
    new_chapter = Chapter(name=name,description=description,subject_id=subject.id)
    db.session.add(new_chapter)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/editchapter/<int:chapter_id>',methods=['GET','POST'])
def editchapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('edit_chapter.html',chapter=chapter)

@app.route('/editchapter2/<int:chapter_id>',methods=['POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.form.get('submit') == "Cancel":
        return redirect(url_for('admin_dashboard'))
    name = request.form.get('name')
    description = request.form.get('description')
    chapter.name = name
    chapter.description = description
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/deletechapter/<int:chapter_id>',methods=['GET','POST'])
def deletechapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quiz = Quiz.query.filter_by(chapter_id=chapter_id).first()
    questions = Question.query.filter_by(quiz_id=quiz.id)
    for question in questions:
        db.session.delete(question)
    db.session.delete(quiz)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/addquiz')
def addquiz():
    return render_template('add_quiz.html')

@app.route('/quizmantemp')
def quizmantemp():
    quizes = Quiz.query.all()
    if quizes:
        return render_template('quiz_management.html',quizes=quizes)
    else:
        return render_template('quiz_management.html',quizes=[])
    
@app.route('/quizman',methods=['GET','POST'])
def quizman():
    if request.method == "POST":
        if request.form.get('submit') == "Cancel":
            return redirect(url_for('quizmantemp'))
        chapter_id = request.form.get('chapter_id')        
        date = request.form.get('date')
        time = request.form.get('time')
        if not date:
            return "Please specify a date for the quiz!"
        if not time:
            return "Please set a time for the quiz!"
        datecon = datetime.strptime(date, '%Y-%m-%d').date()
        timecon = datetime.strptime(time, '%H:%M:%S').time() 
        time_str = timecon.strftime('%H:%M:%S')
        quiz = Quiz.query.filter_by(chapter_id=chapter_id).first()
        chapter = Chapter.query.get(chapter_id)
        if not chapter_id:
            return "Please give id to the Chapter before Adding!"
        if  quiz:
            return "Chapter Already Exists :("
        if not chapter:
            return "The specified Chapter ID does not exist!"
        else:
            quiz2 = Quiz(chapter_id=chapter_id,date=datecon,time=time_str)
            db.session.add(quiz2)
            db.session.commit() 
            quizes = Quiz.query.all()
            return render_template('quiz_management.html',quizes=quizes)
    return redirect('quiz_management.html')



@app.route('/addquestion/<int:quiz_id>',methods=['GET','POST'])
def add_question(quiz_id):
    if request.method == 'POST':
        if request.form.get('submit') == "Cancel":
            return redirect(url_for('quizmantemp'))
        id = request.form.get('id')
        title = request.form.get('title')
        qst = request.form.get('qst')
        o1 = request.form.get('o1')
        o2 = request.form.get('o2')
        o3 = request.form.get('o3')
        o4 = request.form.get('o4')
        co = request.form.get('co')
        if o1 in [o2, o3, o4] or o2 in [o3, o4] or o3 == o4:
            return "No 2 or more options can be same"
        exists = Question.query.filter_by(quiz_id=quiz_id, question_id=id).first()
        if not id:
            return "Please enter some ID for the question!"
        if exists:
            return "A question already exists with this ID!"
        new_question = Question(quiz_id=quiz_id,question_id=id,title=title,question_statement=qst,option1=o1,option2=o2,option3=o3,option4=o4,correct_option=co)
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('quizmantemp'))

    return render_template('add_question.html', quiz_id=quiz_id)

@app.route('/deletequestion/<int:question_id>',methods=['GET','POST'])
def deletequestion(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('quizmantemp'))

@app.route('/deletequiz/<int:quiz_id>',methods=['GET','POST'])
def deletequiz(quiz_id):
    questions = Question.query.filter_by(quiz_id=quiz_id)
    for question in questions:
        db.session.delete(question)
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('quizmantemp'))


@app.route('/start_quiz/<int:quiz_id>/<u_name>',methods=['GET','POST'])
def startquiztemp(quiz_id,u_name):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    questions =  Question.query.filter_by(quiz_id=quiz_id).all()
    noofquestions = len(questions)
    score = int(request.args.get('score', 0))
    start_time = datetime.now()
    time = quiz.time.split(':')

    if 'quiz_timer' not in request.args:
        quiz_timer = int(time[0])*3600 + int(time[1])*60 + int(time[2])
    else:
        quiz_timer = int(request.args.get('quiz_timer'))

    if 'q_index' not in request.args:
        current_index = 0  
    else:
        current_index = int(request.args.get('q_index'))

    
    if request.method == 'POST':
        st = request.form.get('st')
        start_time = datetime.fromisoformat(st)
        current_time = datetime.now()
        spent_time = int((current_time - start_time).total_seconds())
        quiz_timer -= spent_time
    
        selected_option = int(request.form.get('answer',0))
        ci = questions[current_index]
        co = ci.correct_option
        if selected_option == co:
            score += 1
        else:
            score=score
        if not selected_option:
            e = "Please select an option before going on to the next question."
            return render_template('startquiz.html', quiz=quiz, u_name=u_name, questions=questions, current_index=current_index, e=e,timer=quiz_timer)

        if current_index + 1 < noofquestions:
            return redirect(url_for('startquiztemp', quiz_id=quiz_id, u_name=u_name, q_index=current_index + 1,score=score,quiz_timer=quiz_timer))
        else:
            user = User.query.filter_by(username=u_name).first()
            score2 = Score(quiz_id=quiz_id,chapter_name=quiz.chapter.name,noq=noofquestions,qdate=quiz.date,total_score=score,user_id=user.id)
            db.session.add(score2)
            db.session.commit()
            score=0
            return redirect(url_for('scores', u_name=u_name))

    return render_template('startquiz.html', quiz=quiz, u_name=u_name, questions=questions, current_index=current_index,timer=quiz_timer,start=start_time)



@app.route('/deletesubject/<int:subject_id>',methods=['GET','POST'])
def deletesubject(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id)
    for chapter in chapters:
        quiz = Quiz.query.filter_by(chapter_id=chapter.id).first()
        questions = Question.query.filter_by(quiz_id=quiz.id)
        for q in questions:
            db.session.delete(q)
        db.session.delete(quiz)
        db.session.delete(chapter)
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/editquestion/<int:question_id>/<int:quiz_id>',methods=['GET','POST'])
def editquestion(question_id,quiz_id):
    question = Question.query.filter_by(question_id=question_id,quiz_id=quiz_id).first()
    return render_template('edit_question.html',question=question, quiz_id=quiz_id)


@app.route('/editquestion2/<int:question_id>/<int:quiz_id>',methods=['POST'])
def edit_question(question_id,quiz_id):
    question = Question.query.filter_by(question_id=question_id,quiz_id=quiz_id).first()
    if request.form.get('submit') == "Cancel":
        return redirect(url_for('quizmantemp'))
    title = request.form.get('title')
    qst = request.form.get('qst')
    o1 = request.form.get('o1')
    o2 = request.form.get('o2')
    o3 = request.form.get('o3')
    o4 = request.form.get('o4')
    co = request.form.get('co')
    if any([o1,o2,o3,o4]) == any([o1,o2,o3,o4]):
        return "No 2 or more options can be same"

    question.title = title
    question.question_statement = qst
    question.option1 = o1
    question.option2 = o2
    question.option3 = o3
    question.option4 = o4
    question.correct_option = co
    db.session.commit()
    return redirect(url_for('quizmantemp'))

@app.route('/usersdata')
def users_data():
    users = User.query.filter_by(type="user").all()
    quiz = Quiz.query.all()
    q = len(quiz)
    return render_template('userdata.html',users=users,q=q)

@app.route('/search/<u_name>')
def search(u_name):
    search_word = request.args.get('search_word')
    sw = "%" + search_word.lower() +"%"
    chapter = Chapter.query.filter(Chapter.name.like(sw)).all()
    return render_template('after_search.html',chapter = chapter, sw=search_word,u_name=u_name)