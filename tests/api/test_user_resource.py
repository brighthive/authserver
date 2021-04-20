import json

import pytest
from expects import be, be_above_or_equal, contain, equal, expect, raise_error
from flask import Response
from time import sleep

from authserver.api.oauth2 import _store_client_authorization
from tests.utils import post_users


USERS = [
    {
        'username': 'test-user-1',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-1',
        'can_login': True
    },
    {
        'username': 'test-user-2',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-2',
        'can_login': True
    },
    {
        'username': 'test-user-3',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-3',
        'can_login': True
    }
]


class TestUserResource:
    def test_user_api(self, client, token_generator):
        # Common headers go in this dict
        headers = {'content-type': 'application/json',
                   'authorization': f'bearer {token_generator.get_token(client)}'}

        response = client.get('/users', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(equal(1))

        # Populate database with users
        post_users(USERS, client, token_generator.get_token(client))

        # GET all users
        response = client.get('/users', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(be_above_or_equal(3))
        added_users = response_data['response']

        # Store ID for all users since we will break the data.
        added_user_ids = []
        for user in added_users:
            added_user_ids.append(user['id'])

        # Attempt to POST an existing user
        response = client.post(
            '/users', data=json.dumps(USERS[0]), headers=headers)
        expect(response.status_code).to(be_above_or_equal(400))

        # Get all users by ID
        for user in added_users:
            response = client.get(
                '/users/{}'.format(user['id']), headers=headers)
            expect(response.status_code).to(be(200))

        # Update a user with a PATCH
        user_id = added_users[len(added_users) - 1]['id']
        new_person_id = str(
            reversed(added_users[len(added_users) - 1]['person_id']))
        single_field_update = {
            'person_id': new_person_id
        }
        response = client.patch('/users/{}'.format(user_id),
                                data=json.dumps(single_field_update), headers=headers)
        expect(response.status_code).to(equal(200))

        # Rename a user with a PUT, expect to fail because not all fields specified
        response = client.put('/users/{}'.format(user_id),
                              data=json.dumps(single_field_update), headers=headers)
        expect(response.status_code).to(equal(422))

        # Rename a user with a PUT, providing the entire object
        user_to_update = added_users[len(added_users) - 1]
        user_to_update['password'] = 'password'
        user_to_update.pop('role', None)
        user_to_update.pop('date_created', None)
        user_to_update.pop('id', None)
        user_to_update.pop('date_last_updated', None)

        response = client.put('/users/{}'.format(user_id),
                              data=json.dumps(user_to_update), headers=headers)
        expect(response.status_code).to(equal(200))

        # Ensure users have been deleted by the deletion of the data trust associated with them.
        response = client.get('/users', headers=headers)
        expect(response.status_code).to(be(200))
        response_data = response.json

        # Deactivate a user
        headers = {'content-type': 'application/json',
                   'authorization': f'bearer {token_generator.get_token(client)}'}
        response = client.get('/users', headers=headers)

        a_user_id = response.json['response'][1]['id']
        associated_client_id = self._post_client(
            client, a_user_id, token_generator)

        user_to_deactivate = {
            'id': a_user_id
        }

        # First, POST with an invalid argument
        response = client.post('/users?action=not-a-valid-argument',
                               data=json.dumps(user_to_deactivate), headers=headers)
        expect(response.status_code).to(equal(422))

        # Second, POST with an invalid user_id
        response = client.post('/users?action=deactivate',
                               data=json.dumps({'id': '123bad'}), headers=headers)
        expect(response.status_code).to(equal(404))
        expect(response.json['messages'][0]).to(
            equal("No resource with identifier '123bad' found."))

        # Finally, POST with a valid user_id
        response = client.post('/users?action=deactivate',
                               data=json.dumps(user_to_deactivate), headers=headers)
        expect(response.status_code).to(equal(200))

        response = client.get('/users/{}'.format(a_user_id), headers=headers)
        expect(response.json['response']['active']).to(be(False))
        expect(response.json['response']['can_login']).to(be(False))

        response = client.get(
            '/clients/{}'.format(associated_client_id), headers=headers)
        expect(response.json['response']['client_secret']).to(be(None))

        # Delete users and clients
        response = client.delete(
            f'/clients/{associated_client_id}', headers=headers)
        expect(response.status_code).to(be(200))
        for user_id in added_user_ids:
            response = client.delete(f"/users/{user_id}", headers=headers)
            expect(response.status_code).to(be(200))

    def _post_client(self, client, user_id, token_generator):
        headers = {'content-type': 'application/json',
                   'authorization': f'bearer {token_generator.get_token(client)}'}
        client_data = {
            'client_name': 'test client 1',
            'user_id': user_id
        }
        response = client.post(
            '/clients', data=json.dumps(client_data), headers=headers)
        expect(response.status_code).to(equal(201))

        return response.json['response'][0]['id']


class TestDELETEUserResource:
    def test_delete_user_with_client(self, mocker, client, token_generator):
        # Common headers go in this dict
        mocker.patch(
            "authlib.integrations.flask_oauth2.ResourceProtector.acquire_token",
            return_value=True,
        )

        # Populate database with user
        user_data = USERS[0]
        user_data['active'] = True
        response = client.post(
            '/users', data=json.dumps(user_data), headers={})
        user_id = response.json['response'][0]['id']

        # Populate database with client
        client_data = {
            'client_name': 'test client 1',
            'user_id': user_id
        }
        response = client.post(
            '/clients', data=json.dumps(client_data), headers={})
        client_id = response.json['response'][0]['id']

        # Add entity to authorized_client
        _store_client_authorization(client_id=client_id, user_id=user_id)

        # DELETE the user (without 'ForeignKeyViolation' error)
        response = client.delete(f"/users/{user_id}", headers={})
        expect(response.status_code).to(be(200))

        # Assert that user no longer exists
        response = client.get(f"/users/{user_id}", headers={})
        expect(response.status_code).to(equal(404))
