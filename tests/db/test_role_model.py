"""Unit tests for Roles model."""

import pytest
import json
from uuid import uuid4
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal
from authserver.db import db, User, Role, OAuth2Client, Organization


class TestRoleModel:
    def test_role_model(self, app, organization):
        with app.app_context():
            # Create a new user
            new_user = User(username='demo', password='passw0rd', firstname='Demonstration', lastname='User',
                            organization_id=organization.id, email_address='demo@me.com', telephone='304-555-1234')
            db.session.add(new_user)
            db.session.commit()
            user_id = new_user.id

            # Create a new role
            new_role = Role('Role 1', 'Role 1 Description')
            db.session.add(new_role)
            db.session.commit()
            role_id = new_role.id

            # Create a new client
            new_client_metadata = {'client_name': 'Test Client', 'roles': []}
            new_client = OAuth2Client()
            new_client.user_id = user_id
            new_client.id = str(uuid4()).replace('-', '')
            new_client_metadata['roles'].append(new_role)
            new_client.client_metadata = new_client_metadata
            db.session.add(new_client)
            db.session.commit()
            client_id = new_client.id

            # Delete the client and the role
            Role.query.filter_by(id=role_id).delete()
            OAuth2Client.query.filter_by(id=client_id).delete()

            # Delete all users
            User.query.delete()
            db.session.commit()
            expect(User.query.count()).to(equal(0))
