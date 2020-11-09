from datetime import datetime
from scheduler import db, login_manager
from flask_login import UserMixin




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
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
    initiator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Poll('{self.title}', '{self.date_posted}')"

class Poll_response(db.Model):
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable = False, primary_key = True)
    recipient = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False,primary_key = True)
    choice = db.Column(db.Text, nullable=False)

class Poll_recipient(db.Model):
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable = False, primary_key = True)
    recipient = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False,primary_key = True)


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

def init_db():
    db.create_all()