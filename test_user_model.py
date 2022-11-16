"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_is_following_not_detecting(self):
        """Does is_following successfully detect when user1 is following user2?"""
        u = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        
        u2 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u2)
        db.session.commit()
        found=u2.is_following(u)
        self.assertEqual(found,0)
        
    def test_is_following_detecting(self):
        """Does is_following successfully detect when user1 is not following user2?"""
        u = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        
        u2 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u2)
        db.session.commit()
        
        f=Follows(user_being_followed_id=u2.id,user_following_id=u.id)
        db.session.add(f)
        db.session.commit()
        
        found=u.is_following(u2)
        self.assertEqual(found,1)
    
    def test_is_followed_by_detect(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        # testuser2 is added already from test above
        u = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        
        u2 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u2)
        db.session.commit()
        
        f=Follows(user_being_followed_id=u2.id,user_following_id=u.id)
        db.session.add(f)
        db.session.commit()
        
        found=u2.is_followed_by(u)
        self.assertEqual(found,1)
    
    def test_is_followed_by_not_detect(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2? """
        u = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        
        u2 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u2)
        db.session.commit()
        
        found=u2.is_followed_by(u)
        self.assertEqual(found,0)

    def test_user_create_success(self):
        """Does User.create successfully create a new user given valid credentials? """
        u=User.signup(username="test",
                    email="test@email.com",
                    password="hashedpassword",
                    image_url=User.image_url.default.arg)
        
        self.assertEqual(u.username,"test")
        self.assertEqual(u.email,"test@email.com")
        self.assertEqual(u.image_url,"/static/images/default-pic.png")

    def test_user_authenticate_success(self):
        """ Does User.authenticate successfully return a user when given a valid username and password?"""
        u=User.signup(username="test",
                    email="test@email.com",
                    password="hashedpassword",
                    image_url=User.image_url.default.arg)
        
        db.session.commit()
        
        ua=User.authenticate(username="test", password="hashedpassword")
        self.assertEqual(u,ua)

    def test_user_authenticate_fail_username(self):
        """ Does User.authenticate fail to return a user when the username is invalid?"""
        u=User.signup(username="test",
                    email="test@email.com",
                    password="hashedpassword",
                    image_url=User.image_url.default.arg)
        
        db.session.commit()
        
        ua=User.authenticate(username="test2", password="hashedpassword")
        self.assertEqual(ua,False)

    def test_user_authenticate_fail_password(self):
        """ Does User.authenticate fail to return a user when the password is invalid?"""
        u=User.signup(username="test",
                    email="test@email.com",
                    password="hashedpassword",
                    image_url=User.image_url.default.arg)
        
        db.session.commit()
        
        ua=User.authenticate(username="test2", password="hashedpassword22")
        self.assertEqual(ua,False)