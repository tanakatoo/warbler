"""User view tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
from flask import session

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app
app.config['WTF_CSRF_ENABLED'] = False
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the tables
# and create fresh new clean test data

db.create_all()


class UserViewsTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()
        # Likes.query.delete()
        db.drop_all()
        db.create_all()

        self.client = app.test_client()
        
    def tearDown(self):
        db.session.rollback()
    
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
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        html=res.get_data(as_text=True)
        self.assertEqual(res.status_code,200)
        self.assertIn("@test22",html)
    
    def test_user_logout(self):
        # signup first
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg})
        
        res=self.client.get('/logout', follow_redirects=True)
        
        html=res.get_data(as_text=True)
        self.assertEqual(res.status_code,200)
        self.assertIn("Welcome back.", html)
        
    def test_user_login(self):
        # signup first
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg})
        
        res=self.client.get('/logout', follow_redirects=True)
        res=self.client.post('/login', data={'username':"test", 'password':"asdfasdf"}, follow_redirects=True)
        html=res.get_data(as_text=True)
        self.assertEqual(res.status_code,200)
        self.assertIn("Hello, test!", html)
        with self.client as c:
            with c.session_transaction() as sess:
                self.assertEqual(sess['curr_user'],1)
        
    def test_user_login_error_username(self):
        # signup first
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg})
        
        res=self.client.get('/logout', follow_redirects=True)
        res=self.client.post('/login', data={'username':"test2", 'password':"asdfasd"}, follow_redirects=True)
        html=res.get_data(as_text=True)
        self.assertEqual(res.status_code,200)
        self.assertIn("Invalid credentials.", html)
    
    def test_user_login_error_password(self):
        # signup first
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg})
        
        res=self.client.get('/logout', follow_redirects=True)
        res=self.client.post('/login', data={'username':"test", 'password':"sdfasd"}, follow_redirects=True)
        html=res.get_data(as_text=True)
        self.assertEqual(res.status_code,200)
        self.assertIn("Invalid credentials.", html)
        
    def test_user_list(self):
        """make sure all users are listed on the page"""
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
         
        res=self.client.get('/logout', follow_redirects=True)
        
        res=self.client.post('/signup',data={'username':"test2",
                    'email':"test2@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
         
        html=res.get_data(as_text=True)
        self.assertEqual(res.status_code,200)
        self.assertIn("@test", html)
        self.assertIn("@test2", html)
        
    def test_user_profile(self):
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        res=self.client.get('/users/1')
        html=res.get_data(as_text=True)
        self.assertEqual(res.status_code,200)
        self.assertIn('@test',html)
        self.assertIn('Edit Profile', html)
        self.assertIn('Messages', html)
        self.assertIn('Likes', html)
        
    def test_user_like(self):
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        res=self.client.post('/signup',data={'username':"test2",
                    'email':"test2@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        m=Message(user_id=1,text="testing message")
        db.session.add(m)
        db.session.commit()
        #self.client.referrer=('users/likes')
        res=self.client.post('/users/add_like/1', data={'g.user.id':2,'message_id':1}, follow_redirects=True,headers={"Referer": '/users/likes'})
        html=res.get_data(as_text=True)
        
        l=Likes.query.filter(Likes.user_id==2, Likes.message_id==1).first()
        # self.assertEqual(res.status_code,200)
        self.assertNotEqual(l,None)
        
    def test_user_unlike(self):
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        res=self.client.post('/signup',data={'username':"test2",
                    'email':"test2@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        m=Message(user_id=1,text="testing message")
        db.session.add(m)
        db.session.commit()
        #self.client.referrer=('users/likes')
        res=self.client.post('/users/add_like/1', data={'g.user.id':2,'message_id':1}, follow_redirects=True,headers={"Referer": '/users/likes'})
        res=self.client.post('/users/add_like/1', data={'g.user.id':2,'message_id':1}, follow_redirects=True,headers={"Referer": '/users/likes'})
        html=res.get_data(as_text=True)
        
        l=Likes.query.filter(Likes.user_id==2, Likes.message_id==1).first()
        self.assertEqual(l,None)
    
    def test_user_display_likes(self):
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        res=self.client.post('/signup',data={'username':"test2",
                    'email':"test2@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        m=Message(user_id=1,text="testing message")
        db.session.add(m)
        db.session.commit()
        #self.client.referrer=('users/likes')
        res=self.client.post('/users/add_like/1', data={'g.user.id':2,'message_id':1}, follow_redirects=True,headers={"Referer": '/users/likes'})
        res=self.client.get('/users/likes')
        html=res.get_data(as_text=True)
        
        self.assertIn('btn-primary',html)
    
    def test_user_follow(self):
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        res=self.client.post('/signup',data={'username':"test2",
                    'email':"test2@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        u=User.query.get(2)
        res=self.client.post('/users/follow/1', data={'follow_id':1,'g.user':u}, follow_redirects=True)
        html=res.get_data(as_text=True)
        
        self.assertIn('Unfollow',html)
        
    
    def test_user_followers(self):
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        res=self.client.post('/signup',data={'username':"person2",
                    'email':"person2@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        u=User.query.get(2)
        res=self.client.post('/users/follow/1', data={'follow_id':1,'g.user':u}, follow_redirects=True)
        res=self.client.get('/users/1/followers')
        html=res.get_data(as_text=True)
        
        self.assertIn('person2',html)
    
    def test_user_unfollow(self):
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        res=self.client.post('/signup',data={'username':"person2",
                    'email':"person2@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        u=User.query.get(2)
        res=self.client.post('/users/follow/1', data={'follow_id':1,'g.user':u}, follow_redirects=True)
        res=self.client.post('/users/stop-following/1', data={'follow_id':1,'g.user':u}, follow_redirects=True)
        html=res.get_data(as_text=True)
        
        self.assertNotIn('test',html)
    
    def test_user_edit_profile_fail(self):
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        u=User.query.get(1)
        res=self.client.post('/users/profile', data={'g.user':u,'form.password.data':'asdfasdf',"form.username.data":"test2"},follow_redirects=True)
        html=res.get_data(as_text=True)
        
        self.assertIn('Password not correct',html)
    
    def test_user_edit_profile_success(self):
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        u=User.query.get(1)
        res=self.client.post('/users/profile', data={'g.user':u,'form.password.data':'asdfasdf',"form.username.data":"test2"},follow_redirects=True)
        html=res.get_data(as_text=True)
        
        self.assertIn('test2',html)
    
    def test_user_delete(self):
        res=self.client.post('/signup',data={'username':"test",
                    'email':"test@email.com",
                    'password':"asdfasdf",
                    'image_url':User.image_url.default.arg}, follow_redirects=True)
        u=User.query.get(1)
        res=self.client.post('/users/delete', data={"g.user":u})
        u2=User.query.get(1)
        
        self.assertEqual(u2,None)
    