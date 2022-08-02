"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from sqlalchemy.exc import IntegrityError
from test_helpers import set_variables_for_tests, add_users
import os
from unittest import TestCase

from models import db, User, Message, Follows


class UserModelTestCase(TestCase):
    """Test models for users."""

    @classmethod
    def setUpClass(cls):
        """Set variables and import app from helper function"""
        cls.app = set_variables_for_tests()

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = self.app.test_client()

    def test_add_user(self):
        """Does basic model work?"""

        # u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")
        u = add_users()[0]

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(f"<User #{u.id}: testuser, test@test.com>", str(u))

    def test_reject_invalid_user_creation(self):
        """Will new users with various problems be rejected?"""

        add_users()

        old_username = User(
            email="something@something.com", username="testuser", password="PASSWORD"
        )
        no_username = User(email="something@something.com", password="PASSWORD")

        old_email = User(
            email="test@test.com", username="something", password="PASSWORD"
        )
        no_email = User(username="something", password="PASSWORD")

        no_password = User(email="something@something.com", username="something")

        for user in [old_username, no_username, old_email, no_email, no_password]:
            db.session.add(user)
            self.assertRaises(IntegrityError, db.session.commit)
            db.session.rollback()

    def test_authenticate_user(self):
        """Can a user log in with valid credentials?"""

        u = add_users()[0]

        logged_in = User.authenticate("testuser", "UNHASHED_PASSWORD")
        self.assertIs(u, logged_in)

    def test_reject_bad_credentials(self):
        """Will a bad username/password be rejected?"""

        u = add_users()[0]
        self.assertFalse(User.authenticate("testuser", "BAD_PASSWORD"))
        self.assertFalse(User.authenticate("baduser", "UNHASHED_PASSWORD"))

    def test_following_functions(self):
        """Can users follow and be followed?"""

        u1, u2 = add_users()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u2.is_followed_by(u1))

        u1.following.append(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertTrue(u2.is_followed_by(u1))
