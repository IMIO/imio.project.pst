# -*- coding: utf-8 -*-
""" documentgenerator.py tests for this package."""

from imio.project.pst.browser.documentgenerator import DocumentGenerationSOHelper
from imio.project.pst.testing import IntegrationTestCase
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


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

        def short_id(helper_i):
            if helper_i is None:
                return 'None'
            return helper_i.real_context.id.split('-')[-1]

        # flattened structure
        short_flattened_struct = [
            ('efficient', 'venir', 'population'), ('efficient', 'venir', 'mois'), ('efficient', 'venir', 'soi'),
            ('efficient', 'communale', 'guidance'), ('efficient', 'communale', 'pmr'),
            ('efficient', 'communale', 'vous'),
            ('durable', 'budget', 'energie'), ('durable', 'budget', 'wallonie'), ('durable', 'budget', 'energetiques'),
            ('durable', '2013', 'communale'), ('durable', '2013', 'batiment'), ('durable', '2013', 'chaleur'),
            ('securite', '2015', 'sortie')
        ]
        # not dashboard
        del view.request.form['facetedQuery']
        struct = [(short_id(os), short_id(oo), short_id(ac)) for (os, oo, ac) in view.flatten_structure()]
        self.assertEqual(len(struct), len(self.pc(portal_type='pstaction')))
        self.assertListEqual(struct, short_flattened_struct)
        # empty values
        new_os = api.content.create(self.pst, 'strategicobjective', 'new_os', 'New OS')
        struct = [(short_id(os), short_id(oo), short_id(ac)) for (os, oo, ac) in view.flatten_structure()]
        self.assertListEqual(struct, short_flattened_struct + [('new_os', 'None', 'None')])
        api.content.create(new_os, 'operationalobjective', 'new_oo', 'New OO')
        struct = [(short_id(os), short_id(oo), short_id(ac)) for (os, oo, ac) in view.flatten_structure()]
        self.assertListEqual(struct, short_flattened_struct + [('new_os', 'new_oo', 'None')])
        # dashboard
        view.request.form['facetedQuery'] = ''
        brains = self.pc(id='etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient')
        view.context_var = lambda x, default='', brains=brains: brains
        struct = [(short_id(os), short_id(oo), short_id(ac)) for (os, oo, ac) in view.flatten_structure()]
        self.assertListEqual(struct, short_flattened_struct[:6])

    def test_DocumentGenerationSOHelper(self):
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
                         '</thead><tbody><tr><td>Wallonie</td><td>2019</td><td>1,000.0</td><td></td></tr>'
                         '</tbody></table>')
        self.assertEqual(view.getOwnBudgetAsText(), '2019 pour Wallonie: 1000€')
        self.assertTrue(view.hasChildrenBudget(self.os1))
        self.assertIn('<tfoot><tr><td>Totals</td><td>32767.5</td><td>27860.0</td><td>4907.5</td><td>-</td><td>-</td>'
                      '<td>-</td><td>-</td></tr></tfoot>', view.getChildrenBudget())
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
        # on dashboard
        view.request.form['facetedQuery'] = ''
        self.assertTrue(view.is_dashboard())
        brains = self.pc(path={'query': '/'.join(self.ac1.getPhysicalPath()), 'depth': 1})
        view.uids_to_objs(brains)
        self.assertListEqual(view.objs, [self.ac1['rediger-le-profil-de-fonction'], self.tk1])
        self.assertEqual(view.sel_type, 'task')
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
