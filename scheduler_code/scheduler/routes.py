
from flask import render_template, url_for, flash, redirect, request, abort
from scheduler import app, db, bcrypt
from scheduler.forms import SearchForm, RegistrationForm, LoginForm, UpdateAccountForm, AnnouncementForm, TaskForm, PollForm, PollResponseForm
from scheduler.models import User, Announcement, Task, Announcement_recipient, Poll, Poll_recipient, Task_recipient
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image
import re
from sqlalchemy import exc, desc, text, or_
from faker import Faker
import random
from datetime import datetime



@app.route('/') # home page of the website, login here
def home():

	return render_template('home.html')
	
@app.route('/main') # main user page
def main():
	page = request.args.get('page', 1, type = int)
	ann_ids = []
	ann_ids = db.session.query(Announcement_recipient.announcement_id).filter(Announcement_recipient.recipient == current_user.id).filter(Announcement_recipient.read == 0)
	announcements = Announcement.query.filter(Announcement.id.in_(ann_ids)).order_by(desc(Announcement.date_posted)).limit(3)
	task_ids = []
	task_ids = db.session.query(Task_recipient.task_id).filter(Task_recipient.recipient == current_user.id).filter(Task_recipient.completed == 0)
	tasks = Task.query.filter(Task.id.in_(task_ids)).order_by(desc(Task.date_posted)).limit(3)
	poll_ids = []
	poll_ids = db.session.query(Poll_recipient.poll_id).filter(Poll_recipient.recipient == current_user.id).filter(Poll_recipient.completed == 0)
	polls = Poll.query.filter(Poll.id.in_(poll_ids)).order_by(desc(Poll.date_posted)).limit(3)
	return render_template('main.html', announcements =announcements, tasks = tasks, polls = polls,title = 'Main')


@app.route('/about')
def about():
	return  render_template('about.html', title = 'About')

@app.route("/register", methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if current_user.is_authenticated:
		return redirect(url_for('main'))
	if form.validate_on_submit():
		hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		manager = False
		if form.role.data == "manager":
			manager = True
		user = User(username=form.username.data, email=form.email.data, password=hashed_pw, is_manager=manager, dept=form.dept.data)
		db.session.add(user)
		db.session.commit()		
		flash(f'Account created for {form.username.data}!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if current_user.is_authenticated:
		return redirect(url_for('main'))
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		# check if login email and pw is ocrrect
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

# save the pic into static/profile_pics
def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	# resize the image to (125, 125)
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


@app.route("/depts", methods=['GET'])
def depts():
	depts = ['Production', 'RaD', 'Purchasing', 'Marketing','HR', 'Accounting', 'Operations']
	belong = [None] * 7
	for i in range(7):
		belong[i] = db.session.query(User.username).filter(User.dept == depts[i])
	return render_template('depts.html', title='Departments', depts=depts, belong=belong)


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email    = form.email.data
		current_user.dept = form.dept.data
		db.session.commit()
		flash('your account has been update','success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
		form.dept.data = current_user.dept
	image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', 
								image_file = image_file, form = form)



@app.route("/all_announcements", methods=['GET', 'POST'])
def all_announcements():
	page = request.args.get('page', 1, type = int)
	#announcements = Announcement.query.paginate(per_page = 5)
	ann_ids = []
	ann_ids = db.session.query(Announcement_recipient.announcement_id).filter(Announcement_recipient.recipient == current_user.id)
	announcements = Announcement.query.filter(Announcement.id.in_(ann_ids)).order_by(desc(Announcement.date_posted)).paginate(per_page = 5)
	return render_template('all_announcements.html', announcements =announcements, title = 'All announcements')

@app.route("/my_ann", methods=['GET', 'POST'])
def my_ann():
	page = request.args.get('page', 1, type = int)
	#announcements = Announcement.query.paginate(per_page = 5)
	ann_ids = []
	ann_ids = db.session.query(Announcement_recipient.announcement_id).filter(Announcement_recipient.recipient == current_user.id)
	announcements = Announcement.query.filter(Announcement.user_id == current_user.id).order_by(desc(Announcement.date_posted)).paginate(per_page = 5)
	return render_template('my_ann.html', announcements =announcements, title = 'My announcements')




general_groups = [('All','All Users'),('Managers','All Managers'),('Employees','All Employees')]
dept_groups = [				 	 ('Production', 'All Production'),
								 ('RaD', 'All Research & Development'),
								 ('Purchasing', 'All Purchasing'),
								 ('Marketing', 'All Marketing'),
								 ('HR', 'All Human Resource'),
								 ('Accounting', 'All Accounting'),
								 ('Operations', 'All Operations')]
departments = ['Managers','Employees','Production','RaD','Purchasing''Marketing','HR','Accounting','Operations']
audience_groups = general_groups + dept_groups





@app.route("/announcements/new", methods=['GET', 'POST'])
@login_required
def new_announcement():
	form = AnnouncementForm()
	form.audience.choices = audience_groups
	if form.validate_on_submit():
		announcement = Announcement(title = form.title.data, content = form.content.data, 
						author = current_user)
		db.session.add(announcement)
		db.session.commit()
		ann_id = db.session.query(Announcement).order_by(Announcement.id.desc()).first().id
		audi_groups = form.audience.data
		announcement_rec = Announcement_recipient(announcement_id = ann_id, recipient = current_user.id, read = 1)
		db.session.add(announcement_rec)
		db.session.commit()
		
		# loop over different scenarios
		if ('All' in audi_groups) or ('Managers' in audi_groups and 'Employees' in audi_groups):
			all_users = User.query.all()
			for user in all_users:
				try:
					announcement_rec = Announcement_recipient(announcement_id = ann_id, recipient = user.id, read = 0)
					db.session.add(announcement_rec)
					db.session.commit()
				except exc.IntegrityError as e:
					db.session.rollback()

			db.session.commit()

		else:
			if 'Managers' in audi_groups:
				managers = User.query.filter(User.is_manager)
				for man in managers:
					try:
						announcement_rec = Announcement_recipient(announcement_id = ann_id, recipient = man.id, read = 0)
						db.session.add(announcement_rec)
						db.session.commit()
					except exc.IntegrityError as e:
						db.session.rollback()
			if 'Employees' in audi_groups:
				employees = User.query.filter(User.is_manager == False)
				for emp in employees:
					try:
						announcement_rec = Announcement_recipient(announcement_id = ann_id, recipient = emp.id,  read = 0)
						db.session.add(announcement_rec)
						db.session.commit()
					except exc.IntegrityError as e:
						db.session.rollback()
			for dept in departments:
				dept_members = User.query.filter(User.dept == dept)
				for mem in dept_members:
					try:
						announcement_rec = Announcement_recipient(announcement_id = ann_id, recipient = mem.id,  read = 0)
						db.session.add(announcement_rec)
						db.session.commit()
					except exc.IntegrityError as e:
						db.session.rollback()

		flash('Your annoucement has been created', 'success')
		return redirect(url_for('main'))
	return render_template('new_announcement.html', title='New accouncement', form = form, legend = 'New Announcement')

@app.route("/announcements/<announcement_id>")
def announcement(announcement_id):
	announcement = Announcement.query.get_or_404(announcement_id)
	read = db.session.query(Announcement_recipient.read).filter(Announcement_recipient.announcement_id == announcement_id).filter(Announcement_recipient.recipient == current_user.id).first()
	return render_template('announcement.html', title= announcement.title, announcement = announcement, read = int(read[0]))


# Update announcement content
@app.route("/announcements/<announcement_id>/update", methods=['GET', 'POST'])
@login_required

def update_announcement(announcement_id):
	announcement = Announcement.query.get_or_404(announcement_id)
	if announcement.author != current_user:
		abort(403)
	form = AnnouncementForm()
	form.audience.choices = audience_groups
	if form.validate_on_submit():
		announcement.title = form.title.data
		announcement.content = form.content.data
		db.session.commit()
		audi_groups = form.audience.data
		ann_id = announcement_id
		# first we remove this announcements from all original audience
		ann_rec = db.session.query(Announcement_recipient).filter(Announcement_recipient.announcement_id == announcement_id).filter(Announcement_recipient.recipient != current_user.id).all()
		for p in ann_rec:
			db.session.delete(p)
		db.session.commit()
		# loop over different scenarios
		if ('All' in audi_groups) or ('Managers' in audi_groups and 'Employees' in audi_groups):
			all_users = User.query.all()
			for user in all_users:
				try:
					announcement_rec = Announcement_recipient(announcement_id = ann_id, recipient = user.id, read = 0)
					db.session.add(announcement_rec)
					db.session.commit()
				except exc.IntegrityError as e:
					db.session.rollback()

			db.session.commit()

		else:
			if 'Managers' in audi_groups:
				managers = User.query.filter(User.is_manager)
				for man in managers:
					try:
						announcement_rec = Announcement_recipient(announcement_id = ann_id, recipient = man.id, read = 0)
						db.session.add(announcement_rec)
						db.session.commit()
					except exc.IntegrityError as e:
						db.session.rollback()
			if 'Employees' in audi_groups:
				employees = User.query.filter(User.is_manager == False)
				for emp in employees:
					try:
						announcement_rec = Announcement_recipient(announcement_id = ann_id, recipient = emp.id,  read = 0)
						db.session.add(announcement_rec)
						db.session.commit()
					except exc.IntegrityError as e:
						db.session.rollback()
			for dept in departments:
				dept_members = User.query.filter(User.dept == dept)
				for mem in dept_members:
					try:
						announcement_rec = Announcement_recipient(announcement_id = ann_id, recipient = mem.id,  read = 0)
						db.session.add(announcement_rec)
						db.session.commit()
					except exc.IntegrityError as e:
						db.session.rollback()


		flash('Your post has been updated!', 'success')
		return redirect(url_for('announcement',announcement_id = announcement.id))
	elif request.method == 'GET':
		form.title.data = announcement.title
		form.content.data = announcement.content
		form.audience.choices = audience_groups
	return render_template('new_announcement.html', title= 'Update Announcement' , 
								form = form, legend = 'Update Announcement')

@app.route("/announcements/<int:announcement_id>/delete", methods=['POST'])
@login_required
def delete_announcement(announcement_id):
	announcement = Announcement.query.get_or_404(announcement_id)
	ann_recs = Announcement_recipient.query.filter(Announcement_recipient.announcement_id == announcement_id)
	if announcement.author != current_user:
		abort(403)
	db.session.delete(announcement)
	for ann_rec in ann_recs:
		db.session.delete(ann_rec)
	db.session.commit()
	flash('Your announcement has been deleted!', 'success')
	return redirect(url_for('main'))


@app.route("/announcements/<int:announcement_id>/mark", methods=['GET','POST'])
@login_required
def mark_announcement(announcement_id):
	ann_rec = db.session.query(Announcement_recipient).filter(Announcement_recipient.announcement_id == announcement_id).filter(Announcement_recipient.recipient == current_user.id).first()
	r_val = 1- ann_rec.read
	ann_rec.read = r_val
	db.session.commit()
	if r_val == 1:
		print('read value now is ', r_val)
		flash('You have mark this announcement as read!', 'success')
	else:
		flash('You have mark this announcement as unread!', 'success')
	return redirect(url_for('announcement', announcement_id = announcement_id))




@app.route("/poll/new", methods=['GET', 'POST'])
@login_required
def new_poll():
	form = PollForm()
	form.audience.choices = audience_groups
	if form.validate_on_submit():
		if form.option3.data != '' and form.option4.data != '':
			poll = Poll(title = form.title.data, 
						author = current_user, question = form.question.data, 
						option1 = form.option1.data, option2 = form.option2.data,
						option3 = form.option3.data, option4 = form.option4.data)
		elif form.option3.data == '' and form.option4.data != '':
			poll = Poll(title = form.title.data, 
						author = current_user, question = form.question.data, 
						option1 = form.option1.data, option2 = form.option2.data,
						option4 = form.option4.data)
		elif form.option3.data != '' and form.option4.data == '':
			poll = Poll(title = form.title.data, 
						author = current_user, question = form.question.data, 
						option1 = form.option1.data, option2 = form.option2.data,
						option3 = form.option3.data)
		else:
			poll = Poll(title = form.title.data, 
						author = current_user, question = form.question.data, 
						option1 = form.option1.data, option2 = form.option2.data)
		db.session.add(poll)
		db.session.commit()

		poll_id = db.session.query(Poll).order_by(Poll.id.desc()).first().id
		poll_rec = Poll_recipient(poll_id = poll_id, recipient = current_user.id)
		db.session.add(poll_rec)
		db.session.commit()

		audi_groups = form.audience.data
		
		# loop over different scenarios
		if ('All' in audi_groups) or ('Managers' in audi_groups and 'Employees' in audi_groups):
			all_users = User.query.all()
			for user in all_users:
				try:
					poll_rec = Poll_recipient(poll_id = poll_id, recipient = user.id)
					db.session.add(poll_rec)
					db.session.commit()
				except exc.IntegrityError as e:
					db.session.rollback()

		else:
			if 'Managers' in audi_groups:
				managers = User.query.filter(User.is_manager)
				for man in managers:
					try:
						poll_rec = Poll_recipient(poll_id = poll_id, recipient = man.id)
						db.session.add(poll_rec)
						db.session.commit()
					except exc.IntegrityError as e:
						db.session.rollback()
			if 'Employees' in audi_groups:
				employees = User.query.filter(User.is_manager == False)
				for emp in employees:
					try:
						poll_rec = Poll_recipient(poll_id = poll_id, recipient = emp.id)
						db.session.add(poll_rec)
						db.session.commit()
					except exc.IntegrityError as e:
						db.session.rollback()
			for dept in departments:
				dept_members = User.query.filter(User.dept == dept)
				for mem in dept_members:
					try:
						task_rec = Poll_recipient(poll_id = poll_id, recipient = mem.id)
						db.session.add(poll_rec)
						db.session.commit()
						db.session.commit()
					except exc.IntegrityError as e:
						db.session.rollback()

		flash('Your poll has been created', 'success')
		return redirect(url_for('main'))
	return render_template('new_poll.html', title='New poll', form = form, legend = 'New Poll')

@app.route("/polls/<poll_id>", methods=['GET', 'POST'])
@login_required
def poll(poll_id):
	poll = Poll.query.get_or_404(poll_id)
	duplicate = Poll_recipient.query.filter(Poll_recipient.poll_id == poll_id).filter(Poll_recipient.recipient == current_user.id).first()
	
	
	if duplicate.completed == 1:
		print(duplicate)
		flash("You have submitted to this poll already.", 'warning')
		return redirect(url_for('poll_result', poll_id = poll.id))

	form = PollResponseForm(title=poll.title, question=poll.question)
	option1 = poll.option1
	option2 = poll.option2
	form.choice.choices = [(option1, option1), (option2, option2)]
	if poll.option3 is not None:
		option3 = poll.option3
		form.choice.choices.append((option3, option3))
	if poll.option4 is not None:
		option4 = poll.option4
		form.choice.choices.append((option4, option4))
	if form.validate_on_submit():
		poll_res = Poll_recipient.query.filter(Poll_recipient.poll_id == poll_id).filter(Poll_recipient.recipient == current_user.id).first()
		poll_res.completed = 1
		poll_res.choice = form.choice.data
		db.session.commit()
		flash('Your response has been submitted', 'success')
		return redirect(url_for('poll_result', poll_id = poll.id))
	
	return render_template('poll.html', poll = poll, form = form, completed = False)


@app.route("/polls/<poll_id>/result")
@login_required
def poll_result(poll_id):
	poll = Poll.query.get_or_404(poll_id)
	responded = 0
	count_op3 = -1
	count_op4 = -1
	poll_ids = db.session.query(Poll_recipient.poll_id).filter(Poll_recipient.poll_id == poll_id)
	poll_results = Poll_recipient.query.filter(Poll_recipient.poll_id.in_(poll_ids))
	for poll_result in poll_results: 
		if poll_result.choice != 'Poll unfinished':
			responded += 1
	count_op1 = poll_results.filter(Poll_recipient.choice == poll.option1).count()
	count_op2 = poll_results.filter(Poll_recipient.choice == poll.option2).count()
	if poll.option3 is not None:
		count_op3 = poll_results.filter(Poll_recipient.choice == poll.option3).count()
	if poll.option4 is not None:
		count_op4 = poll_results.filter(Poll_recipient.choice == poll.option4).count()
	return render_template('poll_result.html', poll=poll, poll_results=poll_results, 
		count_op2=count_op2, count_op1=count_op1, count_op3=count_op3, count_op4=count_op4,responded=responded)
	

@app.route("/all_polls", methods=['GET', 'POST'])
def all_polls():
	page = request.args.get('page', 1, type = int)
	#polls = Poll.query.paginate(per_page = 5)
	poll_ids = []
	poll_ids = db.session.query(Poll_recipient.poll_id).filter(Poll_recipient.recipient == current_user.id)
	polls = Poll.query.filter(Poll.id.in_(poll_ids)).order_by(desc(Poll.date_posted)).paginate(per_page = 5)
	return render_template('all_polls.html', polls =polls, title = 'All polls')



@app.route("/my_polls", methods=['GET', 'POST'])
def my_polls():
	page = request.args.get('page', 1, type = int)
	#polls = Poll.query.paginate(per_page = 5)
	poll_ids = []
	poll_ids = db.session.query(Poll_recipient.poll_id).filter(Poll_recipient.recipient == current_user.id)
	polls = Poll.query.filter(Poll.initiator_id == current_user.id).order_by(desc(Poll.date_posted)).paginate(per_page = 5)
	return render_template('my_polls.html', polls =polls, title = 'My polls')


@app.route("/polls/<int:poll_id>/delete", methods=['POST'])
@login_required
def delete_poll(poll_id):
	poll = Poll.query.get_or_404(poll_id)
	poll_recs = Poll_recipient.query.filter(Poll_recipient.poll_id == poll_id)
	if poll.author != current_user:
		abort(403)
	for poll_rec in poll_recs:
		db.session.delete(poll_rec)
	db.session.delete(poll)
	db.session.commit()
	flash('Your poll has been deleted!', 'success')
	return redirect(url_for('main'))	


@app.route("/all_tasks", methods=['GET', 'POST'])
def all_tasks():
	page = request.args.get('page', 1, type = int)
	#tasks = Task.query.paginate(per_page = 5)
	task_ids = []
	task_ids = db.session.query(Task_recipient.task_id).filter(Task_recipient.recipient == current_user.id)
	tasks = Task.query.filter(Task.id.in_(task_ids)).order_by(desc(Task.date_posted)).paginate(per_page = 5)
	return render_template('all_tasks.html', tasks =tasks, title = 'All tasks')


@app.route("/my_tasks", methods=['GET', 'POST'])
def my_tasks():
	page = request.args.get('page', 1, type = int)
	#tasks = Task.query.paginate(per_page = 5)
	task_ids = []
	task_ids = db.session.query(Task_recipient.task_id).filter(Task_recipient.recipient == current_user.id)
	tasks = Task.query.filter(Task.user_id == current_user.id).order_by(desc(Task.date_posted)).paginate(per_page = 5)
	return render_template('my_tasks.html', tasks =tasks, title = 'My tasks')


@app.route("/tasks/new", methods=['GET', 'POST'])
@login_required
def new_task():
	form = TaskForm()
	users = [(user.id, user.username) for user in User.query.all()]
	users.sort(key=lambda x: x[1])
	form.assignee1.choices = users
	users_null = [(user.id, user.username) for user in User.query.all()]
	users_null.sort(key=lambda x: x[1])
	users_null.insert(0, (-1, ''))
	for assignee in [form.assignee2, form.assignee3, form.assignee4, form.assignee5]:
		assignee.choices = users_null
	# form.audience.choices = audience_groups

	if form.validate_on_submit():
		task = Task(title = form.title.data, content = form.content.data, author = current_user)
		db.session.add(task)
		db.session.commit()

		task_id = db.session.query(Task).order_by(Task.id.desc()).first().id
		task_rec = Task_recipient(task_id = task_id, recipient = current_user.id)
		db.session.add(task_rec)
		db.session.commit()

		assignees = []
		for assignee in [form.assignee1, form.assignee2, form.assignee3, form.assignee4, form.assignee5]:
			if assignee.data != -1 and assignee.data not in assignees:
				assignees.append(assignee.data)

		# users = User.query.filter(User.username in assignees)

		for userid in assignees:
			task_rec = Task_recipient(task_id = task_id, recipient = userid)
			try:
				db.session.add(task_rec)
				db.session.commit()
			except exc.IntegrityError as e:
				db.session.rollback()
		



		flash('Your task has been assigned', 'success')
		return redirect(url_for('main'))
	return render_template('new_task.html', title='New task', form = form)


@app.route("/tasks/<task_id>")
def task(task_id):
	task = Task.query.get_or_404(task_id)
	completed = db.session.query(Task_recipient.completed).filter(Task_recipient.task_id == task_id).filter(Task_recipient.recipient == current_user.id).first()
	total_workers = db.session.query(Task_recipient).filter(Task_recipient.task_id == task_id).filter(Task_recipient.recipient != -1).count()
	done_workers = db.session.query(Task_recipient).filter(Task_recipient.task_id == task_id).filter(Task_recipient.completed == 1).count()
	return render_template('task.html', title= task.title, task = task,completed = int(completed[0]), total = total_workers, done = done_workers)

@app.route("/tasks/<int:task_id>/mark", methods=['GET','POST'])
@login_required
def mark_task(task_id):
	task_rec = db.session.query(Task_recipient).filter(Task_recipient.task_id == task_id).filter(Task_recipient.recipient == current_user.id).first()
	task_rec.completed = 1- task_rec.completed
	db.session.commit()
	if task_rec.completed == 1:
		flash('You have mark this task as completed!', 'success')
	else:
		flash('You have mark this task as not completed!', 'success')
	return redirect(url_for('task', task_id = task_id))



# Update announcement content
@app.route("/tasks/<task_id>/update", methods=['GET', 'POST'])
@login_required

def update_task(task_id):
	task = Task.query.get_or_404(task_id)
	if task.author != current_user:
		abort(403)
	form = TaskForm()
	users = [(user.id, user.username) for user in User.query.all()]
	users.sort(key=lambda x: x[1])
	form.assignee1.choices = users
	users_null = [(user.id, user.username) for user in User.query.all()]
	users_null.sort(key=lambda x: x[1])
	users_null.insert(0, (-1, ''))
	for assignee in [form.assignee2, form.assignee3, form.assignee4, form.assignee5]:
		assignee.choices = users_null

	if form.validate_on_submit():
		task.title = form.title.data
		task.content = form.content.data
		db.session.commit()

		task_rec = db.session.query(Task_recipient).filter(Task_recipient.task_id == task_id).filter(Task_recipient.recipient != current_user.id).all()
		for rec in task_rec:
			db.session.delete(rec)
		db.session.commit()
		assignees = []
		for assignee in [form.assignee1, form.assignee2, form.assignee3, form.assignee4, form.assignee5]:
			if assignee.data != -1 and assignee.data not in assignees:
				assignees.append(assignee.data)

		for userid in assignees:
			task_rec = Task_recipient(task_id = task_id, recipient = userid)
			try:
				db.session.add(task_rec)
				db.session.commit()
			except exc.IntegrityError as e:
				db.session.rollback()
		flash('Your task content has been updated!', 'success')
		return redirect(url_for('task',task_id = task.id))
	elif request.method == 'GET':
		form.title.data = task.title
		form.content.data = task.content
	return render_template('new_task.html', title= 'Update Task' , 
								form = form, legend = 'Update Task')

@app.route("/tasks/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
	task = Task.query.get_or_404(task_id)
	task_recs = Task_recipient.query.filter(Task_recipient.task_id == task_id)
	if task.author != current_user:
		abort(403)
	for task_rec in task_recs:
		db.session.delete(task_rec)
	db.session.delete(task)
	db.session.commit()
	flash('Your task has been deleted!', 'success')
	return redirect(url_for('main'))

search_groups = [('Announcement','Announcement'),('Task','Task'),('Poll','Poll')]
@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
	form = SearchForm()
	form.target.choices = search_groups
	if form.validate_on_submit():
		search_targets = form.target.data
		keyword = form.keyword.data
		return redirect(url_for('search_result',keyword = keyword, search_targets = search_targets))
	return render_template('search.html',form = form, title= 'Search What You Want')

@login_required
@app.route("/search/<string:keyword>/<string:search_targets>/result", methods=['GET', 'POST'])
def search_result(keyword, search_targets):
	anns, tasks, polls = None, None, None
	if 'Announcement' in search_targets:
		ann_ids = db.session.query(Announcement_recipient.announcement_id).filter(Announcement_recipient.recipient == current_user.id)
		anns = Announcement.query.filter(Announcement.id.in_(ann_ids)).filter(or_(
									Announcement.title.like("%"+keyword+"%"),
									Announcement.content.like("%"+keyword+"%")
									)).order_by(desc(Announcement.date_posted))

	if 'Poll' in search_targets:
		poll_ids = db.session.query(Poll_recipient.poll_id).filter(Poll_recipient.recipient == current_user.id)
		polls = Poll.query.filter(Poll.id.in_(poll_ids)).filter(or_(
									Poll.title.like("%"+keyword+"%"),
									Poll.question.like("%"+keyword+"%")
									)).order_by(desc(Poll.date_posted))

	if 'Task' in search_targets:
		task_ids = db.session.query(Task_recipient.task_id).filter(Task_recipient.recipient == current_user.id)
		tasks = Task.query.filter(Task.id.in_(task_ids)).filter(or_(
									Task.title.like("%"+keyword+"%"),
									Task.content.like("%"+keyword+"%")
									)).order_by(desc(Task.date_posted))
	return render_template('search_result.html',title = 'Search Results', anns = anns, polls = polls, tasks = tasks )