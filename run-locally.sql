-- Run this to login through Facet locally.

INSERT INTO oauth2_roles (id, role, description)
VALUES ('role-1', 'SuperAdmin', 'filler');

UPDATE users
SET person_id='person-1',
    can_login=true,
    role_id=(
        SELECT id FROM oauth2_roles WHERE role='SuperAdmin'
    )
WHERE username='brighthive_admin';

INSERT INTO authorized_clients (
    user_id,
    client_id,
    authorized
)
SELECT id, 'ru2tFykoIcR6vSWpsLgnYTpg', true
FROM users
WHERE users.username='brighthive_admin';

INSERT INTO oauth2_clients (
    user_id,
    id,
    client_id,
    client_secret,
    client_id_issued_at,
    client_secret_expires_at,
    client_metadata
)
SELECT
    id,
    'some-uuid',
    'client-salt',
    'client_secret',
    '123',
    '0',
    '{{"client_name": "testing_client", "scope": "", "token_endpoint_auth_method": "client_secret_json", "grant_types": ["client_credentials"], "response_types": ["token"]}}'
FROM users
WHERE users.username='brighthive_admin';