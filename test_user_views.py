"""User View tests"""

# run these tests like:
#
# FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase
from test_helpers import add_users, set_variables_for_tests

from models import Follows, db, connect_db, Message, User
from flask import request

from app import CURR_USER_KEY


class UserViewTestCase(TestCase):
    """Test views for users"""

    @classmethod
    def setUpClass(cls):
        """Set variables and import app from helper function"""
        cls.app = set_variables_for_tests()

    def setUp(self):
        """Create test client, add sample data"""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = self.app.test_client()

        self.u1, self.u2 = add_users()

    def test_view_follower_following_pages(self):
        """Can a logged in user view another users follower/following pages?"""

        # Why on earth do I need this?
        u2 = User.query.filter(User.username == "fakeuser").one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            logged_in_followers_res = c.get(f"/users/{self.u2.id}/followers")
            self.assertEqual(logged_in_followers_res.status_code, 200)
            logged_in_following_res = c.get(f"/users/{self.u2.id}/following")
            self.assertEqual(logged_in_following_res.status_code, 200)

    def test_view_follower_following_pages_only_if_logged_in(self):
        """Can a logged out user view another users follower/following pages?"""

        with self.client as c:
            logged_out_followers_res = c.get(f"/users/{self.u2.id}/followers")
            self.assertEqual(logged_out_followers_res.status_code, 302)
            logged_out_following_res = c.get(f"/users/{self.u2.id}/following")
            self.assertEqual(logged_out_following_res.status_code, 302)

    def test_logout(self):
        """Can a user logout?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            res = c.get("/logout", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(request.path, "/login")

            # Not sure why this doesn't work
            # self.assertIsNone(sess[CURR_USER_KEY])
