from marshmallow import ValidationError

def must_not_be_blank(data):
    """Custom Marshmallow validator.

    Reference: https://marshmallow.readthedocs.io/en/stable/examples.html#quotes-api-flask-sqlalchemy
    """
    if not data:
        raise ValidationError("Data not provided.")