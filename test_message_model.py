from sqlalchemy.exc import IntegrityError
from test_helpers import set_variables_for_tests, add_users
import os
from unittest import TestCase

from models import db, User, Message, Follows


class MessageModelTestCase(TestCase):
    """Test models for messages."""

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

    def test_add_message(self):
        """Can a user add a message?"""

        u = add_users()[0]

        msg = Message(user_id=u.id, text="A new tweet!")
        db.session.add(msg)
        db.session.commit()
        self.assertEqual(len(u.messages), 1)

    def test_reject_invalid_message(self):
        """Will an invalid message be rejected?"""

        u = add_users()[0]

        no_user = Message(text="A new tweet!")
        no_text = Message(user_id=u.id)
        invalid_user = Message(user_id=0, text="A new tweet!")

        for msg in [no_user, no_text, invalid_user]:
            db.session.add(msg)
            self.assertRaises(IntegrityError, db.session.commit)
            db.session.rollback()
