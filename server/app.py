# app.py
#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):

        json = request.get_json()

        if "username" in json:

            user = User(
                username=json['username'],
            )

            if "image_url" in json:
                user.image_url = json["image_url"]

            if "bio" in json:
                user.bio = json["bio"]

            if "password" in json:
                user.password_hash = json['password']

        try:
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id

            user_dict = {
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio,
                "id": user.id
            }

            return user_dict, 201                
        
        except:

            error = {"error": "invalid input"}
            return error, 422


class CheckSession(Resource):
                
    def get(self):

        if "user_id" in session and session["user_id"]:

            user = User.query.filter(User.id == session["user_id"]).first()

            if user:
                return user.to_dict(), 200
            else:
                return {"error": "user not found"}, 404
        
        else:
            return {}, 401


class Login(Resource):
    
    def post(self):

        json = request.get_json()

        username = json['username']
        password = json['password']
        user = User.query.filter(User.username == username).first()
        if user:
            if user.authenticate(password):
                session["user_id"] = user.id
                print(session["user_id"])
                return user.to_dict(), 200
            else:
                return {"error":"unauthorized"}, 401
        else: 
            return {"error":"username doesn't exist in database"}, 401 
        
       

class Logout(Resource):
    
    def delete(self):
            
        if "user_id" in session and session["user_id"]:

            session["user_id"] = None
            return {}, 204
        
        else:
            return {
                    "error": "user not logged in"
                }, 401
        
class RecipeIndex(Resource):
    
    def get(self):

        if "user_id" in session and session["user_id"]:

            user = User.query.filter(User.id == session["user_id"]).first() 

            recipes = Recipe.query.filter(Recipe.user == user).all()

            response = {
                "user": {
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio
                },
                "recipes": [
                    {
                        "title": recipe.title,
                        "instructions": recipe.instructions,
                        "minutes_to_complete": recipe.minutes_to_complete,
                    }
                    for recipe in recipes
                ]
            }

            return response, 200
        else: 
            return {
                "error": "user not logged in"
            }, 401

        
    def post(self):

        # if "user_id" in session and session["user_id"]:

        json = request.get_json()

        try:

            recipe = Recipe(
            title=json["title"],
            minutes_to_complete=json["minutes_to_complete"],
            instructions=json["instructions"],
            user_id=session["user_id"]
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(), 201
        
        except IntegrityError: 
            return {
                "error": "Unprocessable Entity"
                }, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)