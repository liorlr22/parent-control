import pymongo
from flask import Flask, render_template, request, redirect, url_for, make_response
import bcrypt

client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["users"]
collection = mydb['parents-control']

app = Flask(__name__)


# function to delete one element from db
def delete(data):
    collection.delete_one(data)


# function to insert one element to db
def insert(data):
    collection.insert_one(data)


# function to insert multiple elements to db
def insertMany(data):
    collection.insert_many(data)


# function to update certain element in db
def update(old, new):
    collection.update_one(old, new)


# function to find element in db and return it
def find(data):
    return collection.find_one(data)


# home page
@app.route("/")
def index():
    return render_template("index.html")


# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # get the username and the password that were inputted in the form
        username = request.form["username"]
        password = request.form["password"]

        # find the user based on his inputs, returns true if it finds. false if not
        user = find({"username": username})

        # if the user is found and the password is correct, redirect him to the dashboard
        if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            return redirect(url_for("dashboard", username=username))

        return "Incorrect username or password"

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # get the username and the password that were inputted in the form
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        # find the user based on his inputs, returns true if it finds. false if not
        user = find({"username": username})
        if user:
            return "User already exists"

        # encrypt the password using the salt
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        insert({"username": username, "password": hashed_password.decode(), "role": role})

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/dashboard/<username>")
def dashboard(username):
    data = collection.find_one({"username": username}, {"role": 1, "_id": 0})
    role = list(data.values())[0]
    if role == "parent":
        return "hello parent"
    elif role == "child":
        return "hello child"
    else:
        return "hi admin"


if __name__ == "__main__":
    app.run(debug=True)
