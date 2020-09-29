from datetime import datetime

import pytest
from expects import be_none, equal, expect, raise_error
from sqlalchemy.exc import IntegrityError

from authserver.db import Organization, db


class TestOrganizationModel:
    def test_organization_model_init(self):
        # Test that __init__ instantiates properties as expected.
        organization = Organization(**{"name": "Non-profit Organization"})

        expect(organization.id).not_to(be_none)
        expect(organization.name).to(equal("Non-profit Organization"))
        expect(organization.date_created.date()).to(equal(datetime.utcnow().date()))
        expect(organization.date_last_updated.date()).to(equal(datetime.utcnow().date()))

    def test_organization_str(self, organization):
        expect(str(organization)).to(equal(f'{organization.id} - {organization.name}'))

    def test_organization_model_unique_constraint(self, app, organization):
        # Test that duplicate organizations (i.e., with the same name) cannot be added to database.
        with app.app_context():
            organization = Organization(**{"name": organization.name})
            db.session.add(organization)
            expect(lambda: db.session.commit()).to(raise_error(IntegrityError))

    @pytest.mark.skip(reason='Skipping deprecated test')
    def test_users_backref(self, organization, user):
        expect(organization.id).to(equal(user.organization.id))
        expect(organization.name).to(equal(user.organization.name))
