import pytest
import json
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal
from authserver.db import db, DataTrust, User


class TestUserResource:
    def test_user_api(self, client):
        # Common headers go in this dict
        headers = {'content-type': 'application/json'}

        # Database should be empty at the beginning
        response: Response = client.get('/data_trusts', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(be_above_or_equal(0))

        response = client.get('/users', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(equal(0))

        # POST a new data trust
        request_body = {
            'data_trust_name': 'BrightHive Test Data Trust'
        }
        response = client.post('/data_trusts', data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be(201))
        response_data = response.json
        data_trust_id = response_data['response'][0]['id']

        users = [
            {
                'username': 'test-user-1',
                'email_address': 'demo@me.com',
                'firstname': 'David',
                'lastname': 'Michaels',
                'data_trust_id': data_trust_id,
                'organization': 'BrightHive',
                'telephone': '304-555-1234'
            },
            {
                'username': 'test-user-2',
                'email_address': 'demo2@me.com',
                'firstname': 'Janet',
                'lastname': 'Ferguson',
                'data_trust_id': data_trust_id,
                'organization': 'Second Organization'
            },
            {
                'username': 'test-user-3',
                'email_address': 'demo3@me.com',
                'firstname': 'James',
                'lastname': 'Piper',
                'data_trust_id': data_trust_id,
                'organization': 'Second Organization'
            }
        ]

        # Create good users
        for user in users:
            response = client.post('/users', data=json.dumps(user), headers=headers)
            response_data = response.json
            expect(response.status_code).to(be(201))
        response = client.get('/users', headers=headers)
        expect(len(response.json['response'])).to(be_above_or_equal(3))

        # GET all users
        response = client.get('/users', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(be_above_or_equal(3))
        added_users = response_data['response']

        # Attempt to POST an existing user
        response = client.post('/users', data=json.dumps(users[0]), headers=headers)
        expect(response.status_code).to(be_above_or_equal(400))

        # Get all users by ID
        for user in added_users:
            response = client.get('/users/{}'.format(user['id']))
            expect(response.status_code).to(be(200))

        # Rename a user with a PATCH
        new_name = str(reversed(added_users[0]['firstname']))
        single_field_update = {
            'firstname': new_name
        }
        response = client.patch('/users/{}'.format(added_users[0]['id']), data=json.dumps(single_field_update), headers=headers)
        expect(response.status_code).to(equal(200))

        # Rename a user with a PUT, expect to fail because not all fields specified
        response = client.put('/users/{}'.format(added_users[0]['id']), data=json.dumps(single_field_update), headers=headers)
        expect(response.status_code).to(equal(422))

        # Rename a user with a PUT, providing the entire object
        added_users[0]['firstname'] = new_name
        response = client.put('/users/{}'.format(added_users[0]['id']), data=json.dumps(added_users[0]), headers=headers)
        expect(response.status_code).to(equal(200))

        # DELETE the data trusts and by extension delete the users
        response = client.delete('/data_trusts/{}'.format(data_trust_id), headers=headers)
        expect(response.status_code).to(be(200))

        # Ensure users have been deleted by the deletion of the data trust associated with them.
        response = client.get('/users', headers=headers)
        expect(response.status_code).to(be(200))
        response_data = response.json
        expect(len(response_data['response'])).to(equal(0))

    def test_user(self, app):
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
            found_user = User.query.filter_by(id=user_id).first()
            expect(found_user.id).to(equal(user_id))

            # Do not allow creation of users with the same username
            duplicate_user = User(username='demo', firstname='Demonstration', lastname='User',
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
            expect(User.query.count()).to(equal(1))
            db.session.delete(found_user)
            db.session.commit()
            expect(User.query.count()).to(equal(0))

            # Clean up data trusts
            data_trusts = DataTrust.query.all()
            for data_trust in data_trusts:
                DataTrust.query.filter_by(id=data_trust.id).delete()
                db.session.commit()
            expect(DataTrust.query.count()).to(equal(0))
