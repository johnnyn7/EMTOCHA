from flask import render_template
from flask import redirect, request, session, url_for
from flask import flash, get_flashed_messages
from app import myapp_obj, db
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from datetime import datetime
#from wtforms.validators import Email
#from app.reply_emails import replyEmails
from app.send_emails import sendEmails
from app.register import registerUser 
from app.models import User, Emails, Todo, Profile, Message
from app.login import LoginForm
from app.todo import TodoForm
from app.profile import BioForm, PasswordForm, DeleteForm
from app.chat import ChatForm

#Yue Ying Lee
# index page is the page user see before registering or logging in
@myapp_obj.route("/")
def index():
    return render_template('index.html' )

#Yue Ying Lee
@myapp_obj.route("/homepage")
@login_required
def homepage():
    user = current_user
    user_fullname = user.fullname
    return render_template('homepage.html', user_fullname = user_fullname)

#Yue Ying Lee
@myapp_obj.route("/login", methods=['GET', 'POST'])
def login():
    # create form
    form = LoginForm()
    if form.validate_on_submit():
        valid_user = User.query.filter_by(username = form.username.data).first()
        if valid_user != None:
          if valid_user.check_password(form.password.data)== True:
             login_user(valid_user)
             return redirect(url_for('homepage'))
          else :
             flash(f'Invalid password. Try again.')
        else: 
             flash(f'Invalid username. Try again or register an account.')  

    return render_template('login.html', form=form)

@myapp_obj.route("/members/<string:name>/")
def getMember(name):
    return escape(name)

#Yue Ying Lee
@myapp_obj.route("/logout", methods = ['GET', 'POST'])
@login_required
def logout():
       logout_user()
       return redirect(url_for('login'))

#Yue Ying Lee
@myapp_obj.route("/register", methods =['GET', 'POST'])
def register():
        registerForm  = registerUser()
        if registerForm.validate_on_submit():
          same_Username = User.query.filter_by(username = registerForm.username.data).first()
          if same_Username == None:
            user = User(fullname = registerForm.fullname.data, username= registerForm.username.data)
            user.set_password(registerForm.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
          else :
             flash('The username is not available. Please choose another username.')
        return render_template('register.html', registerForm=registerForm)

#YueYingLee
@myapp_obj.route("/send_emails", methods = ['GET', 'POST'])
@login_required
def send_emails():
   send_emails_form = sendEmails()
   if send_emails_form.validate_on_submit():
    sender_id = current_user.id
    recipients_list = send_emails_form.recipients.data.split(',')
    valid_recipients_list = [] 
    valid_recipients_string = ""
    for recipient in recipients_list:
     valid_recipient =  User.query.filter_by(username = recipient.strip()).first()
     if (valid_recipient):
        valid_recipients_list.append(valid_recipient)
        valid_recipients_string =  valid_recipients_string + ", " + valid_recipient.username
    for valid_recipient in valid_recipients_list:
        recipient_username= valid_recipient.username
        recipient_id = valid_recipient.id
        flash(f' Valid recipients: {valid_recipient.username}')
        recipient_usernames = [r.username for r in valid_recipients_list]
        if current_user.username not in recipient_usernames: 
         valid_recipients_string = valid_recipients_string + "," +  current_user.username
         email_body = send_emails_form.email_body.data +  "\n\n" + "Respond to:  "+  valid_recipients_string 
        else:
         email_body = send_emails_form.email_body.data + "\n\n Respond to: "+ valid_recipients_string
         
        email = Emails (recipient_username = recipient_username, sender_username =  current_user.username, sender_id = sender_id, recipient_id = recipient_id, subject=send_emails_form.subject.data, email_body= email_body)
        db.session.add(email)
    if valid_recipients_list:
        db.session.commit()
        flash(f'Email successfully sent to {", ".join([r.username for r in valid_recipients_list])}!')
        return redirect('/homepage')
    else:
     flash(f' Invalid recipients. Retype username or go back to homepage.')

   return render_template('send_emails.html', send_emails_form = send_emails_form)

'''
def get_emails():
    all_emails_where_i_am_recipient_id = Emails.query(FIND_ALL_MY_EMAILS)
    for email in all_emails_where_i_am_recipient_id:
        subject = email.getSubject()
        sender = email.getSenderUsername()
        body = email.getBody()
        recipient_list = [sender] + getRecipientsFromBody(email.getBody())

def myFunction(email):
    last_line = getLastLineOfString(email.email_body)
    return [email.sender_username] +  last_line.split(',')
'''

#YueYingLee
@myapp_obj.route("/view_emails", methods = ['GET', 'POST'])
@login_required
def view_emails():
    emails = Emails.query.filter_by(recipient_id = current_user.id).all()
    return render_template('view_emails.html', user=current_user, emails = emails)


# @myapp_obj.route("/reply_emails/<int:id>", methods=['GET', 'POST'])
# @login_required
# def reply_email(id):
#     email_to_reply = Emails.query.filter_by(id=id).first()

#     # create a new sendEmails form object
#     reply_email_form = replyEmails()

#     # populate the form fields with the necessary information
#     reply_email_form.recipients.data = email_to_reply.sender_username
#     reply_email_form.subject.data = "Re: " + email_to_reply.subject
#     reply_email_form.email_body.data = f"\n\n\nOn {email_to_reply.timestamp}, {email_to_reply.sender_username} wrote:\n\n{email_to_reply.email_body}"

#     if reply_email_form.validate_on_submit():
#         # send the reply email
#         sender_id = current_user.id
#         recipient = User.query.filter_by(username=email_to_reply.sender_username).first()
#         if recipient:
#             recipient_id = recipient.id
#             email = Emails(recipient_username=email_to_reply.sender_username,
#                            sender_username=current_user.username,
#                            sender_id=sender_id,
#                            recipient_id=recipient_id,
#                            subject=reply_email_form.subject.data,
#                            email_body=reply_email_form.email_body.data)
#             db.session.add(email)
#             db.session.commit()
#             flash(f"Your reply email has been sent to {email_to_reply.sender_username}!")
#             return redirect('/homepage')
#         else:
#             flash("Invalid recipient. Please try again.")

#     return render_template('reply_emails.html', reply_emails_form=reply_email_form)


#kenneth
@myapp_obj.route("/todo", methods = ['GET', 'POST'])
@login_required
def add_todo():
    form = TodoForm()
    if form.validate_on_submit():
        todo = Todo(user = current_user, task = form.task.data, timestamp=datetime.now(), finished=False, favorite=False)
        db.session.add(todo)
        db.session.commit()
        flash('Successfully added a new task.')
        return redirect(url_for('add_todo'))

    user = current_user
    all_tasks = Todo.query.filter(Todo.user_id == current_user.id).all()
    fav_list = []
    not_fav_list = []
    for t in all_tasks:
        if t.favorite == True:
            fav_list.append(t)
        else:
            not_fav_list.append(t)
    return render_template("todo.html", form=form, fav_list=fav_list, not_fav_list=not_fav_list, user=user)

#kenneth
@myapp_obj.route("/finish-task/<int:id>", methods = ['GET', 'POST'])
@login_required
def finish_task(id):
    task = Todo.query.filter(Todo.id == id). first()
    if not task.finished:
        task.finished = True
    else:
        task.finished = False
    db.session.commit()
    return redirect(url_for('add_todo'))

#kenneth
@myapp_obj.route("/favorite-task/<int:id>", methods = ['GET', 'POST'])
@login_required
def favorite_task(id):
    task = Todo.query.filter(Todo.id == id). first()
    if not task.favorite:
        task.favorite = True
    else:
        task.favorite = False
    db.session.commit()
    return redirect(url_for('add_todo'))

#kenneth
@myapp_obj.route('/delete-task/<int:id>', methods=['GET','POST'])
@login_required
def delete_task(id):
    task = Todo.query.filter(Todo.id == id).first()
    if task:
        db.session.delete(task) 
        db.session.commit()
        flash('Task deleted')
    else:
        flash('There is no task to be deleted.')
    return redirect(url_for('add_todo'))

#kenneth
@myapp_obj.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    bio_form = BioForm()
    if bio_form.validate_on_submit() and request.method == "POST":
        #if a current bio exists and a new bio is submitted, delete the current bio and replace it with the new bio
        curr_bio = Profile.query.filter_by(user=current_user).first()
        if curr_bio:
            db.session.delete(curr_bio)
        new_bio = Profile(user=current_user, bio=bio_form.bio.data)
        db.session.add(new_bio)
        db.session.commit()
        flash('Successfully updated a new bio.')
        return redirect(url_for('profile'))
    else:
        #if nothing is submitted, the bio form will be empty, so assign the form.bio to the current bio
        curr_bio = Profile.query.filter_by(user=current_user).first()
        if curr_bio:
            bio_form.bio.data = curr_bio.bio
    
    pw_form = PasswordForm()
    if pw_form.validate_on_submit() and request.method == "POST":
        user = current_user
        if user.check_password(pw_form.old_password.data):
            if not user.check_password(pw_form.new_password.data):
                user.set_password(pw_form.new_password.data)
                db.session.commit()
                flash('Successfully updated password.')
                return redirect(url_for('profile'))
    
    #find all items associated with the current_user and delete them
    delete_form = DeleteForm()
    if delete_form.validate_on_submit() and request.method == "POST":
        user = current_user
        if user.check_password(delete_form.password.data):
            deleteTodo = Todo.query.filter_by(user=current_user).all()
            for item in deleteTodo:
                delete_task(item.id)

            b = Profile.query.filter_by(user=current_user).first()
            if b:
                delete_bio(b.user_id)

            m = Message.query.filter_by(username=current_user.username).all()
            for message in m:
                db.session.delete(message)
                db.session.commit()

            e = Emails.query.filter_by(sender_id=current_user.id).all()
            for emails in e:
                db.session.delete(emails)
                db.session.commit()

            db.session.delete(user)
            db.session.commit()
            logout_user
            flash('Successfully deleted account.')
            return redirect(url_for('login'))
        else:
            flash('wrong password!')
    return render_template('profile.html', bform=bio_form, pform=pw_form, user=current_user, dform=delete_form)

#kenneth
@myapp_obj.route('/delete-bio/<int:id>', methods=['GET','POST'])
@login_required
def delete_bio(id):
    b = Profile.query.filter(Profile.user_id == id).first()
    if b:
        db.session.delete(b) 
        db.session.commit()
        flash('Successfully deleted bio')
    else:
        flash('There is no bio to be deleted.')
    return redirect(url_for('profile'))
    
@myapp_obj.route('/chat', methods=['GET', 'POST'])
@login_required
def start_chat():
    form = ChatForm()
    if form.validate_on_submit():
        recipients = []
        for recipient_name in form.recipient_name.data:
            recipient = User.query.filter_by(username=recipient_name).first()
            if recipient is None:
                continue
            recipients.append(recipient)
        if not recipients:
            flash('At least one recipient must be entered.')
        else:
            dateAndTime = datetime.now()
            for recipient in recipients:
                message = Message(
                    username=current_user.username,
                    subject=form.subject.data,
                    message=form.message.data,
                    sending_user=current_user.id, 
                    receiving_user=recipient.id,
                    timestamp=dateAndTime
                )
                db.session.add(message)
            db.session.commit()
            flash('Message sent successfully!')
            return redirect(url_for('start_chat'))
    messages = Message.query.filter_by(receiving_user=current_user.id).all()
    return render_template('chat.html', user=current_user, form=form, messages=messages)

@myapp_obj.route('/chat/<int:id>', methods=['POST'])
@login_required
def delete_chat(id):
    message = Message.query.filter(Message.id == id, Message.receiving_user == current_user.id).first()
    if message:
        db.session.delete(message)
        db.session.commit()
        flash('Chat deleted', category='success')
        return redirect(url_for('start_chat'))
    else:
        flash('There is no chat to be deleted')
        return redirect(url_for('start_chat'))
    
@myapp_obj.route('/chat/search', methods=['POST'])
def search_messages():
    search_type = request.form.get('search_type')
    search_term = request.form.get('search_term')
    messages = Message.query.filter_by(receiving_user=current_user.id).all()
    if search_type == 'from_user':
        messages = [msg for msg in messages if search_term.lower() in msg.username.lower()]
    elif search_type == 'subject':
        messages = [msg for msg in messages if search_term.lower() in msg.subject.lower()]
    elif search_type == 'message':
        messages = [msg for msg in messages if search_term.lower() in msg.message.lower()]
    return render_template('chat.html', form=ChatForm(), messages=messages)