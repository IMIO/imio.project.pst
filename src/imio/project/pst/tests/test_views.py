# -*- coding: utf-8 -*-
""" views.py tests for this package."""

from imio.project.pst.testing import IntegrationTestCase


class TestViews(IntegrationTestCase):
    """"""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestViews, self).setUp()

    def test_OSOOFacetedTableView(self):
        self.login('psteditor')
        # os context
        view = self.os1.unrestrictedTraverse('@@faceted-table-view')
        view.collection = self.pst['operationalobjectives']['all']
        self.assertNotIn(u'parents', view._getViewFields())
        # oo context
        view = self.oo1.unrestrictedTraverse('@@faceted-table-view')
        view.collection = self.pst['pstactions']['all']
        self.assertNotIn(u'parents', view._getViewFields())
        # category context
        categories = {
            'strategicobjectives': False,
            'operationalobjectives': True,
            'pstactions': True,
            'tasks': True,
        }
        for cat in categories:
            category = self.pst[cat]
            view = category.unrestrictedTraverse('@@faceted-table-view')
            view.collection = category['all']
            self.assertEqual(u'parents' in view._getViewFields(), categories[cat])
