# -*- coding: utf-8 -*-
""" documentgenerator.py tests for this package."""
from datetime import datetime

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from imio.project.pst.testing import IntegrationTestCase
from imio.project.pst.browser.documentgenerator import DocumentGenerationSOHelper


class TestDocumentGenerator(IntegrationTestCase):
    """Test installation of imio.project.pst into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestDocumentGenerator, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.pc = self.portal.portal_catalog

    def test_DocumentGenerationPSTHelper(self):
        view = self.pst.unrestrictedTraverse('@@document_generation_helper_view')
        # not on dashboard
        self.assertFalse(view.is_dashboard())
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives(self.os1)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0], self.oo1)
        objs = view.getActions(self.oo1)
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.ac1)
        # on dashboard
        view.request.form['facetedQuery'] = ''
        self.assertTrue(view.is_dashboard())
        brains = self.pc(id='etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient')
        view.uids_to_objs(brains)
        self.assertListEqual(view.objs, [self.os1])
        self.assertEqual(view.sel_type, 'strategicobjective')
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives(self.os1)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0], self.oo1)
        objs = view.getActions(self.oo1)
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.ac1)
        objs = view.getTasks(self.ac1)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0], self.tk1)

    def test_DocumentGenerationSOHelper(self):
        currentYear = datetime.now().year
        view = self.os1.unrestrictedTraverse('@@document_generation_helper_view')
        # not on dashboard
        self.assertFalse(view.is_dashboard())
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives(self.os1)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0], self.oo1)
        objs = view.getActions(self.oo1)
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.ac1)
        self.assertEqual(view.getSection(), u'Volet interne : Administration générale')
        self.assertEqual(view.getDomain(), u"Amélioration de l'Administration")
        self.portal.REQUEST['PUBLISHED'] = view
        self.assertEqual(view.getOwnBudget(), '<table><thead><tr><th>Budget_type</th><th>Year</th><th>Amount</th></tr>'
                         '</thead><tbody><tr><td>Wallonie</td><td>%s</td><td>1,000.0</td><td></td></tr></tbody></table>'
                         % currentYear)
        self.assertTrue(view.hasChildrenBudget(self.os1))
        self.assertIn('<tfoot><tr><td>Totals</td><td>32767.5</td><td>-</td><td>-</td><td>-</td><td>-</td>'
                      '<td>27860.0</td><td>4907.5</td></tr></tfoot>', view.getChildrenBudget())
        # on dashboard
        view.request.form['facetedQuery'] = ''
        self.assertTrue(view.is_dashboard())
        brains = self.pc(id='diminuer-le-temps-dattente-de-lusager-au-guichet-population-de-20-dans-les-12-mois'
                            '-a-venir')
        view.uids_to_objs(brains)
        self.assertListEqual(view.objs, [self.oo1])
        self.assertEqual(view.sel_type, 'operationalobjective')
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives(self.os1)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.oo1)
        objs = view.getActions(self.oo1)
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.ac1)
        objs = view.getTasks(self.ac1)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0], self.tk1)

    def test_DocumentGenerationOOHelper(self):
        view = self.oo1.unrestrictedTraverse('@@document_generation_helper_view')
        # not on dashboard
        self.assertFalse(view.is_dashboard())
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.oo1)
        objs = view.getActions(self.oo1)
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.ac1)
        self.assertEqual(view.formatResultIndicator(), "Diminution du temps d'attente (en %) = 0 / 20")
        self.assertEqual(view.formatResultIndicator(expected=False), "Diminution du temps d'attente (en %) = 0")
        self.assertEqual(view.formatResultIndicator(reached=False), "Diminution du temps d'attente (en %) = 20")
        # on dashboard
        view.request.form['facetedQuery'] = ''
        self.assertTrue(view.is_dashboard())
        brains = self.pc(id='engager-2-agents-pour-le-service-population')
        view.uids_to_objs(brains)
        self.assertListEqual(view.objs, [self.ac1])
        self.assertEqual(view.sel_type, 'pstaction')
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives(so=self.os1)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.oo1)
        objs = view.getActions(self.oo1)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.ac1)
        objs = view.getTasks(self.ac1)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0], self.tk1)

    def test_DocumentGenerationPSTActionsHelper(self):
        view = self.ac1.unrestrictedTraverse('@@document_generation_helper_view')
        # not on dashboard
        self.assertFalse(view.is_dashboard())
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.oo1)
        objs = view.getActions()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.ac1)
        self.assertEqual(view.formatHealthIndicator(), '<p class="Santé-bon"></p>')
        self.assertFalse(view.hasChildrenBudget(self.ac1))
        objs = view.getTasks(self.ac1)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0], self.tk1)

    def test_CategoriesDocumentGenerationView(self):
        pod_template = self.portal['templates']['ddetail']
        pod_template.context_variables = [{'name': 'details', 'value': '1'}]
        view = self.pst['strategicobjectives'].unrestrictedTraverse('@@document-generation')
        # hview without uids
        hview = self.pst['strategicobjectives'].unrestrictedTraverse('@@document_generation_helper_view')
        dic = view._get_generation_context(hview, pod_template)
        self.assertIn('context', dic)
        self.assertEqual(dic['context'].context, self.pst['strategicobjectives'])
        self.assertIn('view', dic)
        self.assertEqual(dic['view'], hview)
        self.assertIn('details', dic)
        self.assertEqual(dic['details'], '1')
        self.assertNotIn('brains', dic)
        # hview vith brains
        hview.request.form['uids'] = self.oo1.UID()
        hview.request.form['facetedQuery'] = ''
        dic = view._get_generation_context(hview, pod_template)
        self.assertIn('brains', dic)
        self.assertIn('uids', dic)
        self.assertListEqual(dic['uids'], [self.oo1.UID()])
        self.assertIn('context', dic)
        self.assertEqual(dic['context'], self.os1)
        self.assertIn('view', dic)
        self.assertTrue(isinstance(dic['view'], DocumentGenerationSOHelper))
        self.assertIn('details', dic)
        self.assertEqual(dic['details'], '1')
