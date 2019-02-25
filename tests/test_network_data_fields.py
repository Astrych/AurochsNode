"""
Tests checking fields primitieves used by network messaging code.
"""

from io import BytesIO

from pinkcoin.network import data_fields


def test_int16LE():
    """
    Checks Int16LE field.
    """
    field = data_fields.Int16LEField()
    field.parse(2)
    serialized_data = field.serialize()
    buffer = BytesIO()
    buffer.write(serialized_data)
    assert field.deserialize(buffer) == 2, "Wrong number"
