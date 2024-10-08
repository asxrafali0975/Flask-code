# IMPORTS 
from flask import Flask, request, jsonify, render_template, redirect, url_for, session,render_template_string,send_from_directory
from flask_socketio import SocketIO, send, emit
from pymongo import MongoClient
from flask_mail import Mail, Message
from flask_cors import CORS  
import eventlet
import eventlet.wsgi

import pyotp
import os

# Get the IP address of the SMTP server (optional)

# Configurations
app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['app-users'] 
collection = db['users'] 

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME="ashrafalistudy@gmail.com",
    MAIL_PASSWORD = "fvvj ezai khpb vwqm"  # Make sure to set this in environment variables or secure config
)
mail = Mail(app)

app.secret_key = 'secretkeyforsession'

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit max size to 16 MB

app.secret_key="filesuploadsecret"
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, async_mode='eventlet') 
CORS(app) 

# Main code



@app.route("/")
def register_page():
    return render_template("register_page.html")
    
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session["username"] = request.form['username']
        session["email"] = request.form["email"]
        session["password"] = request.form["password"]  
        session["conf_password"] = request.form["2password"]  
        session["profilepic"] = request.form['profilepic']
        
        totp = pyotp.TOTP('secretcode')
        gen_otp = totp.now() 
        
        msg = Message(
            'Verification',
            sender="ashrafalistudy@gmail.com",
            recipients=[session["email"]],
            body=f'Your OTP is {gen_otp}'
        )
        mail.send(msg)
        session['otp'] = gen_otp
        
        return render_template("verify_otp.html")
    return render_template("register_page.html")
        
@app.route("/verifyotp", methods=['POST'])
def verifyotp():
    if request.method == "POST":
        received_otp = request.form["received_otp"]
        if received_otp == session.get('otp'):
            if session.get('password') == session.get('conf_password'):
                existinguser = collection.find_one({"email": session.get('email')})
                if existinguser:
                    return render_template_string('<h3 style="color:red;">Email already exists, login instead</h3>')
                else:
                    user = {
                        "username": session.get('username'),
                        "email": session.get('email'),
                        "password": session.get('password'),
                        "profilepic": session.get('profilepic'),
                        "user_post": [],
                        "followers": [],
                    }
                    result = collection.insert_one(user)
                    if result:
                        return redirect(url_for('login', message="Successful registration, now login"))
                    return render_template_string('<h3 style="color:red;">Registration failed. Please try again.</h3>')
            else:
                return render_template_string('<h3 style="color:red;">Passwords do not match</h3>')
        else:
            return render_template_string('<h3 style="color:red;">Invalid OTP</h3>')
    return render_template("verify_otp.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        existinguser = collection.find_one({"email": email})
        
        if existinguser:
            if password == existinguser["password"]:
                session['current_user'] = existinguser['username']
                return redirect(url_for('user_profile', username=existinguser['username']))
            return render_template_string('<h3 style="color:red;">Wrong password</h3>')
        return render_template_string('<h3 style="color:red;">No user found, try registering</h3>')
    return render_template("login_page.html")
    
@app.route("/post/<username>", methods=["POST"])
def add_post(username):
    if request.method == "POST":
        user_post = request.form.get('post')
        user = collection.find_one({"username": username})
        user['user_post'].append(user_post)
        
        collection.update_one(
            {"username": username},
            {"$set": {"user_post": user['user_post']}}
        )
        return redirect(url_for('user_profile', username=username))

@app.route("/user/<username>")
def user_profile(username):
    user = collection.find_one({"username": username})
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string if necessary
        return render_template("User_profile.html", existinguser=user)
    return "User not found", 404

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_user = request.form["usermail"]
        user = collection.find_one({"username": search_user})
       
        if user:  
            user["_id"] = str(user["_id"])  
            return render_template("User_profile2.html", existinguser=user)
        return render_template_string('<h3 style="color:red;">No user found</h3>')
    return render_template("Search_page.html")

@app.route("/follow/<username>", methods=["POST"])
def follow(username):
    followed_by = session.get('current_user')
    
    

    followed_to = username
    print(followed_by,followed_to)
    followed_to_id = collection.find_one({"username": followed_to})
    
    if not followed_to_id:
        return redirect(url_for('user_profile', username=followed_by))
   
    if followed_by==followed_to:
        print("TWO ARE SAME")
        return redirect(url_for('user_profile',username=followed_by))
    else:
        print('2 ARE DIFFERENT')
        if followed_by in followed_to_id['followers']:
            name_index = followed_to_id['followers'].index(followed_by)
            followed_to_id['followers'].pop(name_index)
        else:
            followed_to_id['followers'].append(followed_by)
        collection.update_one(
        {"username": followed_to},
        {"$set": {"followers": followed_to_id['followers']}}
        )
        return redirect(url_for('user_profile2', username=followed_to))
    
@app.route("/user2/<username>")
def user_profile2(username):
    user = collection.find_one({"username": username})
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string if necessary
        return render_template("User_profile2.html", existinguser=user)
    return "User not found", 404



@app.route('/upload',methods=["POST"])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file:
        session['filename'] = file.filename
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        name=collection.find_one({"username":session.get('current_user')})
        name["_id"]=str(name["_id"])
        collection.update_one({"username":session.get('current_user')},{"$set":{"profilepic":filename}})
        return render_template('User_profile.html', existinguser=name)
        
    
    
@app.route('/upload_pfp')
def upload_pfp():
    return render_template_string('''
    <!doctype html>
    <title>Upload a File</title>
    <h1>Upload a File</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input type="file" name="file" required>
      <input type="submit" value="Upload">
    </form>
    ''')
    
@app.route('/show')
def show():
    filename = session.get('filename')
    if filename:
        return render_template_string('''
        <!doctype html>
        <title>Uploaded File</title>
        <img src="{{ url_for('uploaded_file', filename=filename) }}" alt="Uploaded File">
        ''', filename=filename)
    return 'No file uploaded'
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/delete_pfp')
def delete_pfp():
    user=collection.find_one({"username":session.get('current_user')})
    collection.update_one({"username":session.get('current_user')},{"$set":{"profilepic":""}})
    return render_template('User_profile.html', existinguser=user)
    
    
@app.route('/followers')
def followers():
    username=collection.find_one({"username": session.get('current_user')})
    username['_id']=str(username['_id'])
    # return username['followers']
    session['followers']=username['followers']
    return redirect(url_for("follower_list"))
    
@app.route('/follower_list')
def follower_list():
    return render_template("follower_list.html",followers=session.get('followers'))


@app.route("/group_chat")
def groupchat():
    return render_template("group_chat.html")

@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

@socketio.on('custom_event')
def handle_custom_event():
    emit('response', {'data': 'Received your data!'})

@socketio.on('connect')
def handle_connect():
    emit('server_message', {'message': f"{session.get('current_user', 'A user')} joined"}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    emit('server_message', {'message': f"{session.get('current_user', 'A user')} left"}, broadcast=True)

   
    

def main():
    socketio.run(app, debug=True, port=5000)

main()
