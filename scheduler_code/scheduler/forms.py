from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import widgets, StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField,SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import email_validator
from scheduler.models import User

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators = 
					[DataRequired(),Length(min = 2, max = 20) ])
	role = SelectField('Role', [DataRequired()],
                        choices=[('employee', 'Employee'),
                                 ('manager', 'Manager')])
	dept = SelectField('Department', [DataRequired()],
						choices=[('Production', 'Production'),
                                 ('RaD', 'Research & Development'),
                                 ('Purchasing', 'Purchasing'),
                                 ('Marketing', 'Marketing'),
                                 ('HR', 'Human Resource'),
                                 ('Accounting', 'Accounting'),
                                 ('Operations', 'Operations')])
	email = StringField('Email', validators = 
					[DataRequired(), Email() ])
	password = PasswordField('Password', validators = [DataRequired()] )
	confirm_password = PasswordField('Confirm Password', 
					validators =[DataRequired(), EqualTo('password')])
	submit = SubmitField('Signup')


	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken. Please choose a different one.')



class LoginForm(FlaskForm):
	email = StringField('Email', validators = 
					[DataRequired(), Email() ])
	password = PasswordField('Password', validators = [DataRequired()] )
	remember = BooleanField('remeber me')
	submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators = 
					[DataRequired(),Length(min = 2, max = 20) ])
	email = StringField('Email', validators = 
					[DataRequired(), Email() ])
	dept = SelectMultipleField('Department', [DataRequired()],
						choices=[('Production', 'Production'),
                                 ('RaD', 'Research & Development'),
                                 ('Purchasing', 'Purchasing'),
                                 ('Marketing', 'Marketing'),
                                 ('HR', 'Human Resource'),
                                 ('Accounting', 'Accounting'),
                                 ('Operations', 'Operations')])
	picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg','png'])])
	submit = SubmitField('Update')


	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is taken. Please choose a different one.')



class AnnouncementForm(FlaskForm):
	title = StringField('Title', validators = [DataRequired()])
	content = TextAreaField('Content', validators = [DataRequired()])
	submit = SubmitField('Post')
	audience = MultiCheckboxField('What are you sending this to?')



class TaskForm(FlaskForm):
	title = StringField('Title', validators = [DataRequired()])
	content = TextAreaField('Content', validators = [DataRequired()])
	submit = SubmitField('Post')
	audience = MultiCheckboxField('What are you sending this to?')

class PollForm(FlaskForm):
	title = StringField('Title of your poll', validators = [DataRequired()])
	question = StringField('Your question for the poll', validators = [DataRequired()])
	option1 = StringField('Option 1', validators = [DataRequired()])
	option2 = StringField('Option 2', validators = [DataRequired()])
	submit = SubmitField('Post')
	audience = MultiCheckboxField('What are you sending this to?')

