from datetime import datetime

import pytest
from expects import be_none, equal, expect
from sqlalchemy.exc import IntegrityError

from authserver.db import Organization, db


def test_organization_model_init():
    # Test that __init__ instantiates properties as expected.
    organization = Organization(**{"name": "Non-profit Organization"})

    expect(organization.id).not_to(be_none)
    expect(organization.name).to(equal("Non-profit Organization"))
    expect(organization.date_created.date()).to(equal(datetime.utcnow().date()))
    expect(organization.date_last_updated.date()).to(equal(datetime.utcnow().date()))


def test_organization_str(organization):
    assert str(organization) == f"{organization.id} - {organization.name}"


def test_organization_model_unique_constraint(app, organization):
    # Test that duplicate organizations (i.e., with the same name) cannot be added to database.
    with app.app_context():
        organization = Organization(**{"name": organization.name})
        db.session.add(organization)

        with pytest.raises(IntegrityError) as execinfo:
            db.session.commit()


def test_users_backref():
    pass