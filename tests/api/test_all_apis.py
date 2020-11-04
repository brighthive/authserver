"""Test all API endpoints.

This test class exercises all client facing APIs. It is also usesful as a tool for
demonstrating how to interact with the various APIs.

"""

import json

import pytest
from expects import (be, be_above, be_above_or_equal, contain, equal, expect,
                     raise_error)
from flask import Response

from tests.utils import post_users
from authserver.db import User, db

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
        'username': 'user1',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-1'
    },
    {
        'username': 'user2',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-2'
    },
    {
        'username': 'user3',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-3'
    },
    {
        'username': 'user4',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-4'
    },
    {
        'username': 'user5',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-5'
    },
    {
        'username': 'user6',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-6'
    },
    {
        'username': 'user7',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-7'
    },
    {
        'username': 'user8',
        'password': 'password',
        'person_id': 'c0ffee-c0ffee-8'
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

        # Create users, and clients
        user_ids = post_users(USERS, client, token_generator.get_token(client))
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

        self._cleanup(client, token_generator,
                      user_ids=user_ids, role_ids=role_ids)

    def test_client_secret_delete_rotate(self, client, token_generator):
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        user_ids = post_users(USERS, client, token_generator.get_token(client))
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

        self._cleanup(client, token_generator, user_ids=user_ids)

    def test_client_post_invalid_action(self, client, token_generator):
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        user_ids = post_users(USERS, client, token_generator.get_token(client))
        client_ids = self._post_clients(client, user_ids, token_generator)

        client_to_patch = client_ids[0]

        response = client.post('/clients?action=some_invalid_action',
                               data=json.dumps({"id": client_to_patch}), headers=headers)
        expect(response.status_code).to(equal(422))
        expect(response.json['messages']).to(contain("Invalid query param!"))

        self._cleanup(client, token_generator, user_ids=user_ids)

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

    def _cleanup(self, client, token_generator, role_ids=[], user_ids=[]):
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        for role_id in role_ids:
            response = client.delete(
                '/roles/{}'.format(role_id), headers=headers)
            expect(response.status_code).to(equal(200))

        for user_id in user_ids:
            response = client.delete(
                '/users/{}'.format(user_id), headers=headers)
            expect(response.status_code).to(equal(200))

    def test_assign_scope_to_user(self, client, token_generator):
        CLIENT = {

        }

        USER = {
            'username': 'test_user_scope',
            'password': 'secret',
            'person_id': 'c0ffee-c0ffee-c0ffee-99',
            'role_id': ''
        }

        ROLE = {
            'role': 'Administrator',
            'description': 'An administrative user role.'
        }

        SCOPE = {
            'scope': 'action:do-all-the-things',
            'description': 'A scope that grants the holder superpowers'
        }

        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}

        # Create a role
        response = client.post('/roles', data=json.dumps(ROLE), headers=headers)
        expect(response.status_code).to(be(201))
        role_id = response.json['response'][0]['id']

        # Create a scope
        response = client.post('/scopes', data=json.dumps(SCOPE), headers=headers)
        expect(response.status_code).to(be(201))
        scope_id = response.json['response'][0]['id']

        # Bind the scope to the role
        response = client.post(f'/roles/{role_id}/scopes', data=json.dumps({'scope_id': scope_id}), headers=headers)
        expect(response.status_code).to(be(201))

        # Create a user and make the user an administrator
        USER['role_id'] = role_id
        response = client.post('/users', data=json.dumps(USER), headers=headers)
        expect(response.status_code).to(be(201))
        user_id = response.json['response'][0]['id']

        # Cleanup
        response = client.delete(f'/users/{user_id}', headers=headers)
        expect(response.status_code).to(be(200))
        response = client.delete(f'/roles/{role_id}/scopes/{scope_id}', headers=headers)
        expect(response.status_code).to(be(200))
        response = client.delete(f'/roles/{role_id}', headers=headers)
        expect(response.status_code).to(be(200))
        response = client.delete(f'/scopes/{scope_id}', headers=headers)
        expect(response.status_code).to(be(200))
