from datetime import datetime
from scheduler import db, login_manager
from flask_login import UserMixin




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_manager = db.Column(db.Boolean, nullable=False)
    dept = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    announcement = db.relationship('Announcement', backref='author', lazy=True)
    poll = db.relationship('Poll', backref='author', lazy=True)
    task = db.relationship('Task', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Announcement('{self.title}', '{self.date_posted}')"

class Announcement_recipient(db.Model):
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcement.id'), nullable = False, primary_key = True)
    recipient = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False,primary_key = True)
    read = db.Column(db.Integer, default = 0, nullable = False)
    def __repr__(self):
        return f"Announcement_recipient('{self.announcement_id}','{self.recipient}','{self.read}')"



class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    question = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.Text, nullable=False)
    option2 = db.Column(db.Text, nullable=False)
    option3 = db.Column(db.Text)
    option4 = db.Column(db.Text)
    initiator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Poll('{self.title}', '{self.date_posted}')"


class Poll_recipient(db.Model):
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable = False, primary_key = True)
    recipient = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False,primary_key = True)
    completed = db.Column(db.Integer, default = 0, nullable = False)
    choice = db.Column(db.Text, default = 'Poll unfinished', nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Task('{self.title}', '{self.date_posted}')"

class Task_recipient(db.Model):
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable = False, primary_key = True)
    recipient = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False,primary_key = True)
    completed = db.Column(db.Integer, default = 0, nullable = False)

def init_db():
    db.create_all()
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
    shuffle(is_manager)
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
        announce = Announcement(id = aid[i], title = title[i], date_posted = date_posted[i], content = content[i], user_id = user_id[i])
        db.session.add(announce)
    recipient = []
    for i in range(num):
        recipient.append(random.randint(10001, 10001+num))
    read = []
    for i in range(num):
        read.append(random.randint(0,1))
    for i in range(num):
        annrec = Announcement_recipent(announcement_id = aid[i], recipient = recipient[i])
        db.session.add(annrec)
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
        new_poll = Poll(id = pid[i], title = poll_title[i], date_posted = poll_date[i], question = question[i], option1 = option1[i], option2 = option2[i], option3 = option3[i], option4 = option4[i], initiator_id = initiator[i], audience = audience[i])
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
        poll_rec = Poll_recipent(poll_id = pid[i], recipient = poll_recipient[i], completed = completed[i], choice = poll_choice[i])
        db.session.add(poll_rec)
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
        new_task = Task(id = tid[i], title = task_title[i], date_posted = task_date[i], content = task_content[i], user_id = task_user_id[i])
        db.session.add(new_task)
    task_recipient = []
    for i in range(num):
        task_recipient.append(random.randint(10001, 10001+num))
    task_completed = []
    for i in range(num):
        task_completed.append(random.randint(0,1))
    for i in range(num):
        task_rec = Task_recipent(task_id = tid[i], recipient = task_recipient[i], completed = task_completed[i])
        db.session.add(task_rec)
    db.session.commit()