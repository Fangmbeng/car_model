from flask import Blueprint, request, jsonify
from app.models import db, Post
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
        return redirect(url_for('get_post', post_id=post.id))
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