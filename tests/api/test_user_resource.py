import json

import pytest
from expects import be, be_above_or_equal, contain, equal, expect, raise_error
from flask import Response
from time import sleep

from tests.utils import post_users
from authserver.db import Organization


USERS = [
    {
        'username': 'test-user-1',
        'email_address': 'demo@me.com',
        'password': 'password',
        'firstname': 'David',
        'lastname': 'Michaels',
        'telephone': '304-555-1234'
    },
    {
        'username': 'test-user-2',
        'email_address': 'demo2@me.com',
        'password': 'password',
        'firstname': 'Janet',
        'lastname': 'Ferguson',
        'telephone': '304-555-5678'
    },
    {
        'username': 'test-user-3',
        'email_address': 'demo3@me.com',
        'password': 'password',
        'firstname': 'James',
        'lastname': 'Piper',
        'telephone': '304-555-9101'
    }
]


class TestUserResource:
    def test_user_api(self, client, organization, token_generator):
        # Common headers go in this dict
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}

        response = client.get('/users', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(equal(1))

        # Populate database with users
        post_users(USERS, client, organization.id, token_generator.get_token(client))

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
            response = client.get('/users/{}'.format(user['id']), headers=headers)
            expect(response.status_code).to(be(200))

        # Rename a user with a PATCH
        user_id = added_users[0]['id']
        new_name = str(reversed(added_users[0]['firstname']))
        single_field_update = {
            'firstname': new_name
        }
        response = client.patch('/users/{}'.format(user_id),
                                data=json.dumps(single_field_update), headers=headers)
        expect(response.status_code).to(equal(200))

        # Rename a user with a PUT, expect to fail because not all fields specified
        response = client.put('/users/{}'.format(user_id),
                              data=json.dumps(single_field_update), headers=headers)
        expect(response.status_code).to(equal(422))

        # Rename a user with a PUT, providing the entire object
        user_to_update = added_users[0]
        user_to_update['firstname'] = new_name
        user_to_update['password'] = 'password'
        user_to_update['organization_id'] = user_to_update['organization']['id']
        user_to_update.pop('organization', None)
        user_to_update.pop('date_created', None)
        user_to_update.pop('id', None)
        user_to_update.pop('date_last_updated', None)
        if not user_to_update['telephone']:
            user_to_update['telephone'] = 'N/A'

        response = client.put('/users/{}'.format(user_id), data=json.dumps(user_to_update), headers=headers)
        expect(response.status_code).to(equal(200))

        # Ensure users have been deleted by the deletion of the data trust associated with them.
        response = client.get('/users', headers=headers)
        expect(response.status_code).to(be(200))
        response_data = response.json

        # Deactivate a user
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        response = client.get('/users', headers=headers)

        a_user_id = response.json['response'][1]['id']
        associated_client_id = self._post_client(client, a_user_id, token_generator)

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

        response = client.get(
            '/clients/{}'.format(associated_client_id), headers=headers)
        expect(response.json['response']['client_secret']).to(be(None))

        # Delete users and clients
        response = client.delete(f'/clients/{associated_client_id}', headers=headers)
        expect(response.status_code).to(be(200))
        for user_id in added_user_ids:
            response = client.delete(f"/users/{user_id}", headers=headers)
            expect(response.status_code).to(be(200))

    def _post_client(self, client, user_id, token_generator):
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        client_data = {
            'client_name': 'test client 1',
            'user_id': user_id
        }
        response = client.post(
            '/clients', data=json.dumps(client_data), headers=headers)
        expect(response.status_code).to(equal(201))

        return response.json['response'][0]['id']
