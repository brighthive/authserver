import json

from expects import expect, equal, be_above_or_equal


def post_users(users, client, token):
    # def post_users(users, client, organization_id, token_generator):
    '''
    Helper function that creates (and tests creating) a collection of Users.
    '''

    headers = {'content-type': 'application/json', 'authorization': f'bearer {token}'}
    user_ids = []
    for user in users:
        user['active'] = True
        response = client.post(
            '/users', data=json.dumps(user), headers=headers)
        expect(response.status_code).to(equal(201))
        user_ids.append(response.json['response'][0]['id'])

    expect(len(user_ids)).to(be_above_or_equal(len(users)))

    return user_ids
