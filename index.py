import pymongo
from flask import Flask, render_template, request, redirect, url_for, make_response, session, jsonify
import bcrypt
from flask_mail import Message
from flask_mail import Mail

client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["users"]
collection = mydb['parents-control']

app = Flask(__name__)
app.secret_key = 'secret_key'


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
        session['username'] = request.form["username"]
        password = request.form["password"]

        # find the user based on his inputs, returns true if it finds. false if not
        user = find({"username": session['username']})

        # if the user is found and the password is correct, redirect him to the dashboard
        if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            return redirect(url_for("dashboard", username=session['username']))
        else:
            error_message = "Incorrect username or password"
            return render_template("login.html", error_message=error_message)

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # get the username and the password that were inputted in the form
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        # find the user based on his inputs, returns true if it finds. false if not
        user = find({"username": username})
        if user:
            error_message = "User already exists"
            return render_template("signup.html", error_message=error_message)

        # encrypt the password using the salt
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        insert(
            {"email": email, "username": username, "password": hashed_password.decode(), "role": role})

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route("/dashboard/<username>")
def dashboard(username):
    if username != session.get('username'):
        return redirect(url_for('login'))

    data = collection.find_one({"username": username}, {"role": 1, "_id": 0})
    role = list(data.values())[0]
    return f"hello {role}"


@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    return "hello world"

@app.route("/home")
def toHome():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
