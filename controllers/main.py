from flask import Flask, render_template, request, redirect, url_for
from flask import current_app as app
from .models import *
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")


        

@app.route('/', methods=['GET','POST'])
def Welcome():
    user = User.query.all()
    if not user:
        dte = datetime.strptime("2005-12-15", "%Y-%m-%d").date()
        u = User(username='admin',password='admin',fullname='admin',qualification='admin',dob=dte,type='admin')
        db.session.add(u)
        db.session.commit()
    past_quiz = Quiz.query.filter(Quiz.date < date.today()).all()
    if past_quiz:
        for i in past_quiz:
            i.status = 'expired'
        db.session.commit()
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
                elif above_user.type == "removed":
                    emsg =  "You have been removed, Contact the Admin if this is a mistake"
                    return redirect(url_for('user_login',emsg=emsg))
                else:
                    return redirect(url_for('user_dashboard', u_name = u_name))
            else:
                emsg = "Incorrect Password!"
                return redirect(url_for('user_login',emsg=emsg))
        else:
            emsg = "User Does not Exist!"
            return redirect(url_for('user_login',emsg=emsg))
    if 'emsg' in request.args:
        emsg = request.args.get('emsg')
        return render_template('login.html',emsg=emsg)
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
            emsg = "User Already Exists :("
            return redirect(url_for('user_register',emsg=emsg))
        else:
            new_user = User(username=u_name,password=pwd,fullname=fn,qualification=qfn,dob=dobcon)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('user_dashboard', u_name = u_name))
    if 'emsg' in request.args:
        emsg = request.args.get('emsg')
        return render_template('register.html',emsg=emsg)
    return render_template('register.html')





@app.route('/view/<int:quiz_id>/<u_name>')
def view_quiz(quiz_id,u_name):
    quiz = Quiz.query.get(quiz_id)
    return render_template('user_viewquiz.html',quiz=quiz,u_name=u_name)

@app.route('/user_dashboard')
def user_dashboard():
    u_name = request.args.get('u_name')
    if 'chapter' in request.args:
        chapter = str(request.args.get('chapter'))
        ids = []
        for obj in chapter:
            ids.append(int(obj))
        quizzes = Quiz.query.filter(Quiz.chapter_id.in_(ids)).all()
        return render_template('user_dashboard.html',quizzes=quizzes,u_name=u_name)
    
    if 'subject' in request.args:
        subject = str(request.args.get('subject'))
        ids = []
        for obj in subject:
            ids.append(int(obj))
        quizzes = Quiz.query.filter(Quiz.chapter.has(Chapter.subject_id.in_(ids))).all()
        return render_template('user_dashboard.html',quizzes=quizzes,u_name=u_name)
    
    if 'quiz_date' in request.args:
        quiz_date = request.args.get('quiz_date')
        dts = quiz_date.split(',')
        quizzes = Quiz.query.filter(Quiz.date.in_(dts)).all()
        return render_template('user_dashboard.html',quizzes=quizzes,u_name=u_name)
    
    if 'msg' in request.args:
        quizzes = Quiz.query.all()
        emsg = request.args.get('msg')
        return render_template('user_dashboard.html',quizzes=quizzes,u_name=u_name,msg=emsg)

    quizzes = Quiz.query.filter(Quiz.date >= date.today(), Quiz.status=='active').all()
    return render_template('user_dashboard.html',quizzes=quizzes,u_name=u_name)

@app.route('/scores/<u_name>')
def scores(u_name):
    dte = date.today()
    if 'chapter' in request.args:
        sw = request.args.get('chapter')
        user = User.query.filter_by(username=u_name).first()
        score = Score.query.filter(Score.user_id==user.id,Score.chapter_name.like(sw)).all()
        return render_template('user_scores.html', u_name=u_name, score=score,dte=dte)
    elif 'quiz_date' in request.args:
        sw = request.args.get('quiz_date')
        user = User.query.filter_by(username=u_name).first()
        score = Score.query.filter(Score.user_id==user.id,Score.qdate.like(sw)).all()
        return render_template('user_scores.html', u_name=u_name, score=score,dte=dte)
    user = User.query.filter_by(username=u_name).first()
    score = Score.query.filter_by(user_id=user.id)
    if 'msg' in request.args:
        msg = request.args.get('msg')
        return render_template('user_scores.html', u_name=u_name, score=score, msg=msg, dte=dte)
    return render_template('user_scores.html', u_name=u_name, score=score, dte=dte)

@app.route('/admin',methods=['GET','POST'])
def admin_dashboard():
    if 'subject' in request.args:
        subject = str(request.args.get('subject'))
        ids = []
        for obj in subject:
            ids.append(int(obj))
        subjects = Subject.query.filter(Subject.id.in_(ids)).all()
        return render_template('admin_dashboard.html',subjects=subjects)
    subjects = Subject.query.all()
    if 'emsg' in request.args:
        emsg = request.args.get('emsg')
        return render_template('admin_dashboard.html',subjects=subjects,emsg=emsg)
    if subjects:
        return render_template('admin_dashboard.html',subjects=subjects)
    else:
        return render_template('admin_dashboard.html',subjects=[])

@app.route('/addsubject')
def addsubject():
    if 'emsg' in request.args:
        msg = request.args.get('emsg')
        return render_template('add_subject.html',msg=msg)
    return render_template('add_subject.html')

@app.route('/addsubject2',methods=['GET','POST'])
def add_subject():
    if request.method == "POST":
        if request.form.get('submit') == "Add":
            name = request.form.get("name")
            desc = request.form.get("dsc")
            sub = Subject.query.filter_by(name=name).first()
            if not name:
                emsg =  "Please give name to the Subject before Adding!"
                return redirect(url_for('addsubject',emsg=emsg))
            if sub:
                emsg = "Subject Already Exists :("
                return redirect(url_for('addsubject',emsg=emsg))
            else:
                subject = Subject(name=name,description=desc)
                db.session.add(subject)
                db.session.commit() 
            subjects = Subject.query.all()
            return render_template('admin_dashboard.html',subjects=subjects)
    return redirect('/admin')

@app.route('/addchapter/<int:subject_id>',methods=['GET'])
def addchapter(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first()
    return render_template('add_chapter.html',subject=subject)

@app.route('/addchapter2/<int:subject_id>',methods=['POST'])
def add_chapter(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first()
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
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    return render_template('edit_chapter.html',chapter=chapter)

@app.route('/editchapter2/<int:chapter_id>',methods=['POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    if request.form.get('submit') == "Cancel":
        return redirect(url_for('admin_dashboard'))
    name = request.form.get('name')
    description = request.form.get('dsc')
    if not name:
        chapter.description = description
    elif not description:
        chapter.name = name
    else:
        chapter.name = name
        chapter.description = description
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/deletechapter/<int:chapter_id>',methods=['GET','POST'])
def deletechapter(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    quiz = Quiz.query.filter_by(chapter_id=chapter_id).all()
    if quiz:
        for i in quiz:
            questions = Question.query.filter_by(quiz_id=i.id)
            if questions:
                for question in questions:
                    db.session.delete(question)
            db.session.delete(i)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/quizmantemp')
def quizmantemp():
    if 'chapter' in request.args:
        chapter = request.args.get('chapter')
        ids = []
        for obj in chapter:
            ids.append(int(obj))
        quizes = Quiz.query.filter(Quiz.chapter_id.in_(ids)).all()
        return render_template('quiz_management.html',quizes=quizes)
    quizes = Quiz.query.filter(Quiz.date >= date.today()).all()
    if 'emsg' in request.args:
        emsg = request.args.get('emsg')
        return render_template('quiz_management.html',quizes=quizes,emsg=emsg)
    if quizes:
        if 'statusmsg' in request.args:
            emsg = request.args.get('statusmsg')
            return render_template('quiz_management.html',quizes=quizes,emsg=emsg)
        return render_template('quiz_management.html',quizes=quizes)
    else:
        return render_template('quiz_management.html',quizes=[])
    
@app.route('/addquiz')
def addquiz():
    if 'emsg' in request.args:
        emsg = request.args.get('emsg')
        return render_template('add_quiz.html',emsg=emsg)
    return render_template('add_quiz.html')
    
@app.route('/quizman',methods=['GET','POST'])
def quizman():
    if request.method == "POST":
        if request.form.get('submit') == "Cancel":
            return redirect(url_for('quizmantemp'))
        chapter_id = request.form.get('chapter_id')        
        dte = request.form.get('date')
        time = request.form.get('time')
        status = request.form.get('status')
        if not dte:
            emsg = "Please specify a date for the quiz!"
            return redirect(url_for('addquiz',emsg=emsg))
        if not time:
            emsg = "Please set a time for the quiz!"
            return redirect(url_for('addquiz',emsg=emsg))
        if not status:
            emsg = "Please set a status for the quiz!"
            return redirect(url_for('addquiz',emsg=emsg))
        datecon = datetime.strptime(dte, '%Y-%m-%d').date()
        timecon = datetime.strptime(time, '%H:%M').time() 
        time_str = timecon.strftime('%H:%M')
        chapter = Chapter.query.get(chapter_id)
        if not chapter_id:
            emsg = "Please give id to the Chapter before Adding!"
            return redirect(url_for('addquiz',emsg=emsg))
        if not chapter:
            emsg = "The specified Chapter ID does not exist!"
            return redirect(url_for('addquiz',emsg=emsg))
        
        if not (datecon >= date.today()):
            emsg = "Please enter a valid date!"
            return redirect(url_for('addquiz',emsg=emsg))
        else:
            quiz2 = Quiz(chapter_id=chapter_id,date=datecon,time=time_str,status=status)
            db.session.add(quiz2)
            db.session.commit() 
            quizes = Quiz.query.all()
            return redirect(url_for('quizmantemp'))
    return redirect(url_for('quizmantemp'))



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
        if not id:
            emsg = "Please enter some ID for the question!"
            return redirect(url_for('add_question',emsg=emsg, quiz_id=quiz_id))
        exists = Question.query.filter_by(quiz_id=quiz_id, question_id=id).first()
        if exists:
            emsg = "A question already exists with this ID!"
            return redirect(url_for('add_question',emsg=emsg, quiz_id=quiz_id))
        if not title or not qst or not o1 or not o2 or not o3 or not o4 or not co:
            emsg = "Please fill all fields"
            return redirect(url_for('add_question',emsg=emsg, quiz_id=quiz_id))
        if o1 in [o2, o3, o4] or o2 in [o3, o4] or o3 == o4:
            emsg = "No 2 or more options can be same"
            return redirect(url_for('add_question',emsg=emsg, quiz_id=quiz_id))
        if int(co) not in [1,2,3,4]:
            emsg = "valid correct options - 1,2,3,4!"
            return redirect(url_for('add_question',emsg=emsg, quiz_id=quiz_id))
        new_question = Question(quiz_id=quiz_id,question_id=id,title=title,question_statement=qst,option1=o1,option2=o2,option3=o3,option4=o4,correct_option=co)
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('quizmantemp'))
    if 'emsg' in request.args:
        emsg = request.args.get('emsg')
        return render_template('add_question.html',emsg=emsg, quiz_id=quiz_id)
    return render_template('add_question.html', quiz_id=quiz_id)

@app.route('/deletequestion/<int:question_id>',methods=['GET','POST'])
def deletequestion(question_id):
    question = Question.query.filter_by(id=question_id).first()
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('quizmantemp'))

@app.route('/deletequiz/<int:quiz_id>',methods=['GET','POST'])
def deletequiz(quiz_id):
    questions = Question.query.filter_by(quiz_id=quiz_id)
    for question in questions:
        db.session.delete(question)
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('quizmantemp'))

@app.route('/editquiz/<int:quiz_id>')
def editquiz(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    if 'msg' in request.args:
        msg = request.args.get('msg')
        return render_template('editquiz.html',quiz=quiz,msg=msg)
    return render_template('editquiz.html',quiz=quiz)

@app.route('/editquiz2/<int:quiz_id>/<int:chapter_id>',methods=['GET','POST'])
def editquiz2(quiz_id,chapter_id):
    if request.form.get('submit') == 'Confirm':
        dte = request.form.get('date')
        time = request.form.get('time')
        status = request.form.get('status')
        datecon=''
        if dte:
            datecon = datetime.strptime(dte, '%Y-%m-%d').date()
        if datecon:
            if not (datecon >= date.today()):
                msg = "Please enter a valid date!"
                return redirect(url_for('editquiz',msg=msg,quiz_id=quiz_id))
        if time:
            timecon = datetime.strptime(time, '%H:%M').time() 
            time_str = timecon.strftime('%H:%M')
        quiz = Quiz.query.filter_by(chapter_id=chapter_id).first()
        if dte:
            quiz.date = datecon
        if time:
            quiz.time = time_str
        if status:
            quiz.status = status
        db.session.commit()
        return redirect(url_for('quizmantemp'))
    return redirect(url_for('quizmantemp'))
    


@app.route('/start_quiz/<int:quiz_id>/<u_name>',methods=['GET','POST'])
def startquiztemp(quiz_id,u_name):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    questions =  Question.query.filter_by(quiz_id=quiz_id).all()
    noofquestions = len(questions)
    start_time = datetime.now()
    time = quiz.time.split(':')

    if 'score' not in request.args:
        score = 0
    else:
        score = int(request.args.get('score'))

    if 'user_select' not in request.args:
        user_select = ''
    else:
        user_select = str(request.args.get('user_select'))

    if 'time_taken' not in request.args:
        time_taken = 0 
    else:
        time_taken = int(request.args.get('time_taken'))

    if 'quiz_timer' not in request.args:
        quiz_timer = int(time[0])*3600 + int(time[1])*60 
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
        time_taken += spent_time
        quiz_timer -= spent_time
    
        if 'answer' in request.form:
            selected_option = int(request.form.get('answer'))
            user_select += str(selected_option)
            ci = questions[current_index]
            co = ci.correct_option
            if selected_option == co:
                score += 1
            else:
                score=score
        else:
            emsg = "Please select an option before going on to the next question."
            return render_template('startquiz.html', quiz=quiz, u_name=u_name, questions=questions, current_index=current_index, emsg=emsg,timer=quiz_timer)
        

        if current_index + 1 < noofquestions:
            return redirect(url_for('startquiztemp', quiz_id=quiz_id, u_name=u_name, q_index=current_index + 1,score=score,quiz_timer=quiz_timer,time_taken=time_taken,user_select=user_select))
        else:
            user = User.query.filter_by(username=u_name).first()
            total_time_taken = str(timedelta(seconds=time_taken))

            scoreex = Score.query.filter_by(user_id=user.id,quiz_id=quiz.id).first()
            if scoreex:
                scoreex.quiz_id = quiz.id
                scoreex.chapter_name = quiz.chapter.name
                scoreex.noq = noofquestions
                scoreex.qdate=quiz.date
                scoreex.total_score=score
                scoreex.user_id=user.id
                scoreex.time_taken=total_time_taken
                scoreex.selected_answers=user_select
                db.session.commit()
            else:
                score2 = Score(quiz_id=quiz_id,chapter_name=quiz.chapter.name,noq=noofquestions,qdate=quiz.date,total_score=score,user_id=user.id,time_taken=total_time_taken,selected_answers=user_select)
                db.session.add(score2)
                db.session.commit()

            score3 = Score.query.filter_by(quiz_id=quiz_id,user_id=user.id).order_by(Score.id.desc()).first()
            ud2 = Userdata.query.filter_by(user_id=user.id,score_id=score3.id,quiz_id=score3.quiz_id).all()
            if ud2:
                for i in ud2:
                    db.session.delete(i)
                db.session.commit()
                for i in questions:
                    userdata = Userdata(user_id=user.id,quiz_id=quiz_id,date=quiz.date,time=quiz.time,chapter_name=quiz.chapter.name,score_id=score3.id,question_id=i.id,title=i.title,question_statement=i.question_statement,option1=i.option1,option2=i.option2,option3=i.option3,option4=i.option4,correct_option=i.correct_option)
                    db.session.add(userdata)
                db.session.commit()               
            else:
                for i in questions:
                    userdata = Userdata(user_id=user.id,quiz_id=quiz_id,date=quiz.date,time=quiz.time,chapter_name=quiz.chapter.name,score_id=score3.id,question_id=i.id,title=i.title,question_statement=i.question_statement,option1=i.option1,option2=i.option2,option3=i.option3,option4=i.option4,correct_option=i.correct_option)
                    db.session.add(userdata)
                db.session.commit()
            score=0
            return redirect(url_for('scores', u_name=u_name,quiz_id=quiz_id,ttt=total_time_taken))

    return render_template('startquiz.html', quiz=quiz, u_name=u_name, questions=questions, current_index=current_index,timer=quiz_timer,start=start_time)



@app.route('/deletesubject/<int:subject_id>',methods=['GET','POST'])
def deletesubject(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id)
    for chapter in chapters:
        quiz = Quiz.query.filter_by(chapter_id=chapter.id).all()
        if quiz:
            for i in quiz:
                questions = Question.query.filter_by(quiz_id=i.id)
                if questions:
                    for q in questions:
                        db.session.delete(q)
                db.session.delete(i)
        db.session.delete(chapter)
    subject = Subject.query.filter_by(id=subject_id).first()
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/editsubject/<int:subject_id>')
def editsubject(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first()
    return render_template('editsubject.html',subject=subject)

@app.route('/editsubject2/<int:subject_id>',methods=['GET','POST'])
def editsubject2(subject_id):
    if request.form.get('submit') == 'Confirm':
        name = request.form.get('name')
        dsc = request.form.get('dsc')
        sub = Subject.query.filter_by(id=subject_id).first()
        if name:
            sub.name = name
        elif dsc:
            sub.description = dsc
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_dashboard'))

@app.route('/editquestion/<int:question_id>/<int:quiz_id>',methods=['GET','POST'])
def editquestion(question_id,quiz_id):
    question = Question.query.filter_by(question_id=question_id,quiz_id=quiz_id).first()
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    if quiz.status == 'active':
        msg = "Questions of an active quiz cannot be edited!"
        return redirect(url_for('quizmantemp',statusmsg=msg))
    if 'emsg' in request.args:
        emsg = request.args.get('emsg')
        return render_template('edit_question.html',question=question, quiz_id=quiz_id,emsg=emsg)
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

    if o1 and o2 and o3 and o4:
        if o1 in [o2, o3, o4] or o2 in [o3, o4] or o3 == o4:
            emsg = "No 2 or more options can be same"
            return redirect(url_for('editquestion',emsg=emsg, quiz_id=quiz_id,question_id=question_id))
        question.option1 = o1
        question.option2 = o2
        question.option3 = o3
        question.option4 = o4
    else:
        if o1 or o2 or o3 or o4:
            emsg = "Please give entries for all options"
            return redirect(url_for('editquestion',emsg=emsg, quiz_id=quiz_id,question_id=question_id))
    if co:
        if int(co) not in [1,2,3,4]:
            emsg = "valid correct options - 1,2,3,4!"
            return redirect(url_for('editquestion',emsg=emsg, quiz_id=quiz_id,question_id=question_id))
    
    if title:
        question.title = title
    if qst:
        question.question_statement = qst
    if co:
        question.correct_option = co

    db.session.commit()
    return redirect(url_for('quizmantemp'))

@app.route('/usersdata')
def users_data():
    if 'sw' in request.args:
        sw = request.args.get('sw')
        users = User.query.filter(User.fullname.like(sw)).all()
        quiz = Quiz.query.all()
        q = len(quiz)
        return render_template('userdata.html',users=users,q=q)
    elif 'emsg' in request.args:
        return render_template('userdata.html',users=[])
    users = User.query.filter_by(type="user").all()
    quiz = Quiz.query.all()
    q = len(quiz)
    return render_template('userdata.html',users=users,q=q)

@app.route('/search/<u_name>')
def usersearch(u_name):
    search_word = request.args.get('search_word')
    sw = "%" + search_word.lower() +"%"

    subject = Subject.query.filter(Subject.name.like(sw)).all()
    if subject:
        st = ''
        for i in subject:
            st += str(i.id)
        return redirect(url_for('user_dashboard',subject=st,u_name=u_name))
    
    chapter = Chapter.query.filter(Chapter.name.like(sw)).all()
    if chapter:
        st = ''
        for i in chapter:
            st += str(i.id)
        return redirect(url_for('user_dashboard',chapter=st,u_name=u_name))
    
    dte = Quiz.query.filter(Quiz.date.like(sw)).all()
    if dte:
        st = ''
        for i in dte:
            st = st + str(i.date) + ','
        return redirect(url_for('user_dashboard',quiz_date=st,u_name=u_name))
    if not chapter and not subject and not dte:
        errormsg = "No information found for: "+search_word
        return redirect(url_for('user_dashboard',msg=errormsg,u_name=u_name))

        

@app.route('/view_answers/<int:quiz_id>/<u_name>/<int:score_id>')
def viewanswers(quiz_id,u_name,score_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    
    userdata = Userdata.query.filter_by(quiz_id=quiz_id,score_id=score_id)
    for i in userdata:
        subquiz_id = i.quiz_id
        chaptername = i.chapter_name
        break

    score = Score.query.filter_by(quiz_id=quiz_id,id=score_id).first()
    L=[]
    for i in score.selected_answers:
        L.append(int(i))
    print(L)
    return render_template('view_answers.html',quiz=quiz,questions=userdata,u_name=u_name,L=L,subquiz_id=subquiz_id,chaptername=chaptername,score=score)

@app.route('/inspect/<int:user_id>')
def inspect(user_id):
    user = User.query.filter_by(id=user_id).first()
    score = Score.query.filter_by(user_id=user_id)
    return render_template('user_more_data.html', user=user, score=score)

@app.route('/view_user_answers/<int:quiz_id>/<fullname>/<int:score_id>')
def viewuseranswers(quiz_id,fullname,score_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    user = User.query.filter_by(fullname = fullname).first()

    questions = Userdata.query.filter_by(quiz_id=quiz_id,score_id=score_id)
    for i in questions:
        subquiz_id = i.quiz_id
        chaptername = i.chapter_name
        break

    score = Score.query.filter_by(quiz_id=quiz_id,id=score_id).first()
    L=[]
    for i in score.selected_answers:
        L.append(int(i))
    return render_template('view_user_answers.html',quiz=quiz,questions=questions,user=user,L=L,subquiz_id=subquiz_id,chaptername=chaptername)

@app.route('/remove/<int:user_id>')
def removeuser(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.type = "removed"
    db.session.commit()
    return redirect(url_for('users_data'))

@app.route('/bin')
def bin():
    if 'sw' in request.args:
        sw = request.args.get('sw')
        user = User.query.filter(User.fullname.like(sw),User.type == 'removed').all()
        return render_template('binusers.html',users=user)
    elif 'emsg' in request.args:
        return render_template('binusers.html',users=[])
    user = User.query.filter_by(type="removed").all()
    return render_template('binusers.html',users=user)

@app.route('/reapprove/<int:user_id>')
def reapprove(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.type = "user"
    db.session.commit()
    return redirect(url_for('bin'))

@app.route('/summary/<u_name>')
def usersummary(u_name):
    user = User.query.filter_by(username=u_name).first()
    scorelist = Score.query.filter_by(user_id=user.id).all()

    if scorelist:
        score = Score.query.filter(Score.user_id==user.id, Score.qdate < date.today()).all()
        if not score:
            message = "Available after deadline passes!"
            return render_template('usersummary.html',msg=message,u_name=u_name)
    if not scorelist:
        message = "Please Attempt some quizzes to get summary!"
        return render_template('usersummary.html',msg=message,u_name=u_name)
        
    attendance = Score.query.filter_by(user_id=user.id).all()
    
    avgtime = []
    name_time = {}
    for i in score:
        obj = datetime.strptime(i.time_taken, "%H:%M:%S")
        sec = obj.hour*3600 + obj.minute*60 + obj.second
        name_time[i.chapter_name] = sec
        avgtime.append(sec)

    avgt = sum(avgtime)/len(avgtime)
    average_time_taken = "0"+str(timedelta(seconds=int(avgt)))

    ch_name = list(name_time.keys())
    tt = list(name_time.values())
    plt.clf()
    plt.plot(ch_name, tt, marker='o', linestyle='-', color='b', label='Line 1')
    plt.xlabel("Chapter Name")
    plt.ylabel("Time Taken(Seconds)")
    plt.title("Time Taken in each Quiz")
    plt.savefig('static/img3.png')
        

    ch_perc = {}
    for i in score:
        ch_perc[i.chapter_name] = (i.total_score/i.noq)*100
        
    chap_name = list(ch_perc.keys())
    percen = list(ch_perc.values())
    plt.clf()
    plt.bar(chap_name, percen)
    plt.ylim(0, 105)
    plt.xlabel("Chapter")
    plt.ylabel("Percentage Scored")
    plt.title("Percentage scored in each Quiz")
    plt.savefig('static/img.png')


    accuracy = 0
    inaccuracy = 0
    for i in score:
        accuracy += i.total_score
        inaccuracy += i.noq-i.total_score
    

    if accuracy == 0:
        values = [inaccuracy]
        lables = ["All Incorrect answers!"]
    elif inaccuracy == 0:
        values = [accuracy]
        lables = ["All Correct answers :)"]
    else:
        values = [accuracy,inaccuracy]
        lables = ["Correct Answers","Incorrect Answers"]
    plt.clf()
    plt.pie(values, autopct='%1.1f%%' ,labels=lables)
    plt.title("Accuracy")
    plt.savefig('static/img2.png')

    return render_template('usersummary.html', u_name=u_name,avgt=average_time_taken,attendance=len(attendance))

@app.route('/challenge/<int:ud_id>/<int:qz_id>/<u_name>/<int:score_id>')
def challenge(ud_id,qz_id,u_name,score_id):
    question = Userdata.query.filter_by(quiz_id=qz_id,id=ud_id).first()
    return render_template('challenge.html',question=question,u_name=u_name,score_id=score_id)

@app.route('/challengeanswer/<int:qz_id>/<int:ud_id>/<u_name>/<int:score_id>/<int:user_id>', methods = ['GET','POST'])
def challengeanswer(qz_id,ud_id,u_name,score_id,user_id):
    if request.form.get('submit') == "Submit":
        eco = request.form.get('uco')
        exp = request.form.get('exp')
        userdata = Userdata.query.filter_by(quiz_id=qz_id,id=ud_id).first()
        challenge = Challenge(userdata_id=userdata.id,user_co=eco,explanation=exp)
        db.session.add(challenge)
        db.session.commit()
        return redirect(url_for('viewanswers',quiz_id=qz_id,u_name=u_name,score_id=score_id))
    return redirect(url_for('viewanswers',quiz_id=qz_id,u_name=u_name,score_id=score_id))

@app.route('/challengeque')
def challengeque():
    challenge = Challenge.query.all()
    return render_template('challengeque.html',challenge=challenge)

@app.route('/viewchallenge/<int:ch_id>')
def vc(ch_id):
    challenge = Challenge.query.filter_by(id=ch_id).first()
    return render_template('viewch.html',ch=challenge)

@app.route('/acceptchallenge/<int:ch_id>')
def ach(ch_id):
    challenge = Challenge.query.filter_by(id=ch_id).first()
    newco = challenge.user_co
    question = Question.query.filter_by(id=challenge.userdata.question_id).first()
    score = Score.query.filter_by(quiz_id=challenge.userdata.quiz_id).all()
    if question:
        question.correct_option = newco
    for s in score:
        ud = Userdata.query.filter_by(score_id=s.id,question_id=challenge.userdata.question_id).all()
        for i in ud:
            i.correct_option = newco
        ques = Userdata.query.filter_by(quiz_id=s.quiz_id,score_id=s.id).all()
        new_mark = 0
        index = 0
        L = []
        for i in s.selected_answers:
            L.append(int(i))
        for j in ques:
            if j.correct_option == L[index]:
                new_mark += 1
            index += 1
        s.total_score = new_mark
    db.session.commit()
    
    return redirect(url_for('rch',ch_id=ch_id))

@app.route('/rejectchallenge/<int:ch_id>')
def rch(ch_id):
    challenge = Challenge.query.filter_by(id=ch_id).first()
    db.session.delete(challenge)
    db.session.commit()
    return redirect(url_for('challengeque'))
    
@app.route('/adminsearch/ad')
def adminsearch():
    searchword = request.args.get('searchword')
    sw = "%" + searchword.lower() +"%"
    subject = Subject.query.filter(Subject.name.like(sw)).all()
    if subject:
        st = ''
        for i in subject:
            st += str(i.id)
        return redirect(url_for('admin_dashboard',subject=st))
    emsg = "No results found for: " +searchword
    return redirect(url_for('admin_dashboard',emsg=emsg))

@app.route('/adminsearch/qm')
def adminsearchqm():
    searchword = request.args.get('search_word')
    sw = "%" + searchword.lower() +"%"
    chapter = Chapter.query.filter(Chapter.name.like(sw)).all()
    if chapter:
        st = ''
        for i in chapter:
            st += str(i.id)
        return redirect(url_for('quizmantemp',chapter=st))
    emsg = "No results found for: " + searchword
    return redirect(url_for('quizmantemp',emsg=emsg))


@app.route('/adminsearch/ud')
def adminsearchud():
    searchword = request.args.get('search_word')
    sw = "%" + searchword.lower() +"%"
    users = User.query.filter(User.fullname.like(sw)).all()
    if users:
        return redirect(url_for('users_data',sw=sw))
    emsg = " "
    return redirect(url_for('users_data',emsg=emsg))

@app.route('/adminsearch/bin')
def adminsearchbin():
    searchword = request.args.get('search_word')
    sw = "%" + searchword.lower() +"%"
    users = User.query.filter(User.fullname.like(sw),User.type == 'removed').all()
    if users:
        return redirect(url_for('bin',sw=sw))
    emsg = " "
    return redirect(url_for('bin',emsg=emsg))



@app.route('/adminsummary')
def adminsummary():
    user = User.query.filter_by(type='user').all()
    aquiz = Quiz.query.filter(Quiz.status == 'active').all()
    iquiz = Quiz.query.filter(Quiz.status == 'inactive').all()
    equiz = Quiz.query.filter(Quiz.status == 'expired').all()
    no_of_quiz = {}
    for i in user:
        score = Score.query.filter_by(user_id=i.id).order_by(Score.id.asc()).group_by(Score.quiz_id).all()
        no_of_quiz[i.fullname] = len(score)
    user_names = list(no_of_quiz.keys())
    total_quiz_attempt = list(no_of_quiz.values())
    plt.clf()
    plt.bar(user_names, total_quiz_attempt)
    plt.xlabel("Users")
    plt.ylabel("No. of quiz attempted")
    plt.title("Attendance of quiz")
    plt.xticks(rotation=5)
    plt.savefig('static/adimg1.png')

    user_ids = []
    for i in user:
        user_ids.append(i.id)
    score = Score.query.filter(Score.user_id.in_(user_ids)).all()
    chapter_time = {}
    for i in score:
        obj = datetime.strptime(i.time_taken, "%H:%M:%S")
        sec = obj.hour*3600 + obj.minute*60 + obj.second
        if i.chapter_name not in chapter_time:
            chapter_time[i.chapter_name] = sec
        else:
            chapter_time[i.chapter_name] += sec
        
    avg_ch_time = {} 
    for i in chapter_time:
        s = Score.query.filter_by(chapter_name=i).all()
        avgt = chapter_time[i]/len(s)
        avg_ch_time[i] = avgt

    ch_name = list(avg_ch_time.keys())
    tt = list(avg_ch_time.values())
    plt.clf()
    plt.plot(ch_name, tt, marker='o', linestyle='-', color='b', label='Line 1')
    plt.xlabel("Chapter Name")
    plt.ylabel("Time Taken(Seconds)")
    plt.title(" Average time taken for each chapter")
    plt.xticks(rotation=5)
    plt.savefig('static/adimg2.png')


    name_perc = {}
    for i in score:
        if i.user.fullname not in name_perc:
            s = Score.query.filter_by(user_id=i.user.id).all()
            marks = 0
            count = 0
            for j in s:
                marks_perc = j.total_score/j.noq
                marks += marks_perc
                count += 1
            perc = (marks/count)*100
            name_perc[i.user.fullname] = perc
        
    u_name = list(name_perc.keys())
    perr = list(name_perc.values())
    plt.clf()
    plt.bar(u_name, perr)
    plt.ylim(0, 105)
    plt.xlabel("User Name")
    plt.ylabel("Percentage")
    plt.title("Average percentage in all quizzes")
    plt.xticks(rotation=5)
    plt.savefig('static/adimg3.png')

    if not score:
        msg = 'no user has attempted any quizzes'
        return render_template('adminsummary.html',msg=msg,users = len(user),aq = len(aquiz),iq = len(iquiz),eq = len(equiz))
    return render_template('adminsummary.html',users = len(user),aq = len(aquiz),iq = len(iquiz),eq = len(equiz))



@app.route('/search/score/<u_name>')
def usersearchscore(u_name):
    search_word = request.args.get('search_word')
    sw = "%" + search_word.lower() +"%"
    user = User.query.filter_by(username=u_name).first()
    score = Score.query.filter(Score.user_id==user.id,Score.chapter_name.like(sw)).all()
    if score:
        return redirect(url_for('scores', chapter=sw, u_name=u_name))

    dte = Score.query.filter(Score.user_id==user.id,Score.qdate.like(sw)).all()
    if dte:
        return redirect(url_for('scores',quiz_date=sw,u_name=u_name))
    if not score and not dte:
        errormsg = "No information found for: "+search_word
        return redirect(url_for('scores',msg=errormsg,u_name=u_name))
    

@app.route('/history')
def history():
    if 'chapter' in request.args:
        chapter = request.args.get('chapter')
        ids = []
        for obj in chapter:
            ids.append(int(obj))
        quizes = Quiz.query.filter(Quiz.chapter_id.in_(ids), Quiz.date < date.today()).all()
        return render_template('quiz_history.html',quizes=quizes)
    quizes = Quiz.query.filter(Quiz.date < date.today()).all()
    if 'emsg' in request.args:
        emsg = request.args.get('emsg')
        return render_template('quiz_history.html',quizes=quizes,emsg=emsg)
    if quizes:
        return render_template('quiz_history.html',quizes=quizes)
    else:
        return render_template('quiz_history.html',quizes=[])
    

@app.route('/adminsearch/hst')
def adminsearchhst():
    searchword = request.args.get('search_word')
    sw = "%" + searchword.lower() +"%"
    chapter = Chapter.query.filter(Chapter.name.like(sw)).all()
    if chapter:
        st = ''
        for i in chapter:
            st += str(i.id)
        return redirect(url_for('history',chapter=st))
    emsg = "No results found for: " + searchword
    return redirect(url_for('history',emsg=emsg))


@app.route('/view_question/<int:q_id>')
def viewques(q_id):
    question = Question.query.filter_by(id=q_id).first()
    return render_template('view_question.html',q = question)

@app.route('/viewpastque/<int:q_id>')
def viewpastque(q_id):
    question = Question.query.filter_by(id=q_id).first()
    return render_template('viewpastque.html',q = question)

@app.route('/user_profile/<u_name>')
def user_profile(u_name):
    user = User.query.filter_by(username=u_name).first()
    return render_template('user_profile.html',user=user,u_name=u_name)