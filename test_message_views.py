"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from test_helpers import add_message, add_users, set_variables_for_tests
from flask import request, url_for
from models import db, connect_db, Message, User, Follows


from app import CURR_USER_KEY


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

        self.u1, self.u2 = add_users()

        db.session.commit()

    def test_add_message(self):
        """Can a user add a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            res = c.post(
                "/messages/new", data={"text": "A new message!"}, follow_redirects=True
            )
            msg = Message.query.one()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(request.path, f"/users/{self.u1.id}")
            self.assertIn("A new message", res.get_data(as_text=True))
            self.assertEqual(msg.text, "A new message!")

    def test_delete_message(self):
        """Can a user delete a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            # msg = Message(user_id=self.u1.id, text="A new message!")
            msg = add_message("Test message", self.u1.id)

            res = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(Message.query.count(), 0)
            self.assertEqual(request.path, f"/users/{self.u1.id}")

    def test_logged_out_user_cannot_add_messages(self):
        """Can a logged out user add messages?"""

        with self.client as c:

            res = c.post(
                "/messages/new", data={"text": "A new message!"}, follow_redirects=True
            )
            self.assertEqual(res.status_code, 200)
            self.assertEqual(Message.query.count(), 0)
            self.assertEqual(request.path, "/")

    def test_logged_out_user_cannot_delete_messages(self):
        """Can a logged out user delete messages?"""

        with self.client as c:

            msg = add_message(text="Delete this!", user_id=self.u1.id)
            res = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(Message.query.count(), 1)
            self.assertEqual(request.path, "/")

    # def test_cannot_add_others_message(self):
    #     """Can a user add a message with another user's ID?"""
    #     # Instructions say to add this test, but the messages_add just assigns the current user to the new message.
    #     # I'm not sure how you would even make a post request to do it.

    def test_cannot_delete_others_messages(self):
        """Can a user delete another user's message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            u2 = User.query.filter(User.username == "fakeuser").one()

            msg = add_message(text="Delete this!", user_id=u2.id)
            res = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(Message.query.count(), 1)
            self.assertEqual(request.path, url_for("messages_show", message_id=msg.id))
