from flask import Blueprint, request, jsonify
from app.models import db, Post, User
from forms import PostForm
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user


api = Blueprint('api',__name__, url_prefix='/api')


@api.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        # Get data from form
        brand = form.brand.data
        model = form.model.data
        # Create new post instance which will also add to db
        new_post = Post(brand=brand, model=model, user_id=current_user.id)
        flash(f"{new_post.brand} has been created", "success")
        return redirect(url_for('site.index'))
        
    return render_template('create.html', form=form)

@api.route('/posts/<int:post_id>')
@login_required
def get_post(post_id):
    # post = Post.query.get_or_404(post_id)
    post = Post.query.get(post_id)
    if not post:
        flash(f"A post with id {post_id} does not exist", "danger")
        return redirect(url_for('site.index'))
    return render_template('post.html', post=post)


@api.route('/posts/<post_id>/edit', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        flash(f"A post with id {post_id} does not exist", "danger")
        return redirect(url_for('site.index'))
    # Make sure the post author is the current user
    if post.author != current_user:
        flash("You do not have permission to edit this post", "danger")
        return redirect(url_for('site.index'))
    form = PostForm()
    if form.validate_on_submit():
        # Get the form data
        brand = form.brand.data
        model = form.model.data
        # update the post using the .update method
        post.update(brand=brand, model=model)
        flash(f"{post.brand} has been updated!", "success")
        return redirect(url_for('api.get_post', post_id=post.id))
    if request.method == 'GET':
        form.brand.data = post.brand
        form.model.data = post.model
    return render_template('edit_post.html', post=post, form=form)

# DELETE car ENDPOINT

@api.route('/posts/<post_id>/delete')
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        flash(f"A post with id {post_id} does not exist", "danger")
        return redirect(url_for('site.index'))
    # Make sure the post author is the current user
    if post.author != current_user:
        flash("You do not have permission to delete this post", "danger")
        return redirect(url_for('site.index'))
    post.delete()
    flash(f"{post.brand} has been deleted", "info")
    return redirect(url_for('site.index'))

#routes for JSON request
from app.blueprints.authentication.auth import basic_auth, token_auth


@api.route('/token')
@basic_auth.login_required
def index_():
    user = basic_auth.current_user()
    token = user.get_token()
    return {'token':token, 'token_expiration':user.token_expiration}

@api.route('/posts', methods=['GET'])
def getposts():
    posts = Post.query.all()
    return jsonify([p.to_dict() for p in posts])

@api.route('/post/<int:post_id>')
def getpost(post_id):
    posts = Post.query.get(post_id)
    return posts.to_dict()

@api.route('/posts', methods=['POST'])
@token_auth.login_required
def createpost():
    if not request.is_json:
        return("your request content-type is not JSON"), 400
    data=request.json
    for field in ["brand", "model"]:
        if field not in data:
            return(f"error:{field} must be in request body"), 400
    brand = data.get("brand")
    model = data.get("model")
    user = token_auth.current_user()
    new_post = Post(brand=brand, model=model, user_id=user.id)
    return new_post.to_dict(), 201
    

@api.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    return user.to_dict()

@api.route('/users', methods=['POST'])
def createuser():
    if not request.is_json:
        return("your request content-type is not JSON"), 400
    data=request.json
    for field in ['email', 'username', 'password']:
        if field not in data:
            return("error:f{field} must be in request body"), 400
    email = data.get('email')
    username = data.get("username")
    password = data.get('password')
            # Query our user table to see if there are any users with either username or email from form
    check_user = User.query.filter( (User.username == username) | (User.email == email) ).all()
        # If the query comes back with any results
    if check_user:
        return ('A user with that email and/or username already exists.'), 400
    new_user = User(email=email, password=password, username= username)
    return new_user.to_dict(), 201
    
@api.route('/post/edit/<int:post_id>', methods=['POST'])
@token_auth.login_required
def editpost(post_id):
    post = Post.query.get(post_id)
    if not request.is_json:
        return("your request content-type is not JSON"), 400
    data=request.json
    for field in ['brand', 'model']:
        if field not in data:
            return("error:f{field} must be in request body"), 400
    brand = data.get('brand')
    model = data.get("model")
    user =  token_auth.current_user()
    post.update(brand=brand, model=model, user_id=user)
    return post.to_dict(), 201


@api.route('/post/delete/<int:post_id>', methods=['POST'])
@token_auth.login_required
def deletepost(post_id):
    post = Post.query.get(post_id)
    if not request.is_json:
        return("your request content-type is not JSON"), 400
    data=request.json
    for field in ['brand', 'model']:
        if field not in data:
            return("error:f{field} must be in request body"), 400
    post.delete()
    return post.to_dict(), 201