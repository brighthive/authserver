"""Data Trust Entity Unit Tests."""

import pytest
import json
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal
from authserver.db import db, DataTrust


class TestDataTrustModel:
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

            # Delete the data trusts, accounting for pre-populated one from migration.
            expect(DataTrust.query.count()).to(equal(2))
            db.session.delete(found_trust)
            db.session.commit()
            expect(DataTrust.query.count()).to(equal(1))
