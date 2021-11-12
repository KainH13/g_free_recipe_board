from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

class Recipe:
    db_name = 'recipes_db'

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.under_30 = data['under_30']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date_made = data['date_made']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.likes = []
        self.num_likes = 0

    # Create
    @classmethod
    def create(cls, data):
        query = "INSERT INTO recipes (name, under_30, description, instructions, date_made, users_id) VALUES(%(name)s, %(under_30)s, %(description)s, %(instructions)s, %(date_made)s, %(users_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod
    def add_like(cls, data):
        query = "INSERT INTO likes (users_id, recipes_id) VALUES(%(users_id)s, %(recipes_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)

    # Read
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM recipes;"
        results = connectToMySQL(cls.db_name).query_db(query)
        recipes = []
        for row in results:
            recipes.append(cls(row))
        return recipes
    
    @classmethod
    def get_by_id(cls, data):
        query = "SELECT * FROM recipes WHERE id = %(id)s;"
        result = connectToMySQL(cls.db_name).query_db(query, data)
        return cls(result[0])

    @classmethod
    def get_recipe_with_likes(cls, data):
        query = "SELECT * FROM recipes LEFT JOIN likes ON recipes_id = recipes.id LEFT JOIN users ON users.id = likes.users_id WHERE recipes.id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        print(results)
        recipe = cls(results[0])
        num_likes = 0

        # check for at least 1 like
        if results[0]['likes.id'] != None:
            for row in results:
                user_data = {
                    "id" : row["users.id"],
                    "first_name" : row["first_name"],
                    "last_name" : row["last_name"],
                    "email" : row["email"],
                    "password" : row["password"],
                    "created_at" : row["users.created_at"],
                    "updated_at" : row["users.updated_at"],
                }
                recipe.likes.append(user.User(user_data))
                num_likes += 1
            recipe.num_likes = num_likes
            return recipe
        else:
            return recipe

    # Update
    @classmethod
    def update(cls, data):
        query = "UPDATE recipes SET name = %(name)s, under_30 = %(under_30)s, description = %(description)s, instructions = %(instructions)s, date_made = %(date_made)s WHERE recipes.id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)

    # Delete
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM recipes WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod
    def remove_like(cls, data):
        query = "DELETE FROM likes WHERE users_id = %(users_id)s AND recipes_id = %(recipes_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)

    # Validate
    @staticmethod
    def validate_recipe(data):
        is_valid = True
        
        if len(data['name']) < 3 or len(data['description']) < 3 or len(data['instructions']) < 3:
            flash("Name, description, and instructions must be longer than 3 characters", "recipe")
            is_valid = False
        if 'date_made' not in data or 'under_30' not in data:
            flash("Date Made and Under 30 Minutes? must be filled out.", "recipe")
            is_valid = False
        
        return is_valid