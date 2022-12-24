import os
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from algorithm import *
import json
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

db = SQLAlchemy(app)

recipes = pd.read_csv('./data/recipes10000.csv')
reviews = pd.read_csv('./data/reviews10000.csv', usecols=["AuthorId", "RecipeId", "Rating"])
liked = [192]
disliked = []

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<User {self.firstname}>'


class Recipe(db.Model):
    Calories = db.Column(db.Float, nullable=True)
    CarbohydrateContent = db.Column(db.Float, nullable=True)
    CholesterolContent = db.Column(db.Float, nullable=True)
    FatContent = db.Column(db.Float, nullable=True)
    FiberContent = db.Column(db.Float, nullable=True)
    Images = db.Column(db.String(100), nullable=True)
    ProteinContent = db.Column(db.String(100), nullable=True)
    RecipeInstructions = db.Column(db.String(500), nullable=True)
    RecipeServings = db.Column(db.Integer, nullable=True)
    SaturatedFatContent = db.Column(db.Float, nullable=True)
    SodiumContent = db.Column(db.Float, nullable=True)
    SugarContent = db.Column(db.Float, nullable=True)
    TotalTime = db.Column(db.String(10), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(256), nullable=False)
    # user_id = db.Column(db.Integer)

@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/register', methods=["POST"])
@cross_origin()
def hello_world():  # put application's code here
    firstname = request.json["firstname"]
    lastname = request.json["lastname"]
    email = request.json["email"]
    password = request.json["password"]

    user = User(firstname=firstname, lastname=lastname,
                email=email, password=password)
    db.session.add(user)
    db.session.commit()

    last_id = User.query.order_by(User.id.desc()).first().id

    return {
        "index" : last_id,
        "message" : "Success"
    }, 200


@app.route('/profile/<int:index>/', methods=["GET"])
@cross_origin()
def profile(index):
    if request.method == "GET":

        user = User.query.filter_by(id=index).first()

        return {
            "firstname" : user.firstname,
            "lastname" : user.lastname,
            "email" : user.email
        }

@app.route('/recommendation', methods=["POST"])
@cross_origin()
def get_recommendation():
    if request.method == "POST":
        Calories = request.json["Calories"]
        CarbohydrateContent = request.json["CarbohydrateContent"]
        CholesterolContent = request.json["CholesterolContent"]
        FatContent = request.json["FatContent"]
        FiberContent = request.json["FiberContent"]
        Images = request.json["Images"]
        ProteinContent = request.json["ProteinContent"]
        RecipeInstructions = request.json["RecipeInstructions"]
        RecipeServings = request.json["RecipeServings"]
        SaturatedFatContent = request.json["SaturatedFatContent"]
        SodiumContent = request.json["SodiumContent"]
        SugarContent = request.json["SugarContent"]
        TotalTime = request.json["TotalTime"]
        id = request.json["RecipeId"]
        name = request.json["Name"]
        ingredients = request.json["RecipeIngredientParts"]


        recipe = Recipe(Calories=Calories, CarbohydrateContent=CarbohydrateContent,
                    CholesterolContent=CholesterolContent, FatContent=FatContent, FiberContent=FiberContent,
                    Images=Images, ProteinContent=ProteinContent, RecipeInstructions=RecipeInstructions,
                    RecipeServings=RecipeServings, SaturatedFatContent=SaturatedFatContent,
                    SodiumContent=SodiumContent, SugarContent=SugarContent,
                    TotalTime=TotalTime, id=id, name=name, ingredients=ingredients)
        db.session.add(recipe)
        db.session.commit()

        return {
                   "id": id,
                   "message": "Success"
               }, 200

@app.route('/recommendation/<int:index>/<int:likedf>/', methods=["GET"])
@cross_origin()
def recommendation(index, likedf):
    if likedf == 1:
        liked.append(index)
    elif likedf == 0:
        disliked.append(index)

    if request.method == "GET":
        recom = recommend(recipes, reviews, liked, disliked)
        print(liked, disliked)
        return json.loads(recipes[recipes['RecipeId'] == recom].to_json(orient="records"))


@app.route('/signin', methods=["GET"])
@cross_origin()
def signin():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()
    if user is None:
        return {
            "message" : "No such user!"
        }, 404
    elif user.password != password:
        return {
            "message" : "Wrong password!"
        }, 400
    else:
        return {
            "message" : "Sing in!"
        }, 200


if __name__ == '__main__':
    app.run()
