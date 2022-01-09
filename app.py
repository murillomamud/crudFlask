from os import read
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/firstapp'


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))

    def to_json(self):
        return{"id": self.id, "name": self.name, "email": self.email}

#Select all

@app.route("/users", methods=["GET"])
def selectUsers():
    usersObj = User.query.all()
    usersJson = [ user.to_json() for user in usersObj]

    return responseGenerator(200, "users", usersJson)

#select single
@app.route("/user/<id>", methods=["GET"])
def selectSingleUser(id):
    try:
        userObj = readUserFromDb(id)
        userJson = userObj.to_json()
        return responseGenerator(200, "user", userJson)
    except Exception as e:
        print(e)
        return responseGenerator(400, "user", {}, 'Error getting user')        

    


#create user
@app.route("/user", methods=["POST"])
def userCreate():
    body = request.get_json()
    #validate parameters - do it later
    try:
        user = User(name=body["name"], email=body["email"])
        db.session.add(user)
        db.session.commit()
        return responseGenerator(201, "user", user.to_json(), "Successfully Created")
    except Exception as e:
        print(e)
        return responseGenerator(400, "user", {}, "Error Creating User")


#update user
@app.route("/user/<id>", methods=["PUT"])
def userUpdate(id):
    body = request.get_json()

    try:
        userObj = readUserFromDb(id)
        if('name' in body):
            userObj.name = body["name"]
        
        if('email' in body):
            userObj.email = body["email"]
        
        db.session.add(userObj)
        db.session.commit()
        return responseGenerator(200, "user", userObj.to_json(), "Successfully Updated")
    except Exception as e:
        print(e)
        return responseGenerator(400, "user", {}, "Error Updating User")        


#delete user
@app.route("/user/<id>", methods=["DELETE"])
def userDelete(id):    

    try:
        userObj = readUserFromDb(id)
        db.session.delete(userObj)
        db.session.commit()
        return responseGenerator(200, "user", userObj.to_json(), "Successfully Deleted")
    except Exception as e:
        print(e)
        return responseGenerator(400, "user", {}, "Error Deleting User")          



def responseGenerator(status, contentName, content, message=False):
    body = {}
    body[contentName] = content

    if(message):
        body["message"] = message

    return Response(json.dumps(body), status=status, mimetype="application/json")


def readUserFromDb(id):    
    user = User.query.filter_by(id=id).first()
    if(user == None):
        raise Exception(json.loads('{"msg":"No User Found"}'))
    print(user)
    return user

app.run(debug=True)    
