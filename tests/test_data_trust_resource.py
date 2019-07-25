"""Data Trust Entity Unit Tests."""

import pytest
import json
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal
from authserver.db import db, DataTrust


class TestDataTrustResource:
    def test_data_trust_api(self, client):

        # Common headers go in this dict
        headers = {'content-type': 'application/json'}

        # Database should be empty at the beginning
        response: Response = client.get('/datatrusts', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(equal(0))

        # POST a new data trust
        request_body = {
            'data_trust_name': 'BrightHive Test Data Trust'
        }
        response = client.post('/datatrusts', data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be(201))
        response_data = response.json
        data_trust_id = response_data['response'][0]['id']

        # GET all
        response: Response = client.get('/datatrusts', headers=headers)
        response_data = response.json
        expect(response.status_code).to(be(200))
        expect(len(response_data['response'])).to(be_above_or_equal(1))

        # Attempt to POST the same data trust
        response = client.post('/datatrusts', data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be_above_or_equal(201))

        # GET the data trust by ID
        response = client.get('/datatrusts/{}'.format(data_trust_id), headers=headers)
        expect(response.status_code).to(be(200))

        # Create a new data trust
        request_body['data_trust_name'] = 'BrightHive Test Data Trust 2'
        response = client.post('/datatrusts', data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be(201))
        response_data = response.json
        data_trust_id_2 = response_data['response'][0]['id']
        expect(data_trust_id).not_to(equal(data_trust_id_2))

        # Attempt to name both data trusts the same
        response = client.put('/datatrusts/{}'.format(data_trust_id), data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be_above_or_equal(400))
        response = client.patch('/datatrusts/{}'.format(data_trust_id), data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(be_above_or_equal(400))

        # Rename data trust 2 with a PUT
        new_name = str(reversed(request_body['data_trust_name']))
        request_body['data_trust_name'] = new_name
        response = client.put('/datatrusts/{}'.format(data_trust_id_2), data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(equal(200))

        # Rename data trust 2 with a PATCH
        new_name = str(reversed(request_body['data_trust_name']))
        request_body['data_trust_name'] = new_name
        response = client.patch('/datatrusts/{}'.format(data_trust_id_2), data=json.dumps(request_body), headers=headers)
        expect(response.status_code).to(equal(200))

        # DELETE the data trusts
        response = client.delete('/datatrusts/{}'.format(data_trust_id), headers=headers)
        response = client.delete('/datatrusts/{}'.format(data_trust_id_2), headers=headers)
        expect(response.status_code).to(be(200))

    def test_data_trust(self, app):
        with app.app_context():
            # Create a new data trust
            trust_name = 'Sample Data Trust'
            new_trust = DataTrust(trust_name)
            uuid = new_trust.id
            db.session.add(new_trust)
            db.session.commit()
            found_trust = DataTrust.query.filter_by(id=uuid).first()
            expect(found_trust.id).to(equal(uuid))
            expect(found_trust.data_trust_name).to(equal(trust_name))

            # Do not allow creation of trusts with the same name
            duplicate_trust = DataTrust(trust_name)
            db.session.add(duplicate_trust)
            expect(lambda: db.session.commit()).to(raise_error)
            db.session.rollback()

            # Update the data trust name
            new_name = str(reversed(trust_name))
            found_trust.data_trust_name = new_name
            db.session.commit()
            found_trust = DataTrust.query.filter_by(id=uuid).first()
            expect(found_trust.id).to(equal(uuid))
            expect(found_trust.data_trust_name).to(equal(new_name))

            # Delete the data trusts
            expect(DataTrust.query.count()).to(equal(1))
            db.session.delete(found_trust)
            expect(DataTrust.query.count()).to(equal(0))
