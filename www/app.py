from flask import Flask, render_template, request, jsonify, redirect, session, make_response, request, flash, url_for, abort, send_file
from common.database import Database
from models.user import User
from models.admin import Admin
from models.posts import Post
from models.assignments import Assignment
from models.change_cell import send_cell_email
from models.resources import Other, Video, Book
import datetime
from models.forgot import send
from werkzeug.utils import secure_filename
import os
from random import randint
import uuid
from json import dumps
from flask_moment import Moment


app = Flask(__name__)#main
moment = Moment(app)
app.secret_key = "new"
UPLOAD_FOLDER = './temp/'
ADMIN_UPLOAD_FOLDER = './temp/images/'
ALLOWED_EXTENSIONS = {'txt', 'c', 'pdf', 'docx', 'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ADMIN_UPLOAD_FOLDER'] = ADMIN_UPLOAD_FOLDER
app.url_map.strict_slashes = False


@app.before_first_request
def initialize():
	Database.initialize()
	if request.cookies.get('login') is not None:
		session['email'] = request.cookies.get('login')
	else:
		session['email'] = None




@app.route('/posts/<string:post_id>')
def render_posts(post_id):
	post = Post.get_by_id(post_id)
	return render_template("post.html", post=post, acc=session['email'])


@app.route('/assignment/<string:assignment_id>')
def render_assignments(assignment_id):
	assignment = Assignment.get_by_id(assignment_id)
	return render_template("assignment.html", assignment=assignment, acc=session['email'])


@app.route('/re')
def render_re():
	return render_template("login_failed.html")


@app.route('/hub_content', methods=['GET', 'POST'])
def send_content():
	return render_template("signup_failed.html")


@app.route('/admin/hub/<string:uri>')
def render_admin_hub(uri):
	if session['email'] is None:
		return redirect("https://kcbootcampers-api-heroku.herokuapp.com/login")
	cookie_uri = request.cookies.get('login_id')
	if cookie_uri == uri:
		users = Admin.get_all()
		posts = Post.get_all()
		posts.reverse()
		assignments = Assignment.get_all()
		assignments.reverse()
		others = Other.get_all()
		others.reverse()
		videos = Video.get_all()
		videos.reverse()
		books = Book.get_all()
		books.reverse()
		return render_template("admin_hub.html",
												href="https://kcbootcampers-api-heroku.herokuapp.com/admin/hub/"+cookie_uri,
												acc=session['email'], 
												posts=posts,
												users=users,
												assignments=assignments,
												others=others,
												videos=videos,
												books=books,
												uri=uri,
												display='all')
	else:
		return render_template("expired.html", acc="Account" if session['email'] is None else session['email'])



@app.route('/hub')
def render_hub(uri=None):
	if session['email'] is None:
		return redirect("https://kcbootcampers-api-heroku.herokuapp.com/login")
	posts = Post.get_all()
	posts.reverse()
	others = Other.get_all()
	others.reverse()
	books = Book.get_all()
	books.reverse()
	videos = Video.get_all()
	videos.reverse()
	assignments = Assignment.get_all()
	assignments.reverse()
	user = User.get_by_email(session['email'])
	password = "*"*randint(5, 12)
	cellphone = user.cellphone
	fname = user.fname
	lname = user.lname
	if user.status == "*":
		display = "all"
	else:
		display = "none"
	return render_template("hub.html", 
											acc=session['email'], 
											posts=posts, 
											others=others,
											videos=videos,
											books=books,
											assignments=assignments, 
											fname=fname,
											lname=lname,
											password=password,
											cellphone=cellphone,
											display=display)



@app.route('/', methods=['GET', 'POST'])
def comp_sci_rend():
	display = "none"
	try:
		if session['email'] is not None:
			acc = session['email']
			user = User.get_by_email(session['email'])
			if user.status == "*":
				display = "all"
		else:
			acc = "Account"
	except KeyError:
		acc = "Account"
	return render_template("comp_sci_home.html", acc=acc, display=display)


@app.route('/login', methods=['GET', 'POST'])
def login_template():
	if request.method == 'GET':
		return render_template("log_in.html", acc="Account", display="none")
	else:
		email = request.form['email-zone']
		password = request.form['password-zone']
		remember = request.form['remember']
		if User.login_valid(email, password):
			user = User.get_by_email(email)
			uri = uuid.uuid4().hex
			if user.status == "*":
				if Admin.login_valid(email, password):
					resp = make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/admin/hub/" + uri))
					resp.set_cookie('login_id', uri, expires=datetime.datetime.now() + datetime.timedelta(days=1))
					return resp
				else:
					return render_template("log_in.html", acc="Account", display="block")
			elif remember == "on":
				resp = make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/hub"))
				resp.set_cookie('login', email, expires=datetime.datetime.now() + datetime.timedelta(days=365))
				return resp
			else:
				resp = make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/hub"))
				resp.set_cookie('login', "", expires=0)
				return resp
		else:
			user = User.get_by_email(email)
			if user is not None:
				if not user.active:
					return render_template("login_failed.html", acc="Account")
			return render_template("log_in.html", acc="Account", display="block")


@app.route('/register', methods=['GET', 'POST'])
def register_template():
	if request.method == 'GET':
		return render_template("sign_up.html", acc="Account", display="none")
	else:
		first_name = request.form['fname-zone']
		last_name = request.form['lname-zone']
		email = request.form['email-zone']
		password = request.form['password-zone']
		cellphone = request.form['cell-zone']
		remember = request.form['remember']
		if User.register(first_name, last_name, email, password, cellphone):
			if remember == "on":
				resp = make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/hub"))
				resp.set_cookie('login', email, expires=datetime.datetime.now() + datetime.timedelta(days=365))
				return resp
			else:
				resp = make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/hub"))
				resp.set_cookie('login', "", expires=0)
				return resp
		else:
			return render_template("sign_up.html", acc="Account", display="block")



@app.route('/logout')
def user_logout():
	User.logout()
	resp = make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com"))
	resp.set_cookie('login',"", expires=0)
	resp.set_cookie('login_id', "", expires=0)
	return resp


def allowed_file(filename):
	return '.' in filename and \
				 filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/modal_upload', methods=['GET', 'POST'])
def modal_upload_file():
	if request.method == 'POST':
		#check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		#if user does not select file, browser also
		#submit an empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			try:
				assignment = request.cookies.get('assignment')
				try:
					os.mkdir(app.config['UPLOAD_FOLDER'] + assignment + "/")
				except FileExistsError:
					pass
				os.mkdir(app.config['UPLOAD_FOLDER'] + assignment + "/" + session['email'] + "/")
			except FileExistsError:
				pass
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], assignment +"/" + session['email']+"/", filename))
			resp = make_response(render_template("modal_upload.html", fate="File Sent!"))
			return resp
		else:
			return render_template("modal_upload.html", fate="File Extension Not Allowed!")
	else:
		try:
			if session['email'] is None:
				return make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/login"))
			else:
				return render_template("modal_upload.html")
		except KeyError:
			return make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/login"))


@app.route('/uploads', defaults={'req_path': ''}, methods=['GET', 'POST'])
@app.route('/uploads/<path:req_path>', methods=['GET', 'POST'])
def dir_listing(req_path):
    BASE_DIR = './temp/'

    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
    	resp = make_response(send_file(abs_path))
    	resp.headers['Content-Type'] = 'image/' + req_path.rsplit('.')[-1]
    	return resp

    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('files.html', files=files)


@app.route('/compiler')
def render_compiler():
	try:
		if session['email'] is None:
			return make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/login"))
		else:
			resp = make_response(render_template("c_compiler.html", acc=session['email']))
			resp.headers["X-Frame-Options"] = "allow-from https://kcbootcampers-api-heroku.herokuapp.com/compiler"
			return resp
	except KeyError:
		return make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/login"))



@app.route('/change_password', methods=['GET', 'POST'])
def render_sender():
	if session['email'] is None:
		acc = "Account"
		value = ""
	else:
		acc = session['email']
		value = acc
	return render_template("change.html", acc=acc, value=value)


@app.route('/change_password/email_sent', methods=['POST'])
def catch_email():
	email = request.form['email']
	session['email'] = email
	return send(email)


@app.route('/change_password/auth/send', methods=['POST'])
def catch_password():
	email = request.cookies.get('email')
	password = request.form['password']
	user = User.get_by_email(email)
	if User.change_password(email, password):
		user.activate()
		User.login_valid(email, password)
		Database.update(collection="users", query={"email": email}, new_val={"$set": {"temp_password": ""}})
		resp = make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/hub"))
		resp.set_cookie('email',"", expires=0)
		return resp
	else:
		resp = make_response(render_template("login_failed.html", acc="Account"))
		resp.set_cookie('email',"", expires=0)
		return resp


@app.route('/change_password/auth/<string:uri>')
def forgot_pw(uri):
	email = request.cookies.get('email')
	try:
		if session['email'] is not None:
			acc = session['email']
		else:
			acc = "Account"
	except KeyError:
		acc = "Account"

	if User.temp_login_valid(email, uri):
		session['email'] = None
		return render_template("change_pw.html", acc="Account", email=email)
	else:
		return render_template("expired.html", acc=acc)



@app.route('/change_password/auth/<string:uri>/rectify')
def rectify(uri):
	email = request.cookies.get('email')
	try:
		if session['email'] is not None:
			acc = session['email']
		else:
			acc = "Account"
	except KeyError:
		acc = "Account"
		
	if User.temp_login_valid(email, uri):
		user = User.get_by_email(email)
		User.rectify(email)
		session['email'] = email
		resp = make_response(redirect('https://kcbootcampers-api-heroku.herokuapp.com/hub'))
		resp.set_cookie('email',"", expires=0)
		return resp
	else:
		return render_template("expired.html", acc=acc)


@app.route('/change_cell')
def send_change_email():
	return send_cell_email(session['email'])


@app.route('/change_cell/auth/<string:uri>', methods=['GET', 'POST'])
def change_cell(uri):
	try:
		if session['email'] is not None:
			acc = session['email']
		else:
			acc = "Account"
	except KeyError:
		acc = "Account"

	if request.method == 'GET':
		return render_template('change_cell.html')
	else:
		cellphone = request.form['cellphone']
		email = request.cookies.get('email')
		user = User.get_by_email(email)
		if user is not None:
			user.change_cell(cellphone)
			resp = make_response(redirect("https://kcbootcampers-api-heroku.herokuapp.com/hub"))
			resp.set_cookie('email', "", expires=0)
			return resp
		else:
			return render_template("expired.html", acc=acc)


@app.route('/Activate/<string:user_id>')
def activate_acc(user_id):
	user = User.get_by_id(user_id)
	user.activate()
	return "True"


@app.route('/Deactivate/<string:user_id>')
def deactivate_acc(user_id):
	user = User.get_by_id(user_id)
	user.deactivate()
	return "True"


@app.route('/activate_all')
def activate_all():
	Admin.activate_all()
	return "True"


@app.route('/deactivate_all')
def deactivate_all():
	Admin.deactivate_all()
	return "True"


@app.route('/admin/posts/remove/<string:post_id>')
def remove_post(post_id):
	Post.remove_fr_mongo(post_id)
	Assignment.remove_fr_mongo(post_id)
	return "True"


@app.route('/admin/assignments/remove/<string:assignment_id>')
def remove_assignment(assignment_id):
	Assignment.remove_fr_mongo(assignment_id)
	return "True"



@app.route('/admin/<string:uri>/assignments/create', methods=['GET', 'POST'])
def redner_create(uri):
	file_dict = {}
	if request.method == 'GET':
		return render_template("create_assignment.html", acc=session['email'])
	else:
		title = request.form['title']
		content = request.form['content']
		if 'file' not in request.files:
			title = request.form['title']
			content = request.form['content']
			date_due = request.form['days-until']
			format_due = date_due.split('-')
			due_date = datetime.datetime.utcfromtimestamp(datetime.datetime(year=int(format_due[0]), 
																															month=int(format_due[1]), 
																															day=int(format_due[2])).timestamp())
			assignment = Assignment(author=session['email'], 
														content=content, 
														title=title, 
														date_due=due_date)
			assignment.save_to_mongo()
			return redirect('https://kcbootcampers-api-heroku.herokuapp.com/admin/hub/'+uri)
		files = request.files.getlist("file")
		#if user does not select file, browser also
		#submit an empty part without filename
		for file in files:
			if file.filename == '':
				title = request.form['title']
				content = request.form['content']
				date_due = request.form['days-until']
				format_due = date_due.split('-')
				due_date = datetime.datetime.utcfromtimestamp(datetime.datetime(year=int(format_due[0]), 
																															month=int(format_due[1]), 
																															day=int(format_due[2])).timestamp())
				assignment = Assignment(author=session['email'], 
															content=content, 
															title=title, 
															date_due=due_date)
				assignment.save_to_mongo()
				return redirect('https://kcbootcampers-api-heroku.herokuapp.com/admin/hub/'+uri)
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file_dict[filename.split('.')[0]] = os.path.join("/uploads/images/", filename)
				try:
					os.mkdir(app.config['ADMIN_UPLOAD_FOLDER'])
				except FileExistsError:
					pass
				file.save(os.path.join(app.config['ADMIN_UPLOAD_FOLDER'], filename))
				title = request.form['title']
				content = request.form['content']
				date_due = request.form['days-until']
				format_due = date_due.split('-')
				due_date = datetime.datetime.utcfromtimestamp(datetime.datetime(year=int(format_due[0]), 
																															month=int(format_due[1]), 
																															day=int(format_due[2])).timestamp())
				name_of_file = filename
			else:
				return render_template("create_assignment.html", acc=session['email'])

		assignment = Assignment(author=session['email'], 
													content=content, 
													title=title,
													date_created=None, 
													date_due=due_date,
													_id=None, 
													**file_dict)
		assignment.save_to_mongo()
		return redirect('https://kcbootcampers-api-heroku.herokuapp.com/admin/hub/'+uri)


@app.route('/admin/<string:uri>/posts/create', methods=['GET', 'POST'])
def render_create(uri):
	file_dict = {}
	if request.method == 'GET':
		return render_template("create_post.html", acc=session['email'])
	else:
		title = request.form['title']
		content = request.form['content']
		if 'file' not in request.files:
			title = request.form['title']
			content = request.form['content']
			post = Post(author=session['email'], content=content, title=title)
			post.save_to_mongo()
			return redirect('https://kcbootcampers-api-heroku.herokuapp.com/admin/hub/'+uri)
		files = request.files.getlist("file")
		#if user does not select file, browser also
		#submit an empty part without filename
		for file in files:
			if file.filename == '':
				title = request.form['title']
				content = request.form['content']
				post = Post(author=session['email'], content=content, title=title)
				post.save_to_mongo()
				return redirect('https://kcbootcampers-api-heroku.herokuapp.com/admin/hub/'+uri)
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file_dict[filename.split('.')[0]] = os.path.join("/uploads/images/", filename)
				try:
					os.mkdir(app.config['ADMIN_UPLOAD_FOLDER'])
				except FileExistsError:
					pass
				file.save(os.path.join(app.config['ADMIN_UPLOAD_FOLDER'], filename))
				title = request.form['title']
				content = request.form['content']
				name_of_file = filename
			else:
				return render_template("create_post.html", acc=session['email'])

		post = Post(author=session['email'], 
							content=content, 
							title=title, 
							date_created=None, 
							_id=None, 
							**file_dict)
		post.save_to_mongo()
		return redirect('https://kcbootcampers-api-heroku.herokuapp.com/admin/hub/'+uri)

		



@app.route('/admin/<string:uri>/post/<string:post_id>', methods=['GET', 'POST'])
def render_post(uri, post_id):
	post = Post.get_by_id(post_id)
	if request.method == 'GET':
		return render_template("admin_posts.html", post=post, acc=session['email'])
	else:
		title = request.form['title']
		content = request.form['content']
		post = Post.get_by_id(post_id)
		post.update("title", title)
		post.update("content", content)
		post = Post.get_by_id(post_id)
		return render_template("admin_posts.html", post=post, acc=session['email'])


@app.route('/admin/<string:uri>/assignment/<string:assignment_id>', methods=['GET', 'POST'])
def render_assigment(uri, assignment_id):
	assignment = Assignment.get_by_id(assignment_id)
	if request.method == 'GET':
		return render_template("admin_assignments.html", assignment=assignment, acc=session['email'])
	else:
		title = request.form['title']
		content = request.form['content']
		assignment = Assignment.get_by_id(assignment_id)
		assignment.update("title", title)
		assignment.update("content", content)
		assignment = Assignment.get_by_id(assignment_id)
		return render_template("admin_assignments.html", assignment=assignment, acc=session['email'])


@app.route('/admin/make_admin/<string:_id>')
def make_admin(_id):
	User.admin(_id)
	return "True"


@app.route('/admin/make_teacher/<string:_id>')
def make_teacher(_id):
	User.teacher(_id)
	return "True"


@app.route('/admin/make_student/<string:_id>')
def make_student(_id):
	User.student(_id)
	return "True"



@app.route('/posts/get/images/<string:post_id>')
def get_images(post_id):
	post = Post.get_by_id(post_id)
	if post.imgs is not None:
		return dumps(post.imgs)
	else:
		return dumps({'imgs': {}})


@app.route('/assignments/get/images/<string:assignment_id>')
def get_assigment_images(assignment_id):
	assignment = Assignment.get_by_id(assignment_id)
	if assignment.imgs is not None:
		return dumps(assignment.imgs)
	else:
		return dumps({'imgs': {}})


@app.route('/assignments/set_cookie/<string:assignment_id>')
def set_assignment_cookie(assignment_id):
	assignment = Assignment.get_by_id(assignment_id)
	resp = make_response("Success")
	resp.set_cookie("assignment", assignment.title, expires=datetime.datetime.now() + datetime.timedelta(days=1))
	return resp


@app.route('/search/posts', methods=['GET', 'POST'])
def send_obj():
	posts = []
	dict_posts = {}
	if request.method == 'POST':
		data = request.form.get('data')
		if data is not None:
			posts = Post.search(qs=data)
			for post in posts:
				post.date_created = post.date_created.isoformat()
		try:
			for i in range(len(posts)):
				dict_posts[i] = posts[i].__dict__
			return dumps(dict_posts)
		except IndexError:
			return ""
	else:
		return ""


@app.route('/search/assignments', methods=['GET', 'POST'])
def send_assignment_obj():
	assignments = []
	dict_assignments = {}
	if request.method == 'POST':
		data = request.form.get('data')
		if data is not None:
			assignments = Assignment.search(qs=data)
			for assignment in assignments:
				assignment.date_created = assignment.date_created.isoformat()
				assignment.date_due = assignment.date_due.isoformat()
		try:
			for i in range(len(assignments)):
				dict_assignments[i] = assignments[i].__dict__
			return dumps(dict_assignments)
		except IndexError:
			return ""
	else:
		return ""


@app.route('/admin/other/create', methods=['POST', 'GET'])
def create_other():
	if request.method == 'POST':
		name = request.form.get('name')
		href = request.form.get('href')
		if name != "" and name is not None:
			other = Other(name, href)
			other.save_to_mongo()
			return dumps({'name': name, 'href': href, 'id': other._id})
	return ""


@app.route('/admin/book/create', methods=['POST', 'GET'])
def create_book():
	if request.method == 'POST':
		name = request.form.get('name')
		href = request.form.get('href')
		if name != "" and name is not None:
			book = Book(name, href)
			book.save_to_mongo()
			return dumps({'name': name, 'href': href, 'id': book._id})
	return ""


@app.route('/admin/video/create', methods=['POST', 'GET'])
def create_video():
	if request.method == 'POST':
		name = request.form.get('name')
		href = request.form.get('href')
		if name != "" and name is not None:
			video = Video(name, href)
			video.save_to_mongo()
			return dumps({'name': name, 'href': href, 'id': video._id})
	return ""


@app.route('/admin/other/remove/<string:uri>')
def remove_other(uri):
	Other.remove_fr_mongo(uri)
	return ""


@app.route('/admin/book/remove/<string:uri>')
def remove_book(uri):
	Book.remove_fr_mongo(uri)
	return ""


@app.route('/admin/video/remove/<string:uri>')
def remove_video(uri):
	Video.remove_fr_mongo(uri)
	return ""


@app.route('/signup_failed')
def render_signup_failed():
	return render_template("signup_failed.html", acc="Account")