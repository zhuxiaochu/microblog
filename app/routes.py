from app import app
from flask import (render_template,flash,url_for,session,redirect,request,g,abort,
					make_response)
from app import app, db, login
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Post, User, RegistCode
from app.forms import LoginForm, EditForm, PostForm, SignUpForm, ChangeForm, EditProfileForm
from datetime import datetime,timedelta
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.login_check(form.username.data)
        if user and user.check_password(form.password.data):
            if request.form.get('remember_me') == 'y':
                login_user(user,remember=True,duration=timedelta(seconds=600))
            else:
                login_user(user)
            user.last_seen = datetime.now()
			
            next_page = request.args.get('next')
            print(next_page)
            try:
                db.session.add(user)
                db.session.commit()
            except:
                flash("服务存在异常！请稍后再试。")                      #"The Database error!"  没必要告诉用户太明确的错误原因
                return redirect('/login')
            if not next_page or url_parse(next_page).netloc != '':
                #flash('remember me? ' + str(request.form.get('remember_me')))
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('用户名或密码错误！')          #Login failed, username or password error!
            return redirect('/login')
    return render_template('login.html', form=form, title='登录')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        try:
            db.session.commit()
        except:
            flash('服务存在异常！请稍后再试。')
        flash('修改成功。')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='修改信息', form=form)


#exists race condition problem
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            code = RegistCode.query.filter_by(email=form.email.data).first()
            if code is not None:
                db.session.delete(code)
            db.session.commit()
        except:
            flash("服务存在异常！请稍后再试。")                      #"The Database error!"  没必要告诉用户太明确的错误原因
            return redirect('/signup')
        flash('注册成功')
        return redirect(url_for('login'))
    #if form.username.data is not None:
        #flash('错误')
    return render_template('signup.html', form=form, title='注册')


@app.route('/user/<username>')
@login_required
def user(username):
    if username is None:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(user_id = current_user.id).order_by(db.desc(Post.time)).paginate(1,3, False)
    return render_template('user.html', user=user, posts=posts, timedelta=timedelta(hours=8))  #utc+08:00


@app.route('/picture')
def picture():
    return 'making'


@app.route('/delete/<post_id>',methods = ['POST'])
@login_required
def delete(post_id):
    post = Post.query.filter_by(id = post_id).first()
    db.session.delete(post)
    db.session.commit()
    flash("delete post successful!")
    return redirect(url_for('user',username=current_user.username))


@app.route('/edit/<post_id>',methods = ['GET'])
@login_required
def editpost(post_id):
    form = ChangeForm()
    post = Post.query.filter_by(id = post_id).first()
    form.title.data = post.title
    form.content.data = post.content
    return render_template('change.html',form = form,post_id=post.id)


@app.route('/write',methods=['GET','POST'])
@login_required
def write():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content = form.content.data,user_id = current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('user',username=current_user.username))
    return render_template('write.html',title='写作ing',form=form)



@app.route('/verify',methods=['POST'])
def verify():
    input_email = request.form['email']
    registcode = RegistCode.query.filter_by(email=input_email).first()
    if registcode is not None:
        registcode.generate_code()
    else:
        registcode = RegistCode()
        registcode.email = input_email
        registcode.generate_code()
    try:
        db.session.add(registcode)
        db.session.commit()
    except:
        print('no')
        flash("服务存在异常！请稍后再试。")                      #"The Database error!"  没必要告诉用户太明确的错误原因
    return redirect('/signup')





#error pages
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404