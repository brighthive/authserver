from expects import be, equal, be_above_or_equal, expect, be_none
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
    