# IMPORTS 
from flask import Flask, request, jsonify, render_template, redirect, url_for, session,render_template_string
from pymongo import MongoClient
import pyotp
from flask_mail import Mail, Message
import socket

# Get the IP address of the SMTP server (optional)
socket.gethostbyname('smtp.gmail.com')

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
    MAIL_PASSWORD = "your secret app code"  # Make sure to set this in environment variables or secure config
)
mail = Mail(app)

app.secret_key = 'secretkeyforsession'

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
        user_post = request.form['post']
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

def main():
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()
