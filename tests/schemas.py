"""
Ninja Schemas used by the autodojo unit tests
"""

from ninja import Schema

"""
This schema is used to test behaviours that involve passing
in already defined Schema classes.
"""


class DummySchema(Schema):
    id: int
    message: str
