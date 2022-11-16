"""User view tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from flask_bcrypt import Bcrypt

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserViewsTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
    
    def test_user_create_fail(self):
        """Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail? """
        # password too short
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdf",
                    'image_url':User.image_url.default.arg})
        html=res.get_data(as_text=True)
        self.assertEqual(res.status_code,200)
        self.assertIn("Sign me up!",html)
        
        # username taken
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdf",
                    'image_url':User.image_url.default.arg})
        html=res.get_data(as_text=True)

        self.assertIn("Sign me up!",html)
        
         # no email taken
        res=self.client.post('/signup',data={'username':"test",
                    'password':"asdf",
                    'image_url':User.image_url.default.arg})
        html=res.get_data(as_text=True)

        self.assertIn("Sign me up!",html)
        
    def test_user_create_success(self):
        res=self.client.post('/signup',data={'username':"test22",
                    'email':"test22@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg})
        html=res.get_data(as_text=True)
        self.assertEqual(res.status_code,200)
        self.assertIn("@test22",html)