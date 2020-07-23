import json

from expects import be, be_above_or_equal, be_none, equal, expect
from flask import Response

from authserver.db import Organization, db


def test_get_organizations(client, organization, organization_hh, token_generator):
    headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}

    response: Response = client.get(f'/organizations', headers=headers)
    response_data = response.json

    expect(response.status_code).to(be(200))
    expect(len(response_data['response'])).to(be_above_or_equal(2))
    assert organization.id in [org['id'] for org in response_data['response']]
    assert organization_hh.id in [org['id'] for org in response_data['response']]


def test_get_one_organization(client, organization, token_generator):
    headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}

    response: Response = client.get(f'/organizations/{organization.id}', headers=headers)
    response_data = response.json

    expect(response.status_code).to(be(200))
    expect(response.json['response']['id']).to(equal(organization.id))
    expect(response.json['response']['name']).to(equal(organization.name))
    expect(response.json['response']['date_created']).not_to(be_none)
    expect(response.json['response']['date_last_updated']).not_to(be_none)


def test_post_with_empty_body(client, token_generator):
    headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}

    response: Response = client.post(f'/organizations', headers=headers)

    expect(response.status_code).to(equal(400))
    expect(response.json['messages'][0]).to(equal('Empty request body.'))


def test_post_with_invalid_data(client, token_generator):
    headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
    invalid_org_data = {'not_a_field': 'Bad data'}

    response: Response = client.post(f'/organizations', data=json.dumps(invalid_org_data), headers=headers)

    expect(response.status_code).to(equal(422))
    expect(response.json['messages']['name'][0]).to(equal('Missing data for required field.'))


def test_post_organization(client, token_generator):
    headers = {'content-type': 'application/json', 'authorization': f'bearer {token_generator.get_token(client)}'}
    org_data = {'name': 'Helping Hands'}

    response: Response = client.post(f'/organizations', data=json.dumps(org_data), headers=headers)

    expect(response.status_code).to(equal(201))
    expect(response.json['messages'][0]).to(equal('Successfully created new Organization record.'))