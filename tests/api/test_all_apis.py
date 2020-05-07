"""Test all API endpoints.

This test class exercises all client facing APIs. It is also usesful as a tool for
demonstrating how to interact with the various APIs.

"""

import pytest
import json
from flask import Response
from expects import expect, be, equal, raise_error, be_above, be_above_or_equal, contain
from authserver.db import db, DataTrust, User

DATA_TRUST = {
    'data_trust_name': 'Sample Data Trust'
}

ROLES = [
    {
        'role': 'get:programs',
        'description': 'Get from programs data resource',
        'rules': {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3',
            'key4': 'value4'
        }
    },
    {
        'role': 'administer:programs',
        'description': 'All access on programs data resource',
        'rules': {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3',
            'key4': 'value4'
        }
    },
    {
        'role': 'edit:providers',
        'description': 'Edit providers only'
    },
    {
        'role': 'view:providers',
        'description': 'View providers only',
        'rules': {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3',
            'key4': 'value4'
        }
    }
]

USERS = [
    {
        'firstname': 'Regina',
        'lastname': 'Wolfgang',
        'organization': 'BrightHive',
        'email_address': 'user1@brighthive.me',
        'username': 'user1',
        'password': 'password',
        'data_trust_id': '',
        'telephone': '304-555-1234'
    },
    {
        'firstname': 'Kwame',
        'lastname': 'Anderson',
        'organization': 'BrightHive',
        'email_address': 'user2@brighthive.me',
        'username': 'user2',
        'password': 'password',
        'data_trust_id': '',
        'telephone': '304-555-5678'
    },
    {
        'firstname': 'Logan',
        'lastname': 'Williams',
        'organization': 'BrightHive',
        'email_address': 'user3@brighthive.me',
        'username': 'user3',
        'password': 'password',
        'data_trust_id': '',
        'telephone': '301-555-1234'
    },
    {
        'firstname': 'Amanda',
        'lastname': 'Stewart',
        'organization': 'BrightHive',
        'email_address': 'user4@brighthive.me',
        'username': 'user4',
        'password': 'password',
        'data_trust_id': '',
        'telephone': '412-555-4567'
    },
    {
        'firstname': 'Greg',
        'lastname': 'Henry',
        'organization': 'BrightHive',
        'email_address': 'user5@brighthive.me',
        'username': 'user5',
        'password': 'password',
        'data_trust_id': '',
        'telephone': '812-555-1234'
    },
    {
        'firstname': 'Tom',
        'lastname': 'Jones',
        'organization': 'BrightHive',
        'email_address': 'user6@brighthive.me',
        'username': 'user6',
        'password': 'password',
        'data_trust_id': '',
        'telephone': '912-555-1234'
    },
    {
        'firstname': 'Vyki',
        'lastname': 'Bennett',
        'organization': 'BrightHive',
        'email_address': 'user7@brighthive.me',
        'username': 'user7',
        'password': 'password',
        'data_trust_id': ''
    },
    {
        'firstname': 'Danielle',
        'lastname': 'Bevins',
        'organization': 'BrightHive',
        'email_address': 'user8@brighthive.me',
        'username': 'user8',
        'password': 'password',
        'data_trust_id': ''
    }
]

CLIENTS = [
    {
        'client_name': 'test client 1',
        'user_id': ''
    },
    {
        'client_name': 'test client 2',
        'user_id': ''
    },
    {
        'client_name': 'test client 3',
        'user_id': ''
    },
    {
        'client_name': 'test client 4',
        'user_id': ''
    },
    {
        'client_name': 'test client 5',
        'user_id': ''
    },
    {
        'client_name': 'test client6',
        'user_id': ''
    },
    {
        'client_name': 'test client 7',
        'user_id': ''
    },
    {
        'client_name': 'test client 8',
        'user_id': ''
    }
]


class TestAllAPIs(object):
    def test_all_apis(self, client, token_generator):
        # Common headers go in this dict
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}

        data_trust_id = self._post_data_trust(client, token_generator)
        user_ids = self._post_users(client, data_trust_id, token_generator)
        client_ids = self._post_clients(client, user_ids, token_generator)

        # Create roles
        role_ids = []
        for role in ROLES:
            response = client.post(
                '/roles', data=json.dumps(role), headers=headers)
            expect(response.status_code).to(equal(201))
            role_ids.append(response.json['response'][0]['id'])

        # Assign clients to users and roles to client
        for i, client_id in enumerate(client_ids):
            request_body = {
                'user_id': user_ids[i],
                'roles': role_ids
            }
            response = client.patch(
                '/clients/{}'.format(client_id), data=json.dumps(request_body), headers=headers)
            expect(response.status_code).to(equal(200))

        # Ensure that clients actually have roles, users, and other crucial fields
        for client_id in client_ids:
            response = client.get(
                '/clients/{}'.format(client_id), headers=headers)
            result = response.json['response']
            expect(result['id']).to(equal(client_id))
            expect(result['client_id_issued_at']).to(be_above(0))
            expect(user_ids).to(contain(result['user_id']))
            expect(len(result['roles'])).to(equal(len(role_ids)))

        self._cleanup(client, data_trust_id, token_generator,
                      user_ids=user_ids, role_ids=role_ids)

    def test_client_secret_delete_rotate(self, client, token_generator):
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        data_trust_id = self._post_data_trust(client, token_generator)
        user_ids = self._post_users(client, data_trust_id, token_generator)
        client_ids = self._post_clients(client, user_ids, token_generator)

        client_to_patch = client_ids[0]

        response = client.post('/clients?action=delete_secret',
                               data=json.dumps({"id": client_to_patch}), headers=headers)
        expect(response.status_code).to(equal(200))
        response = client.get('/clients/{}'.format(client_to_patch), headers=headers)
        expect(response.json['response']['client_secret']).to(equal(None))

        response = client.post('/clients?action=rotate_secret',
                               data=json.dumps({"id": client_to_patch}), headers=headers)
        expect(response.status_code).to(equal(200))
        response = client.get('/clients/{}'.format(client_to_patch), headers=headers)
        expect(len(response.json['response']['client_secret'])).to(equal(48))

        self._cleanup(client, data_trust_id, token_generator, user_ids=user_ids)

    def _post_data_trust(self, client, token_generator):
        '''
        Helper function that creates (and tests creating) a Data Trust entity.
        '''
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        response: Response = client.post(
            '/data_trusts', data=json.dumps(DATA_TRUST), headers=headers)
        expect(response.status_code).to(equal(201))

        data_trust_id = response.json['response'][0]['id']

        return data_trust_id

    def _post_users(self, client, data_trust_id, token_generator):
        '''
        Helper function that creates (and tests creating) a collection of Users.
        '''
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        user_ids = []
        for user in USERS:
            user['data_trust_id'] = data_trust_id
            user['active'] = True
            response = client.post(
                '/users', data=json.dumps(user), headers=headers)
            expect(response.status_code).to(equal(201))
            user_ids.append(response.json['response'][0]['id'])

        expect(len(user_ids)).to(equal(8))

        return user_ids

    def _post_clients(self, client, user_ids, token_generator):
        '''
        Helper function that creates (and tests creating) a collection of Clients.
        '''
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        client_ids = []
        for i, api_client in enumerate(CLIENTS):
            api_client['user_id'] = user_ids[i]
            response = client.post('/clients', data=json.dumps(api_client), headers=headers)
            expect(response.status_code).to(equal(201))
            client_ids.append(response.json['response'][0]['id'])

        expect(len(client_ids)).to(equal(8))

        return client_ids

    def _cleanup(self, client, data_trust_id, token_generator, role_ids=[], user_ids=[]):
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        for role_id in role_ids:
            response = client.delete(
                '/roles/{}'.format(role_id), headers=headers)
            expect(response.status_code).to(equal(200))

        for user_id in user_ids:
            response = client.delete(
                '/users/{}'.format(user_id), headers=headers)
            expect(response.status_code).to(equal(200))

        response = client.delete(
            '/data_trusts/{}'.format(data_trust_id), headers=headers)
        expect(response.status_code).to(equal(200))
