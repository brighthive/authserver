import json

import pytest
from expects import be, be_above_or_equal, equal, expect, raise_error
from flask import Response

from authserver.db import User, db


class TestUserModel:
    def test_user_model(self, app):
        with app.app_context():
            # Create a new user
            new_user = User(username='demo', password='password', person_id='c0ffee-c0ffee')
            db.session.add(new_user)
            db.session.commit()
            user_id = new_user.id
            found_user = User.query.filter_by(id=user_id).first()
            expect(found_user.id).to(equal(user_id))

            # Do not allow creation of users with the same username
            duplicate_user = User(username='demo', password='password', person_id='c0ffee-c0ffee')
            duplicate_user_id = duplicate_user.id
            db.session.add(duplicate_user)
            expect(lambda: db.session.commit()).to(raise_error)
            db.session.rollback()

            # Update the user record
            new_person_id = str(reversed(found_user.person_id))
            found_user.person_id = new_person_id
            db.session.commit()
            found_user = User.query.filter_by(id=user_id).first()
            expect(found_user.id).to(equal(user_id))
            expect(found_user.person_id).to(equal(new_person_id))

            # Delete all users
            User.query.delete()
            db.session.commit()
            expect(User.query.count()).to(equal(0))
