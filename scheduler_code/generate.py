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


if __name__ == '__main__':
	db.create_all()
	user1 = User(id = 1, username = 'test', email = 'test@test.com', is_manager = True, dept = 'Production', password = bcrypt.generate_password_hash('test').decode('utf-8'))
	db.session.add(user1)
	db.session.commit()
	num = 100
	uid = [i for i in range(10001, 10001+num)]
	fake = Faker(['en_US', 'en_UK'])
	names = []
	for _ in range(num):
	    names.append(fake.name())
	emails = []
	for _ in range(num):
	    emails.append(fake.email())
	x = int(num/7)
	is_manager = [True]*(x)+[False]*(num-x+1)
	random.shuffle(is_manager)
	choices=[('Production', 'Production'),
	                             ('RaD', 'Research & Development'),
	                             ('Purchasing', 'Purchasing'),
	                             ('Marketing', 'Marketing'),
	                             ('HR', 'Human Resource'),
	                             ('Accounting', 'Accounting'),
	                             ('Operations', 'Operations')]
	dept = []
	for i in range(num):
	    dept.append(choices[random.randint(0,6)][0])
	image_file = ['default.jpg']*num
	password = []
	for i in range(num):
	    password.append(names[i].split()[1])
	for i in range(num):
	    user_i = User(id = uid[i], username = names[i], email = emails[i], is_manager = is_manager[i], dept = dept[i], image_file= image_file[i], password = password[i])
	    db.session.add(user_i)

	aid = [i for i in range(20001, 20001+num)]
	title = []
	for i in range(num):
	    title.append(fake.sentence())
	content = []
	for i in range(num):
	    content.append(fake.text())
	date_posted = []
	for _ in range(num):
	    date_posted.append(datetime.utcnow)
	user_id = []
	for i in range(num):
	    user_id.append(random.randint(10001, 10001+num))

	for i in range(num):
	    announce = Announcement(id = aid[i], title = title[i], content = content[i], user_id = user_id[i])
	    db.session.add(announce)
	recipient = []
	for i in range(num):
	    recipient.append(random.randint(10001, 10001+num))
	read = []
	for i in range(num):
	    read.append(random.randint(0,1))
	for i in range(num):
		try:
			annrec = Announcement_recipient(announcement_id = aid[i], recipient = 1)
			db.session.add(annrec)
			db.session.commit()
		except exc.IntegrityError as e:
			db.session.rollback()

	pid = [i for i in range(30001, 30001+num)]
	poll_title = []
	for i in range(num):
	    poll_title.append(fake.sentence())
	poll_date = []
	for _ in range(num):
	    poll_date.append(datetime.utcnow)
	question = []
	for i in range(num):
	    question.append("Is this valid Question "+str(i+1)+"?")
	option1 = ['Yes']*num
	option2 = ['No']*num
	option3 = ['Undecided']*num
	option4 = ['N/A']*num
	initiator = []
	for i in range(num):
	    initiator.append(random.randint(10001, 10001+num))
	audience = []
	for i in range(num):
	    audience.append(fake.sentence())
	for i in range(num):
	    new_poll = Poll(id = pid[i], title = poll_title[i], question = question[i], option1 = option1[i], option2 = option2[i], option3 = option3[i], option4 = option4[i], initiator_id = initiator[i])
	    db.session.add(new_poll)
	poll_recipient = []
	for i in range(num):
	    poll_recipient.append(random.randint(10001, 10001+num))
	completed = []
	for i in range(num):
	    completed.append(random.randint(0,1))
	choicess = ['Poll unfinished', 'Poll finished']
	poll_choice = []
	for i in range(num):
	    tt = random.randint(0,1)
	    poll_choice.append(choicess[tt])
	for i in range(num):
		try:
			poll_rec = Poll_recipient(poll_id = pid[i], recipient = 1, completed = completed[i], choice = poll_choice[i])
			db.session.add(poll_rec)
			db.session.commit()
		except:
			db.session.rollback()

	tid = [i for i in range(40001, 40001+num)]
	task_title = []
	for i in range(num):
	    task_title.append(fake.sentence())
	task_date = []
	for _ in range(num):
	    task_date.append(datetime.utcnow)
	task_content = []
	for i in range(num):
	    task_content.append(fake.text())
	task_user_id = []
	for i in range(num):
	    task_user_id.append(random.randint(10001, 10001+num))
	task_audience = []
	for i in range(num):
	    task_audience.append(fake.sentence())
	for i in range(num):
	    new_task = Task(id = tid[i], title = task_title[i], content = task_content[i], user_id = task_user_id[i])
	    db.session.add(new_task)
	task_recipient = []
	for i in range(num):
	    task_recipient.append(random.randint(10001, 10001+num))
	task_completed = []
	for i in range(num):
	    task_completed.append(random.randint(0,1))
	for i in range(num):
		try:
			task_rec = Task_recipient(task_id = tid[i], recipient = 1, completed = task_completed[i])
			db.session.add(task_rec)
			db.session.commit()
		except:
			db.session.rollback()
	db.session.commit()