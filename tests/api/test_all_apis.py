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

ORGANIZATION = {
    'name': 'Sample Organization'
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
        'email_address': 'user1@brighthive.me',
        'username': 'user1',
        'password': 'password',
        'telephone': '304-555-1234'
    },
    {
        'firstname': 'Kwame',
        'lastname': 'Anderson',
        'email_address': 'user2@brighthive.me',
        'username': 'user2',
        'password': 'password',
        'telephone': '304-555-5678'
    },
    {
        'firstname': 'Logan',
        'lastname': 'Williams',
        'email_address': 'user3@brighthive.me',
        'username': 'user3',
        'password': 'password',
        'telephone': '301-555-1234'
    },
    {
        'firstname': 'Amanda',
        'lastname': 'Stewart',
        'email_address': 'user4@brighthive.me',
        'username': 'user4',
        'password': 'password',
        'telephone': '412-555-4567'
    },
    {
        'firstname': 'Greg',
        'lastname': 'Henry',
        'email_address': 'user5@brighthive.me',
        'username': 'user5',
        'password': 'password',
        'telephone': '812-555-1234'
    },
    {
        'firstname': 'Tom',
        'lastname': 'Jones',
        'email_address': 'user6@brighthive.me',
        'username': 'user6',
        'password': 'password',
        'telephone': '912-555-1234'
    },
    {
        'firstname': 'Vyki',
        'lastname': 'Bennett',
        'email_address': 'user7@brighthive.me',
        'username': 'user7',
        'password': 'password'
    },
    {
        'firstname': 'Danielle',
        'lastname': 'Bevins',
        'email_address': 'user8@brighthive.me',
        'username': 'user8',
        'password': 'password'
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

        # Create a data trust, organization, users, and clients
        organization_id = self._post_organization(client, token_generator)
        user_ids = post_users(USERS, client, organization_id, token_generator.get_token(client))
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
                      user_ids=user_ids, role_ids=role_ids, organization_id=None)

    def test_client_secret_delete_rotate(self, client, organization, token_generator):
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        user_ids = post_users(USERS, client, organization.id, token_generator.get_token(client))
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

    def test_client_post_invalid_action(self, client, organization, token_generator):
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        user_ids = post_users(USERS, client, organization.id, token_generator.get_token(client))
        client_ids = self._post_clients(client, user_ids, token_generator)

        client_to_patch = client_ids[0]

        response = client.post('/clients?action=some_invalid_action',
                               data=json.dumps({"id": client_to_patch}), headers=headers)
        expect(response.status_code).to(equal(422))
        expect(response.json['messages']).to(contain("Invalid query param!"))

        self._cleanup(client, token_generator, user_ids=user_ids)

    def _post_organization(self, client, token_generator):
        '''
        Helper function that creates (and tests creating) an Organization entity.
        '''
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        response: Response = client.post(
            '/organizations', data=json.dumps(ORGANIZATION), headers=headers)
        expect(response.status_code).to(equal(201))

        organization_id = response.json['response'][0]['id']

        return organization_id

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

    def _cleanup(self, client, token_generator, role_ids=[], user_ids=[], organization_id=None):
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
        for role_id in role_ids:
            response = client.delete(
                '/roles/{}'.format(role_id), headers=headers)
            expect(response.status_code).to(equal(200))

        for user_id in user_ids:
            response = client.delete(
                '/users/{}'.format(user_id), headers=headers)
            expect(response.status_code).to(equal(200))

        if organization_id:
            response = client.delete(
                '/organizations/{}'.format(organization_id), headers)
            expect(response.status_code).to(equal(200))

    def test_assign_scope_to_user(self, client, token_generator):
        ORGANIZATION = {
            'name': 'Data Trust Organization'
        }

        CLIENT = {

        }

        USER = {
            'username': 'test_user_scope',
            'firstname': 'test',
            'lastname': 'testtest',
            'organization_id': '',
            'email_address': 'test@demo.com',
            'password': 'secret',
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

        # Create an organization
        response = client.post('/organizations', data=json.dumps(ORGANIZATION), headers=headers)
        expect(response.status_code).to(be(201))
        organization_id = response.json['response'][0]['id']

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

        # Create a user, assign to organization, and make the user an administrator
        USER['organization_id'] = organization_id
        USER['role_id'] = role_id
        response = client.post('/users', data=json.dumps(USER), headers=headers)
        expect(response.status_code).to(be(201))
        user_id = response.json['response'][0]['id']

        # Cleanup
        response = client.delete(f'/users/{user_id}', headers=headers)
        expect(response.status_code).to(be(200))
        response = client.delete(f'/organizations/{organization_id}', headers=headers)
        expect(response.status_code).to(be(200))
        response = client.delete(f'/roles/{role_id}/scopes/{scope_id}', headers=headers)
        expect(response.status_code).to(be(200))
        response = client.delete(f'/roles/{role_id}', headers=headers)
        expect(response.status_code).to(be(200))
        response = client.delete(f'/scopes/{scope_id}', headers=headers)
        expect(response.status_code).to(be(200))
