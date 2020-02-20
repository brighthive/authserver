import pytest
import json
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal
from authserver.db import db, DataTrust, User


# @pytest.mark.skip(reason=None)
class TestUserModel:
    def test_user_model(self, app):
        with app.app_context():
            # Create a test data trust
            trust_name = 'Sample Data Trust'
            new_trust = DataTrust(trust_name)
            trust_id = new_trust.id
            db.session.add(new_trust)
            db.session.commit()

            # Create a new user
            new_user = User(username='demo', password='password', firstname='Demonstration', lastname='User',
                            organization='Sample Organization', email_address='demo@me.com',
                            data_trust_id=trust_id, telephone='304-555-1234')
            db.session.add(new_user)
            db.session.commit()
            user_id = new_user.id
            found_user = User.query.filter_by(id=user_id).first()
            expect(found_user.id).to(equal(user_id))

            # Do not allow creation of users with the same username
            duplicate_user = User(username='demo', password='password', firstname='Demonstration', lastname='User',
                                  organization='Sample Organization', email_address='demo@me.com',
                                  data_trust_id=trust_id, telephone='304-555-1234')
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

            # Delete the user
            expect(User.query.count()).to(equal(2))
            db.session.delete(found_user)
            db.session.commit()
            expect(User.query.count()).to(equal(1))

            # Clean up data trusts
            data_trusts = DataTrust.query.all()
            for data_trust in data_trusts:
                DataTrust.query.filter_by(id=data_trust.id).delete()
                db.session.commit()
            expect(DataTrust.query.count()).to(equal(0))
