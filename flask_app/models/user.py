from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import recipe
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    db_name = 'recipes_db'

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.recipes = []
        self.liked_recipes = []

    # Create
    @classmethod
    def create(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES(%(first_name)s, %(last_name)s, %(email)s, %(password)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)

    # Read
    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s"
        result = connectToMySQL(cls.db_name).query_db(query, data)
        return cls(result[0])

    @classmethod
    def get_by_email(cls, data):
        query = "SELECT *  FROM users WHERE email = %(email)s;"
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod
    def get_all_emails(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.db_name).query_db(query)
        all_emails = []
        for entry in results:
            all_emails.append(entry['email'])
        return all_emails

    @classmethod
    def get_user_with_recipes(cls, data):
        query = "SELECT * FROM users LEFT JOIN recipes ON recipes.users_id = users.id WHERE users.id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        user = cls(results[0])
        for row in results:
            recipe_data = {
                "id" : row['recipes.id'],
                "name" : row['name'],
                "under_30" : row['under_30'],
                "description" : row['description'],
                "instructions" : row['instructions'],
                "date_made": row['date_made'],
                "created_at" : row['recipes.created_at'],
                "updated_at" : row['recipes.updated_at']
            }
            user.recipes.append(recipe.Recipe(recipe_data))
        return user
    
    @classmethod
    def get_user_with_liked_recipes(cls, data):
        query = "SELECT * FROM users LEFT JOIN likes ON likes.users_id = users.id LEFT JOIN recipes ON recipes.id = likes.recipes_id WHERE users.id = %(id)s"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        user = cls(results[0])

        # check that there is at least 1 like
        if results[0]['likes.id'] != None:
            for row in results:
                recipe_data = {
                    "id" : row['recipes.id'],
                    "name" : row['name'],
                    "under_30" : row['under_30'],
                    "description" : row['description'],
                    "instructions" : row['instructions'],
                    "date_made": row['date_made'],
                    "created_at" : row['recipes.created_at'],
                    "updated_at" : row['recipes.updated_at']
                }
                user.liked_recipes.append(recipe.Recipe(recipe_data))
            return user
        else:
            return user


    # Validate
    @staticmethod
    def validate_registration(user, used_emails):
        is_valid = True

        if len(user['first_name']) < 2:
            flash("First Name must be at least 2 characters and contain only letters.", "registration_error")
            is_valid = False
        if len(user['last_name']) < 2:
            flash("Last Name must be at least 2 characters and contain only letters.", "registration_error")
            is_valid = False
        if not EMAIL_REGEX.match(user['email']):
            flash("Invalid Email Address.", "registration_error")
            is_valid = False
        if user['email'] in used_emails:
            flash("Email already in use.", "registration_error")
            is_valid = False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters.", "registration_error")
            is_valid = False
        if user['password'] != user['confirm_password']:
            flash("Passwords did not match.", "registration_error")
            is_valid = False

        # Checking password complexity    
        password_secure = False
        for x in user['password']:
            if x.isupper():
                password_secure = True
            if x.isdigit():
                password_secure = True
        if not password_secure:
            flash("Password must contain at least one uppercase letter and number.", "registration_error")
            is_valid = False

        return is_valid