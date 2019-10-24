# -*- coding: utf-8 -*-

from imio.project.pst.facetedcatalog import FacetedCatalog
from imio.project.pst.testing import IntegrationTestCase
from plone import api


class TestFacetedCatalog(IntegrationTestCase):
    """Test action.py."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestFacetedCatalog, self).setUp()

    def test_fc_call(self):
        fc = FacetedCatalog()
        # query of all oo
        query = {'facet.field': [u'review_state', u'categories', u'priority', u'representative_responsible',
                                 u'administrative_responsible', u'manager'], 'Language': ['fr', ''], 'b_size': 24,
                 'portal_type': {'query': ['operationalobjective']}, 'sort_on': u'created', 'sort_order': 'descending',
                 'b_start': 0, 'path': {'query': ['/plone/pst']}}
        context = self.pst['operationalobjectives']
        brains = fc.__call__(context, **query)
        self.assertEqual(len(brains), 5)  # all testing oo
        # with :has_child, multiple times => exception
        query = {'facet.field': [u'review_state', u'categories', u'priority', u'representative_responsible',
                                 u'administrative_responsible', u'manager'], 'Language': ['fr', ''], 'b_size': 24,
                 'portal_type': {'query': ['operationalobjective']}, 'sort_on': u'created', 'sort_order': 'descending',
                 'b_start': 0, 'path': {'query': ['/plone/pst']}, ':has_child': {}, ':has_child2': {}}
        with self.assertRaises(Exception) as cm:  # context manager
            brains = fc.__call__(context, **query)
        self.assertEqual(cm.exception.message, 'We only support one :has_child filter')
        # with :has_child
        api.content.transition(self.ac1, 'begin')
        query = {'facet.field': [u'review_state', u'categories', u'priority', u'representative_responsible',
                                 u'administrative_responsible', u'manager'], 'Language': ['fr', ''], 'b_size': 24,
                 'portal_type': {'query': ['operationalobjective']}, 'b_start': 0, 'path': {'query': ['/plone/pst']},
                 ':has_child': {'query': {'portal_type': {'query': ['pstaction']},
                 'review_state': {'query': 'ongoing'}}}}
        brains = fc.__call__(context, **query)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].id, self.oo1.id)

        # update another action to search 2 oos
        os2 = self.pst['etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-de-'
                       'serre-afin-dassurer-le-developpement-durable']
        oo2 = os2['doter-la-commune-de-competences-en-matiere-energetique-pour-fin-2021-compte-tenu-du-budget']
        api.content.transition(oo2['proceder-a-lengagement-dun-conseiller-en-energie'], 'begin')
        brains = fc.__call__(context, **query)
        self.assertEqual(len(brains), 2)
        self.assertListEqual([b.id for b in brains], [self.oo1.id, oo2.id])

        # change order
        query.update({'sort_on': u'id', 'sort_order': 'descending'})
        brains = fc.__call__(context, **query)
        self.assertListEqual([b.id for b in brains], [oo2.id, self.oo1.id])
