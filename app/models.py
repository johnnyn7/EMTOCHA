from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    fullname =db.Column(db.String(45), nullable = False)
    password = db.Column(db.String(128), nullable=False)

    emails = db.relationship('Emails', backref = 'user', lazy = 'dynamic')
    todo = db.relationship('Todo', backref = 'user', lazy = 'dynamic')
    profile = db.relationship('Profile', backref = 'user', lazy = 'dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        print("self.password is: ")
        print(self.password)
        print("input password is: ")
        print(password)
        return check_password_hash(self.password, password)

    def __repr__(self): #for debugging process
        return f'<user {self.id}: {self.username}, {self.fullname}>'

#sending emails function
class Emails(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   #recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   subject_line = db.Column(db.String(25))
   email_body = db.Column (db.String (600))
   timestamp = db.Column(db.DateTime, default=datetime.utcnow)
   def __repr__(self):
      return f'< Emails {self.id} Sender: {self.subject_line} Body: {self.email_body}>'
   
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(200))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



#received emails function 
#class received_emails (db.Model) 

#class sent_emails(db.Model)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
