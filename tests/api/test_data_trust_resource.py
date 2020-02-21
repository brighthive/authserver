"""Data Trust Entity Unit Tests."""

import pytest
import requests
import json
from authserver.db import OAuth2Client
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal


class TestDataTrustResource:
    def test_data_trust_api(self, client, token_generator):

        # Common headers go in this dict
        headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}

        # Database should have pre-populated data trust at the beginning
        response: Response = client.get('/data_trusts', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(equal(1))

        # POST a new data trust
        request_body = {
            'data_trust_name': 'BrightHive Test Data Trust'
        }
        response = client.post(
            '/data_trusts', data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be(201))
        response_data = response.json
        data_trust_id = response_data['response'][0]['id']

        # GET all
        response: Response = client.get('/data_trusts', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(be_above_or_equal(1))

        # Attempt to POST the same data trust
        response = client.post(
            '/data_trusts', data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be_above_or_equal(400))

        # GET the data trust by ID
        response = client.get(
            '/data_trusts/{}'.format(data_trust_id), headers=headers)
        expect(response.status_code).to(be(200))

        # Create a new data trust
        request_body['data_trust_name'] = 'BrightHive Test Data Trust 2'
        response = client.post(
            '/data_trusts', data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be(201))
        response_data = response.json
        data_trust_id_2 = response_data['response'][0]['id']
        expect(data_trust_id).not_to(equal(data_trust_id_2))

        # Attempt to name both data trusts the same
        response = client.put('/data_trusts/{}'.format(data_trust_id),
                              data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be_above_or_equal(400))
        response = client.patch('/data_trusts/{}'.format(data_trust_id),
                                data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be_above_or_equal(400))

        # Rename data trust 2 with a PUT
        new_name = str(reversed(request_body['data_trust_name']))
        request_body['data_trust_name'] = new_name
        response = client.put('/data_trusts/{}'.format(data_trust_id_2),
                              data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(equal(200))

        # Rename data trust 2 with a PATCH
        new_name = str(reversed(request_body['data_trust_name']))
        request_body['data_trust_name'] = new_name
        response = client.patch('/data_trusts/{}'.format(data_trust_id_2),
                                data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(equal(200))

        # DELETE the data trusts
        response = client.delete(
            '/data_trusts/{}'.format(data_trust_id), headers=headers)
        response = client.delete(
            '/data_trusts/{}'.format(data_trust_id_2), headers=headers)
        expect(response.status_code).to(be(200))
