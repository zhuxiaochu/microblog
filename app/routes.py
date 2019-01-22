from app import app
from flask import (render_template,flash,url_for,session,redirect,request,g,abort,
					make_response)
from app import app, db, login
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Post,User
from app.forms import LoginForm,EditForm,PostForm,SignUpForm,ChangeForm
from datetime import datetime,timedelta


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.login_check(request.form.get('username'))
        if user and user.check_password(request.form.get('password')):
            if request.form.get('remember_me') == 'y':
                login_user(user,remember=True,duration=timedelta(seconds=600))
            else:
                login_user(user)
            user.last_seen = datetime.now()
			
            next = request.args.get('next')
            if next:
               return abort(400)
			
            try:
                db.session.add(user)
                db.session.commit()
            except:
                flash("服务存在异常！请稍后再试。")                      #"The Database error!"  没必要告诉用户太明确的错误原因
                return redirect('/login')
            flash('Your name: ' + request.form.get('username'))
            flash('remember me? ' + str(request.form.get('remember_me')))
            return redirect(url_for("index"))
        else:
            flash('用户名或密码错误！')          #Login failed, username or password error!
            return redirect('/login')
    return render_template('login.html',form=form)