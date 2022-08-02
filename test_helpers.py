"""Helpers for the test code"""

import os
from unittest import TestCase

from models import db, User, Message, Follows


def set_variables_for_tests():
    # os.environ["DATABASE_URL"] = "postgresql:///warbler_test"

    from app import app

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///warbler_test"

    app.config["TESTING"] = True
    app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
    app.config["WTF_CSRF_ENABLED"] = False

    # Create our tables (we do this here, so we only create the tables
    # once for all tests --- in each test, we'll delete the data
    # and create fresh new clean test data
    db.create_all()
    return app


def add_users() -> tuple[User, User]:
    """Add two test users to database"""

    user1 = User.signup(
        email="test@test.com",
        username="testuser",
        password="UNHASHED_PASSWORD",
        image_url=None,
    )
    user2 = User.signup(
        email="fake@fake.com",
        username="fakeuser",
        password="ANOTHER_PASSWORD",
        image_url=None,
    )
    db.session.add_all([user1, user2])
    db.session.commit()

    return (user1, user2)


def add_message(text: str, user_id: int) -> Message:
    """ "Add a message to the database"""

    msg = Message(user_id=user_id, text=text)
    db.session.add(msg)
    db.session.commit()
    return msg
