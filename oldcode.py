

from flask import Flask, request, jsonify,render_template
from pymongo import MongoClient

app = Flask(__name__)

# kind of usermodel.js file

client = MongoClient('mongodb://localhost:27017/')
db = client['flask-db'] #this is db name (which will be shown in mongo db compass )
collection = db['users'] #this is schema name



#main code starts from here

@app.route('/')
def home():
    return render_template("form.html")

#to accept dynamic routes

@app.route("/<name>")
def random(name):
    return f"hello {name}"

#to check if user exists or nto

@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        user_name = request.form.get("name") 
        password= request.form.get("message")
        username=request.form["name"]
        password=request.form["password"]  
        print(f"username is {user_name} and message is {password}")
       
        inuser = collection.find_one({"name": user_name})
        
        if inuser:
                return "name already exist"
        
        user={
                "name":user_name,
            }
        result = collection.insert_one(user)
        if result:
            return "submitted"
        
        
    
# @app.route('/',methods=["GET","POST"])
# def front():
#     if request.method=="POST":
#         username=request.form["username"]
#         password=request.form["password"]
#         if username=="ash" and password=="a":
#             return render_template("dash.html")
#         else:
#             return render_template("error.html")
    
#     else:
#         return render_template("front.html")
        
#to accept form data

@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        user = request.form.get("name")  
        password= request.form.get("password")  
        if user:
            return render_template("contact.html",user=user,password=password)
        else:
            print("No 'naam' field in form data.")
    return "Form submission received!"


#to add data in mongodb  (create)
@app.route("/add") 
def add_user():
    user = {'name': 'zara'}
    result = collection.insert_one(user)
    return f"User added with id: {result.inserted_id}"


#to read (read)
@app.route("/show")
def show():
    allusers=collection.find()
    list=[]
    for i in allusers:
        list.append(i['name'])
        list.append(i['message'])
    return list

#to find 
@app.route("/find")
def find():
    user = collection.find_one({"name": "Ashraf Ali"})
    user['_id']=str(user['_id'])
    return jsonify(user)  

#to delete 

@app.route('/delete')
def delOne():
    delete=collection.delete_one({"name":"Ashraf Ali"})
    return "deleted"




# to update

@app.route("/update")
def update():
    collection.update_one({"name":"ashraf"},{"$set":{"name":"zara"}})
    return "updated"




#to link one button to another page

@app.route("/link")
def link():  #both function name and link name should be same
    return "you are on link page"


#  <a href="{{url_for('link')}}">click here</a>  (in html)


for loop in python

 {% for keys,values in  result.items() %}
        <h1>{{keys}}</h1>
        <h1>{{values}}</h1>
        
    {% endfor %}

     {% print("hellow orld") %}
    {# print("hellow orld") #}


     return render_template("delimeter.html",result=dict)



# AUTHENTICATION AND SETUP

#BCRYPT

from flask_bcrypt import Bcrypt

bcrypt=Bcrypt(app)
password="mypass"
hashed_password=bcrypt.generate_password_hash(password).decode('utf-8')
print(hashed_password)
print(bcrypt.check_password_hash(hashed_password,password))



#json web token

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

# Set the secret key to sign the JWTs
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure key in production
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # Validate credentials (for demonstration purposes, these are hardcoded)
    if username == 'user' and password == 'password':
        # Create an access token that contains the identity of the user
        access_token = create_access_token(identity={'username': username})
        return jsonify(access_token=access_token)
    
    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Access the identity of the current user
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200






#set cookie
from flask import Flask,Response,make_response,request

@app.route("/set")
def setcookie():
    resp = make_response("cookieset")
    resp.set_cookie('cookie-name', 'cookie-value')
    return resp


#take cookie
  username = request.cookies.get('cookie-name')
    return f'The username is {cookie-value}'
    
    #delete cookie
  resp=make_response("cookie_deleted")
    resp.delete_cookie("cookie-name")
    return resp








if __name__ == '__main__':
    app.run(debug=True,port=3001)
