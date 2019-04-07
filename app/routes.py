import os, sys, pickle
from time import time
from threading import Thread
from flask_sqlalchemy import get_debug_queries
from bs4 import BeautifulSoup
from flask import (render_template, flash, url_for, session, redirect, request,
    abort, send_from_directory, jsonify, make_response)
from app import app, db, login, limiter, csrf
from flask_login import login_user, logout_user, current_user, login_required
from app.models import (Post, User, RegistCode, UploadImage, LeaveMessage,
    PostCat, Use_Redis, Stats)
from app.forms import (LoginForm, PostForm, SignUpForm, ChangeForm,
    EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, LeaveMsgForm,
    AddCat, RepCat)
from datetime import datetime, timedelta
from werkzeug.urls import url_parse
from app.email import send_password_reset_email, send_verify_code_email
from flask_ckeditor import upload_success, upload_fail
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.contrib.profiler import ProfilerMiddleware


app.wsgi_app = ProxyFix(app.wsgi_app)
if app.config['PROFILER']:
    if not os.path.exists('profile'):
        os.mkdir('profile')
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir='profile',
        restrictions=[30])
flag = app.config['REDIS_DISABLE']

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@limiter.request_filter
def header_whitelist():
    return request.method == 'GET'


@app.before_request
def before_request():
    if request.endpoint == 'user' and request.referrer.endswith('/login'):
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

@app.after_request
def add_header(response):
    if 'Content-Type' in response.headers and\
          '/css' in response.content_type:
        response.cache_control.max_age = 2592000
    if app.config['DEBUG_QUERY']:
        for l in get_debug_queries():
            print(l)
    return response

@app.route('/')
@app.route('/index')
def index(page=1):
    html = Use_Redis.get('index', str(current_user.get_id() or '0'),
        disable=flag)
    if html:
        return html
    user = User.query.filter_by(role=1,
        username=app.config['DATABASE_ADMIN']).first()
    if user:
        total = Use_Redis.get('total', 'post', disable=flag)
        if not total:
            total = Stats.query.filter_by(name='post_count').first().total
            Use_Redis.set('total', 'post', total, disable=flag)
        total = int(total)
        posts = Post.query.filter_by(user_id=user.id).order_by(
            Post.time.desc()).paginate(
            page, app.config['POST_PER_PAGE'], False, total_in=total)
        news = user.about_me
    else:
        posts = None
        news = 'Testing'
    cats = PostCat.query.all()
    html = render_template('index.html', user=user, posts=posts,
                          cats=cats, page=page, new=news)
    Use_Redis.set('index', str(current_user.get_id() or '0'), html,
            disable=flag)
    return html


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
            if not next_page or url_parse(next_page).netloc != '':
                #flash('remember me? ' + str(request.form.get('remember_me')))
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('用户名或密码错误！')          #Login failed, username or password error!
            return redirect('/login', code=301)
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

#@cache.cached(timeout=120) !pagination conflicts cache
def show(page=None, per_page=None, error_out=True):
    msgs = LeaveMessage.query.order_by(
            LeaveMessage.leave_time).paginate(page, per_page, error_out)
    return msgs


@app.route('/contact', methods=['GET','POST'])
@limiter.limit("80/day;30/hour;10/minute")
def contact(page=1):
    per_page = 15
    page_num = request.args.get('page')
    if page_num:
        if not request.is_xhr:
            abort(404)
        msgs = show(int(page_num), per_page, False)
        if msgs.items:
            next_content = {}
            num = 0
            for n,l in enumerate(msgs.items):
                num += 1
                next_content[n] = {'name':l.name,
                                   'content':l.content,
                                   'leave_time':l.leave_time.isoformat(),
                                   'user_id' :l.user_id,
                                   'role':'站长' if l.user_id == 1\
                                   else '匿名'}
            #when json encode,function sort will go wrong,so i define the order
            next_content[997] = str(per_page) #max_total_number
            next_content[998] = str(num)  #real_total_number
            next_content[999] = str(msgs.prev_num)  
            next_content[1000] = str(msgs.next_num)
        else: next_content = None
        return jsonify(next_content)
    form = LeaveMsgForm()
    if form.validate_on_submit():
        msg = LeaveMessage(name=form.name.data, content=form.content.data,
            email=form.email.data, user_id=
                current_user.get_id())
        try:
            db.session.add(msg)
            db.session.commit()
        except:
            app.logger.error('database error when leaving message!')
        flash('提交成功')
    for error in form.email.errors:
        flash(error)
    msgs = show(page, per_page, False)
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
        Use_Redis.eval('index', '*', disable=flag)
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
    total = Use_Redis.get('total', 'post', disable=flag)
    if not total:
        total = Stats.query.filter_by(name='post_count').first().total
        Use_Redis.set('total', 'post', total, disable=flag)
    total = int(total)
    posts=Post.query.filter_by(user_id=current_user.id).order_by(
        db.desc(Post.time)).paginate(page, 8, False, total_in=total)
    if posts.pages < page and page > 1:
        abort(404)
    return render_template('user.html', user=current_user, posts=posts, page=page)


#can just see the content
@app.route('/<username>/articles/<post_id>')
def article_detail(username, post_id):
    html = Use_Redis.get('article', post_id,
        str(current_user.get_id() or '0'), disable=flag)
    if not html:
        post = Post.query.filter_by(id=post_id).first_or_404()
        html = render_template('detail.html', title=post.title, post=post,
            user=current_user)
        Use_Redis.set('article', post_id,
            str(current_user.get_id() or '0'), html, disable=flag)
    return html


#making
@app.route('/picture')
def picture():
    app.logger.error('error')
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
    Use_Redis.eval('index', '*', disable=flag)
    Use_Redis.eval('article', post_id, '*', disable=flag)
    Use_Redis.eval('cat', '0', '*', disable=flag)
    Use_Redis.eval('cat', str(post.cat_id), '*', disable=flag)
    Use_Redis.delete('total', 'post', disable=flag)
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
    form.cat.data = post.cat_id
    return render_template('editpost.html', form=form, post_id=post.id)


def del_image(post, form, user_id):
    with app.app_context():
        soup_post = BeautifulSoup(post.content, 'lxml')
        soup_form = BeautifulSoup(form.content.data, 'lxml')
        img_post = {img['src'] for img in soup_post.find_all('img')}
        img_form = {img['src'] for img in soup_form.find_all('img')}
        delete_img = img_post - img_form
        if delete_img:
            for img in delete_img:
                if not img.startswith('http'):
                    try:
                        f_path = os.path.join(app.config['UPLOADED_PATH'],
                            str(user_id),
                            os.path.basename(img))
                        os.remove(f_path)
                    except:
                        app.logger.warning('delete error')
        if img_post:
            for img in img_post:
                f_fullname = os.path.basename(img)
                f_path = os.path.join(
                    app.config['UPLOADED_PATH'],
                    str(user_id), f_fullname)
                db_image = UploadImage.query.filter_by(
                    user_id=user_id, image_path=f_path).first()
                if db_image:
                    db_image.mark = 1
            try:
                db.session.commit()
            except:
                app.logger.error("could't mark images")


@app.route('/change/<post_id>', methods=['POST'])
@login_required
def change(post_id):
    form = ChangeForm()
    post = Post.query.filter_by(id=post_id).first_or_404()
    if post.author.username != current_user.username:
        abort(404)
    if form.validate_on_submit():
        t = Thread(target=del_image, args=(post, form, current_user.id))
        t.start()
        temp_store = 0
        if request.form.get('temp'):
            temp_store = 1
        origin_id = str(post.cat_id)
        post.title = form.title.data
        post.content = form.content.data
        post.cat_id = form.cat.data
        post.last_modify = datetime.utcnow()
        post.temp_store = temp_store
        db.session.add(post)
        db.session.commit()
        Use_Redis.eval('article', post_id, '*', disable=flag)
        Use_Redis.eval('index', '*', disable=flag)
        Use_Redis.eval('cat', '0', '*', disable=flag)
        Use_Redis.eval('cat', origin_id, '*', disable=flag)
        Use_Redis.eval('cat', str(form.cat.data), '*', disable=flag)
        flash('你的修改已经保存.')
        return redirect(url_for('user', username=current_user.username)), 301
    else:
        flash('修改异常！')
        app.logger.error(form.errors)
    return redirect(url_for('editpost', form=form, post_id=post.id)), 301


@app.route('/write',methods=['GET','POST'])
@login_required
def write():
    form = PostForm()
    if form.validate_on_submit() and request.method == 'POST':
        temp_store = 0
        if request.form.get('temp'):
            temp_store = 1
        post = Post(title=form.title.data, content=form.content.data,
            user_id=current_user.id, cat_id=form.cat.data,
            temp_store=temp_store)
        db.session.add(post)
        db.session.commit()
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
        Use_Redis.eval('index', '*', disable=flag)
        Use_Redis.eval('cat', str(form.cat.data), '*', disable=flag)
        Use_Redis.eval('cat', '0', '*', disable=flag)
        Use_Redis.eval('srh', '*', disable=flag)
        Use_Redis.delete('total', 'post', disable=flag)
        flash('提交成功!')
        if current_user.id == 1:
            return redirect(url_for('user', username=current_user.username)), 301
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
def uploaded_files(filename):
    image = UploadImage.query.filter_by(
        image_name=filename).first_or_404()
    dirname = os.path.dirname(image.image_path)
    
    return send_from_directory(dirname, filename)


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    f = request.files.get('upload')
    basename, *extension = f.filename.split('.')       #prevent danger.jpg.exe,etc
    if extension[-1].lower() not in ['jpg', 'gif', 'png', 'jpeg']\
            and len(extension) == 1:
        return upload_fail(message='Image only!')
    #image_name' length
    f_fullname = basename[:10] + '_' + str(int(time()*100)) + '.' + extension[0]
    f_dirname = os.path.join(app.config['UPLOADED_PATH'], str(current_user.id))
    if not os.path.exists(f_dirname):
        os.makedirs(f_dirname)
    elif not os.access(f_dirname, os.W_OK):
        app.logger.error(' '.join(f_dirname, 'Non-writable!'))
        return upload_fail(message='Write error')   
    f_path = os.path.join(app.config['UPLOADED_PATH'], str(current_user.id),
        f_fullname)
    f.save(f_path)
    image = UploadImage(
        image_path=f_path,
        image_name=f_fullname,
        user_id=current_user.id)
    try:
        db.session.add(image)
        db.session.commit()
    except:
        app.logger.error('database error')
        return upload_fail(message='Database error!')
    url = url_for('uploaded_files', filename=f_fullname)
    return upload_success(url=url)


@app.route('/control')
@login_required
def control():
    cat = AddCat()
    rep = RepCat()
    cats = PostCat.query.order_by('name').all()
    return render_template('control.html', cat=cat, cats=cats, rep=rep)


@app.route('/category/add', methods=['POST'])
@login_required
def add_cat():
    cat = AddCat()
    if cat.validate_on_submit():
        query_cat = PostCat.query.filter_by(name=cat.name.data).first()
        if not query_cat:
            new_cat = PostCat(name=cat.name.data)
            try:
                db.session.add(new_cat)
                db.session.commit()
                flash('类别增加成功')
                Use_Redis.eval('index', '*', disable=flag)
            except:
                app.logger.error('database errror when add new cat')
        else:
            flash('类别已存在!')
    return redirect('control'), 301


@app.route('/category/replace', methods=['POST'])
@login_required
def rep_cat():
    origin_id = request.form.get('origin_id')
    if not origin_id:
        return redirect('control'), 301
    form = RepCat()
    if form.validate_on_submit():
        cat = PostCat.query.filter_by(id=int(origin_id)).first_or_404()
        cat.name = form.name.data
        try:
            db.session.commit()
            flash('ok')
            Use_Redis.eval('index', '*', disable=flag)
            Use_Redis.eval('total', 'post', disable=flag)
            Use_Redis.eval('cat', origin_id, '*', disable=flag)
        except:
            flash('DB error!')
            return redirect('control'), 301
    for error in form.name.errors:
        flash(error)
    return redirect('control'), 301


@app.route('/category/del', methods=['POST'])
@login_required
def del_cat():
    cat_id = request.form['cat']
    if cat_id:
        cat = PostCat.query.filter_by(id=cat_id).first()
        if cat:
            try:
                db.session.delete(cat)
                db.session.commit()
                flash('成功删除')
                Use_Redis.eval('index', '*', disable=flag)
                Use_Redis.eval('cat', str(cat_id), '*', disable=flag)
            except:
                app.logger.warning("can't delete {0}".format(cat.name))
    return redirect('control'), 301


@app.route('/category')
def choose_cate():
    if not request.is_xhr:
        abort(404)
    cat_id = request.args.get('cat_id','0')
    page = request.args.get('page','1')
    if len(cat_id) > 9 or len(page) > 9:
        abort(404)
    if int(cat_id) < 0 or int(page) < 1:
        abort(404)
    xml = Use_Redis.get('cat', cat_id, page, disable=flag)
    if xml:
        xml = pickle.loads(xml)
        return xml
    if int(cat_id) == 0:
        total = Use_Redis.get('total', 'post', disable=flag)
        if not total:
            total = Stats.query.filter_by(name='post_count').first().total
            Use_Redis.set('total', 'post', total, disable=flag)
        total = int(total)
        #user_id = 1 is admin'id
        posts = Post.query.filter_by(user_id=1).order_by(db.desc(Post.time)).paginate(
            int(page), app.config['POST_PER_PAGE'], False, total_in=total)
        xml = make_response(render_template('category.xml', posts=posts))
        xml.headers['Content-Type'] = 'application/xml; charset=utf-8'
        Use_Redis.set('cat', cat_id, page, pickle.dumps(xml), disable=flag)
    else:
        #user_id=1 is admin's id
        posts = Post.query.filter_by(
            cat_id=int(cat_id), user_id=1).order_by(
            Post.time.desc()).paginate(
            int(page), app.config['POST_PER_PAGE'], False)
        xml = make_response(render_template('category.xml', posts=posts))
        xml.headers['Content-Type'] = 'application/xml; charset=utf-8'
        Use_Redis.set('cat', cat_id, page, pickle.dumps(xml), disable=flag)
    return xml


@app.route('/search')
def search():
    keys = request.args.get('s')
    if keys:
        html = Use_Redis.get('srh', keys, str(current_user.get_id() or '0'),
            disable=flag)
    else:
        html = None
    if not html:
        results = Post.query.whoosh_search(keys).all()
        html = render_template('search.html', results=results)
        Use_Redis.set('srh', keys, str(current_user.get_id() or '0'),
            html, disable=flag)
    return html


#error pages
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
