# -*- coding: utf-8 -*-
""" Content action tests for this package."""
from imio.project.pst.content.pstprojectspace import OPERATIONALOBJECTIVE_EXCLUDED_FIELDS
from imio.project.pst.content.pstprojectspace import STRATEGICOBJECTIVE_EXCLUDED_FIELDS
from imio.project.pst.testing import IntegrationTestCase
from zope.app.content import queryContentType
from zope.schema import getFieldsInOrder


class TestOperational(IntegrationTestCase):
    """Test strategic.py."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestOperational, self).setUp()

    def test_operationalobjective_fields_type(self):
        """Test of fields type."""
        schema = queryContentType(self.oo1)
        fields = getFieldsInOrder(schema)
        # field is a tuple : (field_name, field_obj)
        for field in fields:
            try:
                # a_fields_type is a dict : {'field_name': field_class}
                self.assertTrue(isinstance(field[1], self.operationalobjective_fields_class[field[0]]))
            except KeyError as err:
                # its ok for fields excluded intentionally
                print('EXCLUDED : {}'.format(err.message))
                if err.message in OPERATIONALOBJECTIVE_EXCLUDED_FIELDS:
                    pass
