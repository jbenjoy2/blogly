"""Blogly application."""

from flask import Flask, redirect, render_template, flash, request
from models import db, connect_db, User, Post, DEFAULT_IMG_URL
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

# routes


@app.route('/')
def show_root():
    """root which redirects to users"""
    return redirect('/users')


@app.route('/users')
def show_users():
    """show all users, ordered by last_name, first_name"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('/users/users.html', users=users)


@app.route('/users/new')
def show_add_user():
    """render html for the add_user form"""
    return render_template('/users/add.html')


@app.route('/users/new', methods=['POST'])
def submit_add_form():
    """handle form submission for new user"""
    new_user = User(first_name=request.form['first_name'],
                    last_name=request.form['last_name'], image_url=request.form['image'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:user_id>')
def user_details(user_id):
    """render details page for a given user"""
    user = User.query.get_or_404(user_id)
    return render_template('/users/details.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['GET'])
def edit_user_form(user_id):
    """render form to edit a user's info"""
    user = User.query.get_or_404(user_id)
    return render_template('/users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['POST'])
def edit_user(user_id):
    """handle form submission for edited user"""
    user = User.query.get_or_404(user_id)

    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image'] or DEFAULT_IMG_URL

    db.session.add(user)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """handle delete of user"""
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect('/users')

# **************PART 2 ADDITIONS********************


@app.route('/users/<int:user_id>/posts/new')
def show_new_post_form(user_id):

    user = User.query.get_or_404(user_id)
    return render_template('/posts/new.html', user=user)


@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def submit_new_post_form(user_id):

    user = User.query.get_or_404(user_id)

    new_post = Post(title=request.form['title'],
                    content=request.form['content'], user=user)

    db.session.add(new_post)
    db.session.commit()

    return redirect(f'/users/{user_id}')
