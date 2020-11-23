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
        schema = queryContentType(self.oo1)
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

    def test_list_contained_brains(self):
        """Test list_contained_brains method on operationalobjective."""
        self.assertEqual(
            [brain.Title for brain in
             self.oo_15.list_contained_brains(["pstaction", "action_link", "pstsubaction", "subaction_link"])],
            ["R\xc3\xa9duire la consommation \xc3\xa9nerg\xc3\xa9tique de l'administration communale (A.16)",
             'R\xc3\xa9aliser un audit \xc3\xa9nerg\xc3\xa9tique du b\xc3\xa2timent (SA.17)',
             "En fonction des r\xc3\xa9sultats, proc\xc3\xa9der \xc3\xa0 l'isolation du b\xc3\xa2timent (SA.18)",
             'En fonction des r\xc3\xa9sultats, remplacer le syst\xc3\xa8me de chauffage (SA.19)',
             'R\xc3\xa9duire la consommation \xc3\xa9nerg\xc3\xa9tique du hangar communal (A.20)',
             'R\xc3\xa9aliser un audit \xc3\xa9nerg\xc3\xa9tique du b\xc3\xa2timent (SA.17)',
             "En fonction des r\xc3\xa9sultats, proc\xc3\xa9der \xc3\xa0 l'isolation du b\xc3\xa2timent (SA.18)",
             'En fonction des r\xc3\xa9sultats, remplacer le syst\xc3\xa8me de chauffage (SA.19)']
        )

    def test_list_planned_end_date_of_contained_brains(self):
        """Test list_planned_end_date_of_contained_brains method on operationalobjective."""
        self.assertEqual(
            self.oo_15.list_planned_end_date_of_contained_brains(
                ["pstaction", "action_link", "pstsubaction", "subaction_link"]),
            [datetime.date(datetime(2024, 6, 30)), datetime.date(datetime(2020, 6, 30)),
             datetime.date(datetime(2020, 10, 31)), datetime.date(datetime(2020, 10, 31)),
             datetime.date(datetime(2024, 6, 30)), datetime.date(datetime(2020, 6, 30)),
             datetime.date(datetime(2020, 10, 31)), datetime.date(datetime(2020, 10, 31))]
        )

    def test_get_max_planned_end_date_of_contained_brains(self):
        """Test get_max_planned_end_date_of_contained_brains method on operationalobjective."""
        self.assertEqual(
            self.oo_15.get_max_planned_end_date_of_contained_brains(
                ["pstaction", "action_link", "pstsubaction", "subaction_link"]),
            datetime.date(datetime(2024, 6, 30))
        )
