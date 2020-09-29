import json

import pytest
from expects import be, be_above_or_equal, equal, expect, raise_error
from flask import Response

from authserver.db import Organization, User, db


class TestUserModel:
    def test_user_model(self, app, organization):
        with app.app_context():
            # Create a new user
            new_user = User(username='demo', password='password', firstname='Demonstration', lastname='User',
                            organization_id=organization.id, email_address='demo@me.com', telephone='304-555-1234')
            db.session.add(new_user)
            db.session.commit()
            user_id = new_user.id
            found_user = User.query.filter_by(id=user_id).first()
            expect(found_user.id).to(equal(user_id))

            # Do not allow creation of users with the same username
            duplicate_user = User(username='demo', password='password', firstname='Demonstration', lastname='User',
                                  organization_id=organization.id, email_address='demo@me.com', telephone='304-555-1234')
            duplicate_user_id = duplicate_user.id
            db.session.add(duplicate_user)
            expect(lambda: db.session.commit()).to(raise_error)
            db.session.rollback()

            # Update the user record
            new_first_name = str(reversed(found_user.firstname))
            new_last_name = str((reversed(found_user.lastname)))
            found_user.firstname = new_first_name
            found_user.lastname = new_last_name
            db.session.commit()
            found_user = User.query.filter_by(id=user_id).first()
            expect(found_user.id).to(equal(user_id))
            expect(found_user.firstname).to(equal(new_first_name))
            expect(found_user.lastname).to(equal(new_last_name))

            # Delete all users
            User.query.delete()
            db.session.commit()
            expect(User.query.count()).to(equal(0))
