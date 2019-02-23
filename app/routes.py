import os
from time import time
from bs4 import BeautifulSoup
from flask import (render_template, flash, url_for, session, redirect, request,
    abort, send_from_directory)
from app import app, db, login, limiter, csrf
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Post, User, RegistCode, UploadImage, LeaveMessage
from app.forms import (LoginForm, PostForm, SignUpForm, ChangeForm,
    EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, LeaveMsgForm)
from datetime import datetime,timedelta
from werkzeug.urls import url_parse
from app.email import send_password_reset_email, send_verify_code_email
from flask_ckeditor import upload_success, upload_fail
from werkzeug.contrib.fixers import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@limiter.request_filter
def header_whitelist():
    return request.method == 'POST'


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    user = User.query.filter_by(role=1,
        username=app.config['DATABASE_ADMIN']).first()
    if user:
        posts = user.posts.order_by(db.desc(Post.time)).paginate(page, 10, False)
        if posts.pages < page and page > 1:
            abort(404)
    else:
        posts = None
    return render_template('index.html', user=user, posts=posts)


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
            #user.last_seen = datetime.utcnow()
			
            next_page = request.args.get('next')
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


@app.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and not app.config['NO_EMAIL']:
            try:
                send_password_reset_email(user)
                flash('重置链接已发送，请检查你的邮箱。')
                return redirect(url_for('login'))
            except:
                flash('服务存在异常，请稍后再试。')
                return redirect(url_for('reset_password_request'))
        flash('不存在此用户','no_user')
    return render_template('reset_password_request.html', form=form,
         title='重置密码')


@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('密码修改成功。')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/contact', methods=['GET','POST'])
@limiter.limit("80/day;30/hour;10/minute")
def contact(page=1):
    form = LeaveMsgForm()
    if form.validate_on_submit():
        msg = LeaveMessage(name=form.name.data, content=form.content.data,
            email=form.email.data, user_id=
                current_user.id if current_user.is_authenticated else None)
        try:
            db.session.add(msg)
            db.session.commit()
        except:
            app.logger.error('database error!')
        flash('提交成功')
    msgs = LeaveMessage.query.order_by(LeaveMessage.leave_time).paginate(page,
        20, False)
    return render_template('contact.html', form=form, msgs=msgs)


@app.route('/contact/delete/<msg_id>')
@login_required
def delete_msg(msg_id):
    msg = LeaveMessage.query.filter_by(id=msg_id).first_or_404()
    try:
        db.session.delete(msg)
        db.session.commit()
    except:
        app.logger.error('database error')
    return redirect(url_for('contact'))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        try:
            db.session.commit()
        except:
            flash('服务存在异常！请稍后再试。')
            return redirect(url_for('edit_profile'))
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
            db.session.commit()
        except:
            flash("服务存在异常！请稍后再试。")                      #"The Database error!"  没必要告诉用户太明确的错误原因
            return redirect('/signup')
        flash('注册成功')
        return redirect(url_for('login'))
    #if form.username.data is not None:
        #flash('错误')
    return render_template('signup.html', form=form, title='注册')

#manage all the content
@app.route('/user/<username>')
@app.route('/user/<username>/<int:page>')
@login_required
def user(username, page=1):
    if username is None:
        return redirect(url_for('login'))
    if username != current_user.username:
        abort(404)
    posts=Post.query.filter_by(user_id=current_user.id).order_by(
        db.desc(Post.time)).paginate(page, 8, False)
    if posts.pages < page and page > 1:
        abort(404)
    return render_template('user.html', user=current_user, posts=posts, page=page)


#can just see the content
@app.route('/<username>/articles/<post_id>')
def article_detail(username, post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    return render_template('detail.html', title='全文内容', post=post)


#making
@app.route('/picture')
def picture():
    abort(404)


@app.route('/delete/<post_id>', methods = ['POST'])
@login_required
def delete(post_id):
    post = Post.query.filter_by(id = post_id).first_or_404()
    if post.author.username != current_user.username:
        abort(404)
    db.session.delete(post)
    db.session.commit()
    flash("删除成功!")
    return redirect(url_for('user',username=current_user.username))


@app.route('/editpost/<post_id>', methods=['GET'])
@login_required
def editpost(post_id):
    form = ChangeForm()
    post = Post.query.filter_by(id=post_id).first_or_404()
    if post.author.username != current_user.username:
        abort(404)
    form.title.data = post.title
    form.content.data = post.content
    return render_template('editpost.html', form=form, post_id=post.id)


@app.route('/change/<post_id>', methods=['POST'])
@login_required
def change(post_id):
    form = ChangeForm()
    post = Post.query.filter_by(id=post_id).first_or_404()
    if post.author.username != current_user.username:
        abort(404)
    if form.validate_on_submit():
        soup_post = BeautifulSoup(post.content, 'lxml')
        soup_form = BeautifulSoup(form.content.data, 'lxml')
        img_post = {img['src'] for img in soup_post.find_all('img')}
        img_form = {img['src'] for img in soup_form.find_all('img')}
        delete_img = img_post - img_form
        if delete_img:
            for img in delete_img:
                try:
                    f_path = os.path.join(app.config['UPLOADED_PATH'],
                        current_user.id,
                        os.path.basename(img))
                    os.remove(f_path)
                    db_image = UploadImage.query.filter_by(
                        user_id=current_user.id,
                        image_path=f_path).first()
                except:
                    flash('异常')
        if img_post:
            for img in img_post:
                f_fullname = os.path.basename(img)
                f_path = os.path.join(
                    app.config['UPLOADED_PATH'],
                    str(current_user.id),
                    f_fullname)
                db_image = UploadImage.query.filter_by(
                    user_id=current_user.id,
                    image_path=f_path).first()
                if db_image:
                    db_image.mark = 1
            try:
                db.session.commit()
            except:
                flash('服务异常')
                return redirect(url_for('editpost', form=form, post_id=post.id))
        post.title = form.title.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash('你的修改已经保存.')
        return redirect(url_for('user', username=current_user.username))
    flash('修改异常！')
    return redirect(url_for('editpost', form=form, post_id=post.id))


@app.route('/write',methods=['GET','POST'])
@login_required
def write():
    form = PostForm()
    if form.validate_on_submit() and request.method == 'POST':
        post = Post(title=form.title.data, content=form.content.data,
            user_id = current_user.id)
        db.session.add(post)
        soup_post = BeautifulSoup(post.content, 'lxml')
        img_set = {img['src'] for img in soup_post.find_all('img')}
        if img_set:
            for img in img_set:
                f_fullname = os.path.basename(img)
                f_path = os.path.join(
                    app.config['UPLOADED_PATH'],
                    str(current_user.id),
                    f_fullname)
                db_image = UploadImage.query.filter_by(
                    user_id=current_user.id,
                    image_path=f_path).first()
                if db_image:
                    db_image.mark = 1
            try:
                db.session.commit()
            except:
                flash('服务异常')
                return render_template('write.html', title='写作ing',form=form)
        flash('提交成功!')
        return redirect(url_for('user', username=current_user.username))
    return render_template('write.html', title='写作ing',form=form)


#send verification code
@app.route('/verify',methods=['POST'])
@limiter.limit("100/day;60/hour;10/minute")
def verify():
    receive_email = request.form['email']
    registcode = RegistCode.query.filter_by(email=receive_email).first_or_404()
    if registcode:
        registcode.generate_code()
    else:
        registcode = RegistCode()
        registcode.email = receive_email
        registcode.generate_code()
    try:
        db.session.add(registcode)
        db.session.commit()
        if not app.config['NO_EMAIL']:
            send_verify_code_email(receive_email, registcode.verify_code)
    except:
        flash("服务存在异常！请稍后再试。")   #"The Database error!"
    return redirect('/signup')


@app.route('/files/<filename>')
@login_required
def uploaded_files(filename):
    dirname = os.path.join(app.config['UPLOADED_PATH'], str(current_user.id))
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except:
            error = 'ERROR_CREATE_DIR'
    elif not os.access(dirname, os.W_OK):
        error = 'ERROR_DIR_NOT_WRITEABLE'
    #raise custom error
    return send_from_directory(dirname, filename)


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    f = request.files.get('upload')
    basename, *extension = f.filename.split('.')       #prevent danger.jpg.exe,etc
    if extension[-1].lower() not in ['jpg', 'gif', 'png', 'jpeg']\
            and len(extension) == 1:
        return upload_fail(message='Image only!')
    f_fullname = basename[:10] + '_' + str(int(time()*100)) + '.' + extension[0]
    if not os.path.exists(os.path.join(app.config['UPLOADED_PATH'],
            str(current_user.id))):
        os.mkdir(os.path.join(app.config['UPLOADED_PATH'],
            str(current_user.id)))
    f_path = os.path.join(app.config['UPLOADED_PATH'], str(current_user.id),
        f_fullname)
    f.save(f_path)
    image = UploadImage(image_path=f_path, user_id=current_user.id)
    db.session.add(image)
    db.session.commit()
    print('database error')
    url = url_for('uploaded_files', filename=f_fullname)
    return upload_success(url=url)


#error pages
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
