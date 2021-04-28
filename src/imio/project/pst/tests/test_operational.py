# -*- coding: utf-8 -*-
""" Content action tests for this package."""
from datetime import datetime

from imio.project.pst.content.pstprojectspace import OPERATIONALOBJECTIVE_EXCLUDED_FIELDS
from imio.project.pst.testing import IntegrationTestCase
from zope.app.content import queryContentType
from zope.schema import getFieldsInOrder


class TestOperational(IntegrationTestCase):
    """Test strategic.py."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestOperational, self).setUp()
        self.os_10 = self.pst['etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-'
                              'de-serre-afin-dassurer-le-developpement-durable']
        self.oo_15 = self.os_10['reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-2024']
        self.a_16 = self.oo_15['reduire-la-consommation-energetique-de-ladministration-communale']

    def test_operationalobjective_fields_type(self):
        """Test operationalobjective fields type."""
        schema = queryContentType(self.oo2)
        fields = getFieldsInOrder(schema)
        # field is a tuple : (field_name, field_obj)
        for field in fields:
            try:
                # operationalobjective_fields_class is a dict : {'field_name': field_class}
                self.assertTrue(isinstance(field[1], self.operationalobjective_fields_class[field[0]]))
            except KeyError as err:
                # its ok for fields excluded intentionally
                print('EXCLUDED : {}'.format(err.message))
                if err.message in OPERATIONALOBJECTIVE_EXCLUDED_FIELDS:
                    pass
