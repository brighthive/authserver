import json

import pytest
from expects import be, be_above_or_equal, contain, equal, expect, raise_error
from flask import Response
from authserver.db import Scope

SCOPES = [
    {
        'scope': 'user',
        'description': 'Standard user scope'
    },
    {
        'scope': 'superuser',
        'description': 'Super user scope'
    },
    {
        'scope': 'administrator',
        'description': 'Administrative user scope'
    }
]


class TestScopeResource:
    def test_scope_api(self, client, token_generator):
        # Common headers go in this dict
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}

        response = client.get('/scopes', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        print(f'******** {response.json}')
        expect(len(response_data['response'])).to(equal(0))

        # POST some new scoeps
        scope_ids = []
        for scope in SCOPES:
            response = client.post('/scopes', data=json.dumps(scope), headers=headers)
            expect(response.status_code).to(be(201))
            scope_ids.append(response.json['response'][0]['id'])

        # PATCH the first scope
        patched_scope = {
            'scope': SCOPES[0]['scope'].capitalize()
        }
        response = client.patch(f'/scopes/{scope_ids[0]}', data=json.dumps(patched_scope), headers=headers)
        expect(response.status_code).to(be(200))

        # Repost the second scope with PUT
        response = client.put(f'/scopes/{scope_ids[1]}', data=json.dumps(SCOPES[1]), headers=headers)
        expect(response.status_code).to(be(200))

        # Raise a 4xx status code if a scope is duplicated
        response = client.post(f'/scopes/{scope_ids[2]}')
        expect(response.status_code).to(be_above_or_equal(400))

        # Delete all scopes
        for id in scope_ids:
            response = client.delete(f'/scopes/{id}', headers=headers)
            expect(response.status_code).to(be(200))
        response = client.get('/scopes', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(equal(0))
