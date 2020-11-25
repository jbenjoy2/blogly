from unittest import TestCase

from app import app
from models import db, User, Post, Tag, PostTag


# use test database and dont clutter tests with sql
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# make flask errors real errors instead of html error pages
app.config['TESTING'] = True

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class UserViewsTestCase(TestCase):
    """Tests for views for Users routes."""

    def setUp(self):
        """add sample pet."""
        Post.query.delete()
        User.query.delete()
        Tag.query.delete()

        user = User(first_name="Test", last_name="User",
                    image_url='https://www.freeiconspng.com/uploads/person-icon-user-person-man-icon-4.png')

        db.session.add(user)
        db.session.commit()

        self.user_id = user.id
        self.user = user

        post = Post(title="Testpost", content="this is a test post",
                    user_id=user.id)

        db.session.add(post)
        db.session.commit()

        self.post_id = post.id
        self.post = post

        tag = Tag(name='TestTag')
        db.session.add(tag)
        db.session.commit()

        self.tag_id = tag.id
        self.tag = tag

    def tearDown(self):
        """Clean up fouled session"""
        db.session.rollback()

    def test_show_users(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Users</h1>', html)

    def test_show_user(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Test User</h1>', html)
            self.assertIn(self.user.image_url, html)

    def test_add_user(self):
        with app.test_client() as client:
            d = {"first_name": "Test", "last_name": "User2",
                 "image": "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"}

            resp = client.post('/users/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Test User2</h1>', html)

    def test_delete_user(self):
        with app.test_client() as client:
            resp = client.post(
                f"/users/{self.user_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(self.user.full_name, html)

    def test_show_homepage(self):
        """test to make sure recent posts show up on home page, and that home page is active"""
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Recent Posts</h1>', html)
            self.assertIn('<li class="nav-item home active">', html)

    def test_posts_route(self):
        with app.test_client() as client:
            resp = client.get('/posts')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">All Posts</h1>', html)

    def test_show_post_details(self):
        """test to make sure post details show up as expected"""
        with app.test_client() as client:
            resp = client.get(f"/posts/{self.post_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1>{self.post.title}</h1>', html)
            self.assertIn(
                f'<i>By <a href="/users/{self.post.user_id}">{self.post.user.full_name}', html)

    def test_add_new_post(self):
        """test to make sure a form to add new post gets submitted properly"""
        with app.test_client() as client:
            d = {"title": "Testpost2", "content": "test case for adding a new post",
                 "user_id": self.user_id}
            resp = client.post(
                f'/users/{self.user_id}/posts/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f'Testpost2</a>', html)

    def test_delete_post(self):
        """test to make sure deleting post occurs as expected"""
        with app.test_client() as client:
            resp = client.post(
                f"/posts/{self.post_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(self.post.title, html)

    def test_show_tags(self):
        """test rendering of all tags page"""
        with app.test_client() as client:
            resp = client.get("/tags")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">All Tags</h1>', html)

    def test_show_tag_details(self):
        """test rendering of tag details page"""
        with app.test_client() as client:
            resp = client.get(f'/tags/{self.tag_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1>{self.tag.name}</h1>', html)

    def test_show_add_tag(self):
        """test rendering of form to add a new tag, including post checkboxes"""
        with app.test_client() as client:
            resp = client.get('/tags/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<input type="text" class="form-control" id="name" name="name" placeholder="Enter a name for the tag" required>', html)
            self.assertIn(
                f'<label class="form-check-label" for="post_{ self.post_id }">{self.post.title}</label>', html)

    def test_add_tag(self):
        """test submission of tag addition"""
        with app.test_client() as client:
            d = {"name": "tag2"}
            resp = client.post(f"/tags/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<span class="badge badge-primary badge-pill">tag2</span>', html)

    def test_show_edit_tag(self):
        """test rendering of form to edit a tag"""
        with app.test_client() as client:
            resp = client.get(f'/tags/{self.tag_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f'<input type="text" class="form-control" id="name" name="name" value="{self.tag.name}" required>', html)

    def test_delete_tag(self):
        """test deletion of tag, and make sure alert renders"""
        with app.test_client() as client:
            resp = client.post(
                f'tags/{self.tag_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('There are currently no tags in use', html)
            self.assertNotIn(self.tag.name, html)
