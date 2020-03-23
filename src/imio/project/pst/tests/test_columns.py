# -*- coding: utf-8 -*-
""" columns.py tests for this package."""

from imio.project.pst.columns import HistoryActionsColumn
from imio.project.pst.columns import ParentsColumn
from imio.project.pst.testing import IntegrationTestCase
from plone import api
from plone.app.testing import setRoles


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
        # oo search
        category = self.pst['operationalobjectives']
        column = ParentsColumn(category, category.REQUEST, category.unrestrictedTraverse('@@faceted-table-view'))
        brain = self.portal.portal_catalog(UID=self.oo1.UID())[0]
        rendered = column.renderCell(brain)
        self.assertEqual(rendered, u'<ul class="parents_col"><li><a href="http://nohost/plone/pst/etre-une-commune'
                                   u'-qui-offre-un-service-public-moderne-efficace-et-efficient" target="_blank" '
                                   u'title="Etre une commune qui offre un service public moderne, efficace et '
                                   u'efficient" class="contenttype-strategicobjective"><span '
                                   u'class="pretty_link_content"> Etre une commune qui offre un ...</span></a>'
                                   u'</li></ul>')
        # ac search
        category = self.pst['pstactions']
        column = ParentsColumn(category, category.REQUEST, category.unrestrictedTraverse('@@faceted-table-view'))
        brain = self.portal.portal_catalog(UID=self.ac1.UID())[0]
        rendered = column.renderCell(brain)
        self.assertIn(u'<span class="pretty_link_content"> Etre une commune qui offre un ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Diminuer le temps d\'attente de ...</span>', rendered)

        # tk1 on global search
        category = self.pst['tasks']
        column = ParentsColumn(category, category.REQUEST, category.unrestrictedTraverse('@@faceted-table-view'))
        brain = self.portal.portal_catalog(UID=self.tk1.UID())[0]
        rendered = column.renderCell(brain)
        self.assertIn(u'<span class="pretty_link_content"> Etre une commune qui offre un ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Diminuer le temps d\'attente de ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Engager 2 agents pour le Service ...</span>', rendered)

        # tk1 on ac1 context
        column2 = ParentsColumn(self.ac1, category.REQUEST, category.unrestrictedTraverse('@@faceted-table-view'))
        rendered2 = column2.renderCell(brain)
        self.assertEqual(rendered2, '-')

        # Adding sub task
        tk2 = api.content.create(self.tk1, 'task', title=u'Tâche de second niveau')
        tk3 = api.content.create(tk2, 'task', title=u'Tâche de 3ème niveau')
        brain = self.portal.portal_catalog(UID=tk3.UID())[0]
        rendered = column.renderCell(brain)  # search context
        self.assertIn(u'<span class="pretty_link_content"> Etre une commune qui offre un ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Diminuer le temps d\'attente de ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Engager 2 agents pour le Service ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Ajouter une annonce sur le site ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Tâche de second niveau</span>', rendered)
        rendered2 = column2.renderCell(brain)  # action context
        self.assertNotIn(u'<span class="pretty_link_content"> Etre une commune qui offre un ...</span>', rendered2)
        self.assertNotIn(u'<span class="pretty_link_content"> Diminuer le temps d\'attente de ...</span>', rendered2)
        self.assertNotIn(u'<span class="pretty_link_content"> Engager 2 agents pour le Service ...</span>', rendered2)
        self.assertIn(u'<span class="pretty_link_content"> Ajouter une annonce sur le site ...</span>', rendered2)
        self.assertIn(u'<span class="pretty_link_content"> Tâche de second niveau</span>', rendered2)

        # adding sub action
        self.sac1 = api.content.create(self.ac1, 'pstsubaction', title=u'Sous-action')

        # ac search, rendering action and subaction
        category = self.pst['pstactions']
        column = ParentsColumn(category, category.REQUEST, category.unrestrictedTraverse('@@faceted-table-view'))
        brain = self.portal.portal_catalog(UID=self.ac1.UID())[0]
        rendered = column.renderCell(brain)
        self.assertIn(u'<span class="pretty_link_content"> Etre une commune qui offre un ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Diminuer le temps d\'attente de ...</span>', rendered)
        self.assertNotIn(u'<span class="pretty_link_content"> Engager 2 agents pour le Service ...</span>', rendered)
        brain = self.portal.portal_catalog(UID=self.sac1.UID())[0]
        rendered = column.renderCell(brain)
        self.assertIn(u'<span class="pretty_link_content"> Etre une commune qui offre un ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Diminuer le temps d\'attente de ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Engager 2 agents pour le Service ...</span>', rendered)

        # tk1 on global search : tk1 has been moved to sac1
        category = self.pst['tasks']
        column = ParentsColumn(category, category.REQUEST, category.unrestrictedTraverse('@@faceted-table-view'))
        brain = self.portal.portal_catalog(UID=self.tk1.UID())[0]
        rendered = column.renderCell(brain)
        self.assertIn(u'<span class="pretty_link_content"> Etre une commune qui offre un ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Diminuer le temps d\'attente de ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Engager 2 agents pour le Service ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Sous-action</span>', rendered)

        # tk1 on sac1 context
        column2 = ParentsColumn(self.sac1, self.sac1.REQUEST, category.unrestrictedTraverse('@@faceted-table-view'))
        rendered2 = column2.renderCell(brain)
        self.assertEqual(rendered2, '-')

        # Sub task
        brain = self.portal.portal_catalog(UID=tk3.UID())[0]
        rendered = column.renderCell(brain)  # search context
        self.assertIn(u'<span class="pretty_link_content"> Etre une commune qui offre un ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Diminuer le temps d\'attente de ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Engager 2 agents pour le Service ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Sous-action</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Ajouter une annonce sur le site ...</span>', rendered)
        self.assertIn(u'<span class="pretty_link_content"> Tâche de second niveau</span>', rendered)
        rendered2 = column2.renderCell(brain)  # action context
        self.assertNotIn(u'<span class="pretty_link_content"> Etre une commune qui offre un ...</span>', rendered2)
        self.assertNotIn(u'<span class="pretty_link_content"> Diminuer le temps d\'attente de ...</span>', rendered2)
        self.assertNotIn(u'<span class="pretty_link_content"> Engager 2 agents pour le Service ...</span>', rendered2)
        self.assertNotIn(u'<span class="pretty_link_content"> Sous-action</span>', rendered2)
        self.assertIn(u'<span class="pretty_link_content"> Ajouter une annonce sur le site ...</span>', rendered2)
        self.assertIn(u'<span class="pretty_link_content"> Tâche de second niveau</span>', rendered2)
