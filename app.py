from flask import Flask, request, render_template, flash, url_for, redirect, abort, session, g
'''
Flask: the application object
request: a object,the data from a client's web page
render_template: a function
	(template_file_name,parameters)
flash: a function
url_for: a function
	(where)
redirect: a function
	redirect(url_for(where))
abort: for ERROR
session: per-client data
g: per-request data
'''
import os
from sqlite3 import dbapi2 as sqlite3

#Create the application, a Flask object-----------------
app=Flask(__name__)

#Configuration------------------------------------------
app.config.update(dict(
	DATABASE=os.path.join(app.root_path,'blog.db'),
	DEBUG=True,
	SECRET_KEY='#include<alex>',
	USERNAME='yuanmu',
	PASSWORD='PB15111615'))

#Database------------------------------------------------
def get_db():
	if not hasattr(g,'sqlite_db'):
		con = sqlite3.connect(app.config['DATABASE'])
		con.row_factory = sqlite3.Row
		g.sqlite_db = con		
	db = g.sqlite_db
	with app.open_resource('schema.sql',mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()
	return db

@app.teardown_appcontext
def close_db(error):
	if hasattr(g,'sqlite_db'):
		g.sqlite_db.close()


#MyBlog----------------------------------------------------------
@app.route('/')
def index():
	db = get_db()
	cur = db.execute('select username, title, content from blogs order by id desc')
	blogs = cur.fetchall()
	return render_template('index.html',blogs=blogs)

'''
HTTP methods:
	GET: want to get the info. from the page
	POST: want to send info. to the server
'''	
@app.route('/signup',methods=['GET','POST'])
def signup():
	error = None
	if request.method=='POST': #when user submit
		if not request.form['username'] or not request.form['password']:
			error = 'Invalid infomation!'
		else:
			db = get_db()
			db.execute('insert into users (username,passwd) values (?,?)',
					   [request.form['username'],request.form['password']])
			db.commit()
			flash('Congratualations!\nYou have successfully registered!')
			return redirect((url_for('index')))
	return render_template('signup.html',error=error)


@app.route('/login',methods=['GET','POST']) 
def login():
	error= None
	if request.method=='POST':
		db = get_db()
		tmp = (request.form['username'],)
		cur= db.execute('select passwd from users where username=?',tmp)
		match = cur.fetchone()
		#print match
		if match[0]==request.form['password']:
			session['logged_in']=True
			session['username']=request.form['username']
			flash('Successfully logged in!')
			return redirect(url_for('index'))
		else:
			error='Invalid username or incorrect password.'
	return render_template('login.html',error=error)

@app.route('/logout')
def logout():
	session['logged_in']=False
	session['username']=''
	flash('Now you are logged out.')
	return redirect(url_for('index'))

@app.route('/write_blog',methods=['Get','POST'])
def write_blog():
	error = None
	if request.method=='POST':
		if not request.form['title'] and not request.form['content']:
			error = 'Are you kidding me...'
		elif not request.form['title']:
			error = 'Title cannot be empty.'
		elif not request.form['content']:
			error = 'Only title?! You are creative.XD'
		else:
			db = get_db()
			db.execute('insert into blogs (username,title,content) values (?,?,?)',
						[session['username'],request.form['title'],request.form['content']])
			db.commit()
			flash('Your blog has been post successfully!')
			return redirect(url_for('users',username=session['username']))
	return render_template('write_blog.html',error=error)
	
@app.route('/user/<username>')
def users(username):
	db = get_db()
	tmp = (username,)
	cur = db.execute('select id,username,title,content from blogs where username=?',tmp)
	user_blogs = cur.fetchall()
	#print user_blogs
	return render_template('users.html',blogs=user_blogs)

@app.route('/delete_blog/<blog_id>')
def delete_blog(blog_id):
	db = get_db()
	tmp = (blog_id,)
	db.execute('delete from blogs where id=?',tmp)
	db.commit()
	flash('Your blog has been deleted successfully!')
	return redirect(url_for('users',username=session['username']))

if __name__=='__main__':
	app.run()
