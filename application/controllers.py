from flask import Flask, render_template, request, redirect, url_for
from flask import current_app as app
from .models import *


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
                    return render_template('user_dashboard.html', u_name = u_name)
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
        above_user = User.query.filter_by(username=u_name).first()
        if above_user:
            return "User Already Exists :("
        else:
            new_user = User(username=u_name,password=pwd,fullname=fn,qualification=qfn,dob=dob)
            db.session.add(new_user)
            db.session.commit()
            return render_template('user_dashboard.html', u_name = u_name)

    return render_template('register.html')







@app.route('/view')
def view_quiz():
    return render_template('user_viewquiz.html')

@app.route('/user_dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/user_scores')
def user_scores():
    return render_template('user_scores.html')

@app.route('/admin',methods=['GET','POST'])
def admin_dashboard():
    subjects = Subject.query.all()
    if subjects:
        sub = [subj.name for subj in subjects]
    else:
        sub = []
    return render_template('admin_dashboard.html',sub=sub)

@app.route('/admin/addsubject')
def addsubject():
    return render_template('add_subject.html')

@app.route('/admin/addsubject2',methods=['GET','POST'])
def add_subject():
    if request.method == "POST":
        if request.form.get('submit') == "Cancel":
            subjects = Subject.query.all()
            if subjects:
                sub = [subj.name for subj in subjects]
            else:
                sub = []
            return render_template('admin_dashboard.html', sub=sub)
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
            sub = [subj.name for subj in subjects]
            return render_template('admin_dashboard.html',sub=sub)
    return redirect('/admin')



