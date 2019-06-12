# -*- coding: utf-8 -*-
""" columns.py tests for this package."""

from imio.project.pst.columns import HistoryActionsColumn
from imio.project.pst.columns import ParentsColumn
from imio.project.pst.testing import IntegrationTestCase
from plone import api


class TestColumns(IntegrationTestCase):
    """"""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestColumns, self).setUp()
        self.os_table = self.pst['strategicobjectives'].unrestrictedTraverse('@@faceted-table-view')
        self.maxDiff = None

    def test_HistoryActionsColumn(self):
        self.login('psteditor')
        category = self.pst['strategicobjectives']
        category.REQUEST['AUTHENTICATED_USER'] = api.user.get_current()
        self.assertEquals(category.REQUEST.form.get('c0[]'), u'getObjPositionInParent')
        column = HistoryActionsColumn(category, category.REQUEST, self.os_table)
        brain = self.portal.portal_catalog(UID=self.os1.UID())[0]
        rendered = column.renderCell(brain)
        self.assertIn('title="back_to_created"', rendered)
        self.assertIn('title="achieve"', rendered)
        self.assertIn('title="Edit"', rendered)
        self.assertIn('title="title_move_item_bottom"', rendered)
        self.assertIn('title="title_move_item_down"', rendered)
        self.assertIn('title="Copy"', rendered)
        self.assertIn('title="history.gif_icon_title"', rendered)
        category.REQUEST.form['c0[]'] = u'sortable_title'
        rendered = column.renderCell(brain)
        self.assertIn('title="back_to_created"', rendered)
        self.assertNotIn('title="title_move_item_bottom"', rendered)
        self.assertNotIn('title="title_move_item_down"', rendered)

    def test_ParentsColumn(self):
        self.login('psteditor')
        # column not managed on this context
        category = self.pst['strategicobjectives']
        column = ParentsColumn(category, category.REQUEST, self.os_table)
        brain = self.portal.portal_catalog(UID=self.os1.UID())[0]
        rendered = column.renderCell(brain)
        self.assertEqual(rendered, u'-')
        # oo context
        category = self.pst['operationalobjectives']
        column = ParentsColumn(category, category.REQUEST, category.unrestrictedTraverse('@@faceted-table-view'))
        brain = self.portal.portal_catalog(UID=self.oo1.UID())[0]
        rendered = column.renderCell(brain)
        self.assertEqual(rendered, u'<ul class="parents_col"><li><a href="http://nohost/plone/pst/etre-une-commune-qui-'
                                   u'offre-un-service-public-moderne-efficace-et-efficient" target="_blank" title="Etre'
                                   u' une commune qui offre un service public moderne, efficace et efficient"><span '
                                   u'class="pretty_link_content">OS.1</span></a></li></ul>')
        # ac1 context
        category = self.pst['pstactions']
        column = ParentsColumn(category, category.REQUEST, category.unrestrictedTraverse('@@faceted-table-view'))
        brain = self.portal.portal_catalog(UID=self.ac1.UID())[0]
        rendered = column.renderCell(brain)
        self.assertIn(u'<span class="pretty_link_content">OS.1</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content">OO.2</span>', rendered)
