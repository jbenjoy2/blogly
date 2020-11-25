"""Blogly application."""

from flask import Flask, redirect, render_template, flash, request
from models import db, connect_db, User, Post, DEFAULT_IMG_URL, Tag, PostTag
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

# routes


@app.route('/')
def show_root():
    """root , shows 5 most recent posts"""
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    return render_template('index.html', posts=posts, homeactive='active')


@app.route('/users')
def show_users():
    """show all users, ordered by last_name, first_name"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users.html', users=users, usersactive='active')


@app.route('/users/new')
def show_add_user():
    """render html for the add_user form"""
    return render_template('adduser.html')


@app.route('/users/new', methods=['POST'])
def submit_add_form():
    """handle form submission for new user"""
    new_user = User(first_name=request.form['first_name'],
                    last_name=request.form['last_name'], image_url=request.form['image'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect(f'/users/{new_user.id}')


@app.route('/users/<int:user_id>')
def user_details(user_id):
    """render details page for a given user"""
    user = User.query.get_or_404(user_id)
    return render_template('userdetails.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['GET'])
def edit_user_form(user_id):
    """render form to edit a user's info"""
    user = User.query.get_or_404(user_id)
    return render_template('edituser.html', user=user)


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

    tags = Tag.query.order_by(Tag.id).all()
    user = User.query.get_or_404(user_id)

    return render_template('newpost.html', user=user, tags=tags)


@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def submit_new_post_form(user_id):

    user = User.query.get_or_404(user_id)

    ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(ids)).all()

    new_post = Post(title=request.form['title'],
                    content=request.form['content'], user=user, tags=tags)

    db.session.add(new_post)
    db.session.commit()

    return redirect(f'/users/{user_id}')


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.order_by(Tag.id).all()

    return render_template('postdetails.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.order_by(Tag.id).all()

    return render_template('editpost.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def submit_edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    post.title = request.form['title']
    post.content = request.form['content']

    ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(ids)).all()

    post.tags = tags

    db.session.add(post)
    db.session.commit()

    return redirect(f'/posts/{post_id}')


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect(f'/users/{post.user_id}')


@app.route('/posts')
def show_all_posts():
    posts = Post.query.order_by(Post.created_at).all()

    return render_template('posts.html', posts=posts, postactive='active')

# FURTHER STUDY- CUSTOM 404


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# tags routes
@app.route('/tags')
def show_tags():
    """return the page with all of the tags"""
    tags = Tag.query.order_by(Tag.id).all()
    return render_template('tags.html', tags=tags, tagsactive='active')


@app.route('/tags/new')
def new_tag_form():
    """render form to create a new tag"""

    posts = Post.query.order_by(Post.created_at).all()
    return render_template('newtag.html', posts=posts)


@app.route('/tags/new', methods=['POST'])
def add_the_tag():
    ids = [int(num) for num in request.form.getlist('posts')]
    posts = Post.query.filter(Post.id.in_(ids)).all()
    new_tag = Tag(name=request.form['name'], posts=posts)

    db.session.add(new_tag)
    db.session.commit()

    return redirect('/tags')


@app.route('/tags/<int:tag_id>')
def tag_info(tag_id):
    """show specific tag details"""
    tag = Tag.query.get_or_404(tag_id)

    return render_template('tagdetails.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def edit_tag(tag_id):
    """render form to edit the tag"""
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.order_by(Post.created_at).all()

    return render_template('edittag.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def submit_tag_edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    ids = [int(num) for num in request.form.getlist('posts')]
    posts = Post.query.filter(Post.id.in_(ids)).all()

    tag.name = request.form['name']

    tag.posts = posts
    db.session.add(tag)
    db.session.commit()

    return redirect('/tags')


@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    db.session.delete(tag)
    db.session.commit()

    return redirect('/tags')
