import pytest
import json
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal
from authserver.db import db, DataTrust, User


class TestUserResource:
    def test_user_api(self, client):
        expect(1).to(be(1))

        # # Common headers go in this dict
        # headers = {'content-type': 'application/json'}

        # # Database should be empty at the beginning
        # response: Response = client.get('/datatrusts', headers=headers)
        # response_data = response.json
        # expect(response.status_code).to(be(200))
        # expect(len(response_data['response'])).to(equal(0))

        # # POST a new data trust
        # request_body = {
        #     'data_trust_name': 'BrightHive Test Data Trust'
        # }
        # response = client.post('/datatrusts', data=json.dumps(request_body), headers=headers)
        # expect(response.status_code).to(be(201))
        # response_data = response.json
        # data_trust_id = response_data['response'][0]['id']

        # # GET all
        # response: Response = client.get('/datatrusts', headers=headers)
        # response_data = response.json
        # expect(response.status_code).to(be(200))
        # expect(len(response_data['response'])).to(be_above_or_equal(1))

        # # Attempt to POST the same data trust
        # response = client.post('/datatrusts', data=json.dumps(request_body), headers=headers)
        # expect(response.status_code).to(be_above_or_equal(201))

        # # GET the data trust by ID
        # response = client.get('/datatrusts/{}'.format(data_trust_id), headers=headers)
        # expect(response.status_code).to(be(200))

        # # Create a new data trust
        # request_body['data_trust_name'] = 'BrightHive Test Data Trust 2'
        # response = client.post('/datatrusts', data=json.dumps(request_body), headers=headers)
        # expect(response.status_code).to(be(201))
        # response_data = response.json
        # data_trust_id_2 = response_data['response'][0]['id']
        # expect(data_trust_id).not_to(equal(data_trust_id_2))

        # # Attempt to name both data trusts the same
        # response = client.put('/datatrusts/{}'.format(data_trust_id), data=json.dumps(request_body), headers=headers)
        # expect(response.status_code).to(be_above_or_equal(400))
        # response = client.patch('/datatrusts/{}'.format(data_trust_id), data=json.dumps(request_body), headers=headers)
        # expect(response.status_code).to(be_above_or_equal(400))

        # # Rename data trust 2 with a PUT
        # new_name = str(reversed(request_body['data_trust_name']))
        # request_body['data_trust_name'] = new_name
        # response = client.put('/datatrusts/{}'.format(data_trust_id_2), data=json.dumps(request_body), headers=headers)
        # expect(response.status_code).to(equal(200))

        # # Rename data trust 2 with a PATCH
        # new_name = str(reversed(request_body['data_trust_name']))
        # request_body['data_trust_name'] = new_name
        # response = client.patch('/datatrusts/{}'.format(data_trust_id_2), data=json.dumps(request_body), headers=headers)
        # expect(response.status_code).to(equal(200))

        # # DELETE the data trusts
        # response = client.delete('/datatrusts/{}'.format(data_trust_id), headers=headers)
        # response = client.delete('/datatrusts/{}'.format(data_trust_id_2), headers=headers)
        # expect(response.status_code).to(be(200))

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
                            telephone='304-555-1234')
            new_user.data_trust_id = trust_id
            db.session.add(new_user)
            db.session.commit()
            user_id = new_user.id
            found_user = User.query.filter_by(id=user_id).first()
            expect(found_user.id).to(equal(user_id))

            # Do not allow creation of users with the same username
            duplicate_user = User(username='demo', firstname='Demonstration', lastname='User',
                                  organization='Sample Organization', email_address='demo@me.com',
                                  telephone='304-555-1234')
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
