from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user import User
from flask_app.models.recipe import Recipe
import datetime

@app.route('/dashboard')
def dashboard_page():
    # check for login
    if 'user_id' not in session:
        return redirect('/user/logout')

    data = {
            "id": session['user_id']
        }
    user = User.get_user_with_recipes(data)
    return render_template('dashboard.html', user=user)
    
@app.route('/recipes/new')
def new_recipe_page():
    # check for login
    if 'user_id' not in session:
        return redirect('/user/logout')

    return render_template('add_recipe.html', user_id=session['user_id'])

@app.route('/recipes/new/save', methods=['POST'])
def save_recipe():
    # check for login
    if 'user_id' not in session:
        return redirect('/user/logout')
    
    if not Recipe.validate_recipe(request.form):
        return redirect(f'/recipes/new')

    data = {
        "users_id": session['user_id'],
        "name": request.form["name"],
        "description": request.form["description"],
        "instructions": request.form["instructions"],
        "date_made": request.form["date_made"],
        "under_30": request.form["under_30"]
    }
    Recipe.create(data)
    return redirect('/dashboard')

@app.route('/recipes/delete/<int:id>')
def delete_recipe(id):
    # check for login
    if 'user_id' not in session:
        return redirect('/user/logout')

    data = {
        "id": id
    }
    Recipe.delete(data)
    return redirect('/dashboard')

@app.route('/recipes/edit/<int:id>')
def edit_recipe_page(id):
    # check for login
    if 'user_id' not in session:
        return redirect('/user/logout')

    data = {
        "id": id
    }
    recipe = Recipe.get_by_id(data)
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/recipes/edit/<int:id>/save', methods=['POST'])
def save_edit(id):
    # check for login
    if 'user_id' not in session:
        return redirect('/user/logout')
    
    if not Recipe.validate_recipe(request.form):
        return redirect(f'/recipes/edit/{id}')

    data = {
        "id": id,
        "users_id": session['user_id'],
        "name": request.form["name"],
        "description": request.form["description"],
        "instructions": request.form["instructions"],
        "date_made": request.form["date_made"],
        "under_30": request.form["under_30"]
    }

    Recipe.update(data)
    return redirect('/dashboard')

@app.route('/recipes/<int:id>')
def recipe_details_page(id):
    # check for login
    if 'user_id' not in session:
        return redirect('/user/logout')

    recipe = Recipe.get_by_id({"id" : id})
    recipe.date_made = recipe.date_made.strftime("%B %d %Y")
    return render_template('recipe.html', recipe=recipe)

@app.route('/recipes/all')
def all_recipes_page():
    # check for login
    if 'user_id' not in session:
        return redirect('/user/logout')

    # get likes per recipe
    all_recipes = Recipe.get_all()
    recipes = []
    for recipe in all_recipes:
        data = {
            "id": recipe.id
        }
        recipes.append(Recipe.get_recipe_with_likes(data))

    # get all recipes liked by user -- for validating that users only like recipes once
    user = User.get_user_with_liked_recipes(data = {"id": session['user_id']})

    # get recipe ids the user has liked
    liked_recipes = []
    for recipe in user.liked_recipes:
        liked_recipes.append(recipe.id)

    return render_template('all_recipes.html', recipes=recipes, liked_recipes=liked_recipes)

@app.route('/recipes/<int:id>/like')
def like_recipe(id):
    # check for login
    if 'user_id' not in session:
        return redirect('/user/logout')

    data = {
        "users_id": session['user_id'],
        "recipes_id": id
    }
    Recipe.add_like(data)
    return redirect('/recipes/all')

@app.route('/recipes/<int:id>/unlike')
def unlike_recipe(id):
    # check for login
    if 'user_id' not in session:
        return redirect('/user/logout')

    data = {
        "users_id": session['user_id'],
        "recipes_id": id
    }
    Recipe.remove_like(data)
    return redirect('/recipes/all')