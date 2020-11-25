from unittest import TestCase

from app import app
from models import db, User, Post


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
            self.assertIn('>Test User2</a></li>', html)

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
        with app.test_client() as client:
            resp = client.post(
                f"/posts/{self.post_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(self.post.title, html)
