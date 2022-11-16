"""Like model tests."""

# run these tests like:
#
#    python -m unittest test_like_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
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


class LikeModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_like_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u2)
        db.session.commit()

        m=Message(text='hello',user_id=u2.id)
        db.session.add(m)
        db.session.commit()
        
        l=Likes(user_id=u.id,message_id=m.id)
        # User should have no messages & no followers
        db.session.add(l)
        db.session.commit()
        self.assertEqual(len(u.likes), 1)
