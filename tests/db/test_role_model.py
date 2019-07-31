"""Unit tests for Roles model."""

import pytest
import json
from uuid import uuid4
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal
from authserver.db import db, DataTrust, User, Role, OAuth2Client


@pytest.mark.skip(reason=None)
class TestRoleModel:
    def test_role_model(self, app):
        with app.app_context():
            # Create a test data trust
            trust_name = 'Sample Data Trust'
            new_trust = DataTrust(trust_name)
            trust_id = new_trust.id
            db.session.add(new_trust)
            db.session.commit()

            # Create a new user
            new_user = User(username='demo', firstname='Demonstration', lastname='User',
                            organization='Sample Organization', email_address='demo@me.com',
                            data_trust_id=trust_id, telephone='304-555-1234')
            db.session.add(new_user)
            db.session.commit()
            user_id = new_user.id

            # Create a new role
            new_role = Role('Role 1', 'Role 1 Description')
            db.session.add(new_role)
            db.session.commit()
            role_id = new_role.id

            # Create a new client
            new_client = OAuth2Client()
            new_client.client_name = 'Test Client'
            new_client.user_id = user_id
            new_client.id = str(uuid4()).replace('-', '')
            new_client.roles.append(new_role)
            db.session.add(new_client)
            db.session.commit()
            client_id = new_client.id

            # Delete the client and the role
            Role.query.filter_by(id=role_id).delete()
            OAuth2Client.query.filter_by(id=client_id).delete()

            # Delete the user
            expect(User.query.count()).to(equal(1))
            db.session.delete(new_user)
            db.session.commit()
            expect(User.query.count()).to(equal(0))

            # Clean up data trusts
            data_trusts = DataTrust.query.all()
            for data_trust in data_trusts:
                DataTrust.query.filter_by(id=data_trust.id).delete()
                db.session.commit()
            expect(DataTrust.query.count()).to(equal(0))
