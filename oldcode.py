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





if __name__ == '__main__':
    app.run(debug=True,port=3001)
