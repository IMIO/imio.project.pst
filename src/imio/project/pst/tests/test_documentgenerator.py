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
        self.assertEqual(objs[0], self.oo2)
        objs = view.getActions(self.oo2)
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.a3)
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
        self.assertEqual(objs[0], self.oo2)
        objs = view.getActions(self.oo2)
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.a3)
        objs = view.getTasks(self.a3)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[1], self.t1)

        def short_id(helper_i):
            if helper_i is None:
                return 'None'
            return helper_i.real_context.id.split('-')[-1]

        # flattened structure
        short_flattened_struct = [
            ('efficient', 'venir', 'population', 'None'),
            ('efficient', 'venir', 'population', 'None'),
            ('efficient', 'venir', 'mois', 'None'),
            ('efficient', 'venir', 'soi', 'None'),
            ('efficient', 'communale', 'guidance', 'None'),
            ('efficient', 'communale', 'guidance', 'None'),
            ('efficient', 'communale', 'guidance', 'None'),
            ('efficient', 'communale', 'pmr', 'None'),
            ('efficient', 'communale', 'vous', 'None'),
            ('efficient', 'communale', 'mois', 'None'),
            ('durable', 'budget', 'energie', 'None'),
            ('durable', 'budget', 'energie', 'None'),
            ('durable', 'budget', 'wallonie', 'None'),
            ('durable', 'budget', 'energetiques', 'None'),
            ('durable', '2024', 'communale', 'batiment'),
            ('durable', '2024', 'communale', 'batiment'),
            ('durable', '2024', 'communale', 'batiment'),
            ('durable', '2024', 'communale', 'chauffage'),
            ('durable', '2024', 'communal', 'batiment'),
            ('durable', '2024', 'communal', 'batiment'),
            ('durable', '2024', 'communal', 'batiment'),
            ('durable', '2024', 'communal', 'chauffage'),
            ('securite', '2022', 'sortie', 'None'),
            ('securite', '2022', 'sortie', 'None')
        ]

        # not dashboard
        del view.request.form['facetedQuery']
        struct = [(short_id(tup[0]), short_id(tup[1]), short_id(tup[2]), short_id(tup[3])) for tup in view.flatten_structure()]
        self.assertListEqual(struct, short_flattened_struct)
        # empty values
        new_os = api.content.create(self.pst, 'strategicobjective', 'new_os', 'New OS')
        struct = [(short_id(tup[0]), short_id(tup[1]), short_id(tup[2]), short_id(tup[3])) for tup in view.flatten_structure()]
        self.assertListEqual(struct, short_flattened_struct + [('new_os', 'None', 'None', 'None')])
        api.content.create(new_os, 'operationalobjective', 'new_oo', 'New OO')
        struct = [(short_id(tup[0]), short_id(tup[1]), short_id(tup[2]), short_id(tup[3])) for tup in view.flatten_structure()]
        self.assertListEqual(struct, short_flattened_struct + [('new_os', 'new_oo', 'None', 'None')])
        # dashboard
        view.request.form['facetedQuery'] = ''
        brains = self.pc(id='etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient')
        view.context_var = lambda x, default='', brains=brains: brains
        struct = [(short_id(tup[0]), short_id(tup[1]), short_id(tup[2]), short_id(tup[3])) for tup in view.flatten_structure()]
        self.assertListEqual(struct, short_flattened_struct[:10])

        # list_pst_elements
        elt_titles = [
            u'Etre une commune qui offre un service public moderne, efficace et efficient',
            u"Diminuer le temps d'attente de l'usager au guichet population de 20% dans les 12 mois \xe0 venir",
            u'Engager 2 agents pour le Service Population',
            u'Cr\xe9er un guichet suppl\xe9mentaire dans les 3 mois',
            u'Mettre en ligne sur le site internet diff\xe9rents documents "population" \xe0 t\xe9l\xe9charger de '
            u'chez soi',
            u"Optimiser l'accueil au sein de l'administration communale",
            u'Placer des pictogrammes de guidance',
            u"Installer une rampe d'acc\xe8s pour PMR",
            u'Mettre en place des permanences sur rendez-vous',
            u'Cr\xe9er un guichet suppl\xe9mentaire dans les 3 mois']
        self.assertEqual([elt.real_context.title for elt in view.list_pst_elements()], elt_titles)

        # check activated fields
        view.init_hv()
        dic = view.activated_fields
        self.assertEqual(len(dic['so']), 11)
        self.assertEqual(len(dic['oo']), 19)
        self.assertEqual(len(dic['ac']), 24)
        self.assertEqual(len(dic['sb']), 24)
        self.assertTrue(view.keep_field('so', 'categories'))
        self.assertFalse(view.keep_field('so', 'mygod'))

    def test_DocumentGenerationSOHelper(self):
        view = self.os1.unrestrictedTraverse('@@document_generation_helper_view')
        # not on dashboard
        self.assertFalse(view.is_dashboard())
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives(self.os1)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0], self.oo2)
        objs = view.getActions(self.oo2)
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.a3)
        self.assertEqual(view.getSection(), u'Volet interne : Administration générale')
        self.assertEqual(view.getDomain(), u"Amélioration de l'Administration")
        self.portal.REQUEST['PUBLISHED'] = view
        self.assertEqual(view.getOwnBudget(), '<table><thead><tr><th>Budget_type</th><th>Year</th><th>Amount</th><th>De'
                                              'tail / Comment</th></tr></thead><tbody><tr><td>Wallonie</td><td>2019</td'
                                              '><td>1,000.0</td><td></td><td></td></tr></tbody></table>'
                         )
        self.assertEqual(view.getOwnBudgetAsText(), '2019 pour Wallonie: 1000€')
        # TODO : Fix AssertionError
        self.assertTrue(view.hasChildrenBudget(self.os1))
        self.assertIn('<tfoot><tr><td>Totals</td><td>32767.5</td><td>27860.0</td><td>4907.5</td><td>-</td><td>-</td>'
                      '<td>-</td><td>-</td></tr></tfoot>', view.getChildrenBudget())
        self.assertEqual(view.getGlobalBudgetByYear(),
                         {2019: 28860.0, 2020: 4907.5, 2021: 0, 2022: 0, 2023: 0, 2024: 0})
        # on dashboard
        view.request.form['facetedQuery'] = ''
        self.assertTrue(view.is_dashboard())
        brains = self.pc(id='diminuer-le-temps-dattente-de-lusager-au-guichet-population-de-20-dans-les-12-mois'
                            '-a-venir')
        view.uids_to_objs(brains)
        self.assertListEqual(view.objs, [self.oo2])
        self.assertEqual(view.sel_type, 'operationalobjective')
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives(self.os1)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.oo2)
        objs = view.getActions(self.oo2)
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.a3)
        objs = view.getTasks(self.a3)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[1], self.t1)

    def test_DocumentGenerationOOHelper(self):
        view = self.oo2.unrestrictedTraverse('@@document_generation_helper_view')
        # not on dashboard
        self.assertFalse(view.is_dashboard())
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.oo2)
        objs = view.getActions(self.oo2)
        self.assertEqual(len(objs), 3)
        self.assertEqual(objs[0], self.a3)
        self.assertEqual(view.formatResultIndicator(), "Diminution du temps d'attente (en %) = 0 / 20")
        self.assertEqual(view.formatResultIndicator(expected=False), "Diminution du temps d'attente (en %) = 0")
        self.assertEqual(view.formatResultIndicator(reached=False), "Diminution du temps d'attente (en %) = 20")
        # on dashboard
        view.request.form['facetedQuery'] = ''
        self.assertTrue(view.is_dashboard())
        brains = self.pc(id='engager-2-agents-pour-le-service-population')
        view.uids_to_objs(brains)
        self.assertListEqual(view.objs, [self.a3])
        self.assertEqual(view.sel_type, 'pstaction')
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives(so=self.os1)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.oo2)
        objs = view.getActions(self.oo2)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.a3)
        objs = view.getTasks(self.a3)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[1], self.t1)

    def test_DocumentGenerationPSTActionsHelper(self):
        view = self.a3.unrestrictedTraverse('@@document_generation_helper_view')
        # not on dashboard
        self.assertFalse(view.is_dashboard())
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.oo2)
        objs = view.getActions()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.a3)
        self.assertEqual(view.formatHealthIndicator(), '<p class="Santé-bon"></p>')
        self.assertFalse(view.hasChildrenBudget(self.a3))
        objs = view.getTasks(self.a3)
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[1], self.t1)
        # on dashboard
        view.request.form['facetedQuery'] = ''
        self.assertTrue(view.is_dashboard())
        brains = self.pc(path={'query': '/'.join(self.a3.getPhysicalPath()), 'depth': 1})
        view.uids_to_objs(brains)
        self.assertListEqual(view.objs, [self.a3['rediger-le-profil-de-fonction'], self.t1, self.an1])
        self.assertEqual(view.sel_type, 'task')
        objs = view.getStrategicObjectives()
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.os1)
        objs = view.getOperationalObjectives(so=self.os1)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.oo2)
        objs = view.getActions(self.oo2)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0], self.a3)
        objs = view.getTasks(self.a3)
        self.assertEqual(len(objs), 3)

    def test_CategoriesDocumentGenerationView(self):
        pod_template = self.portal['templates']['ddetail']
        pod_template.context_variables = [{'name': 'details', 'value': '1'}]
        view = self.pst['strategicobjectives'].unrestrictedTraverse('@@document-generation')
        # hview without uids
        hview = self.pst['strategicobjectives'].unrestrictedTraverse('@@document_generation_helper_view')
        dic = view._get_generation_context(hview, pod_template)
        self.assertIn('context', dic)
        # TODO : Fix AssertionError
        # self.assertEqual(dic['context'].context, self.pst['strategicobjectives'])
        self.assertIn('view', dic)
        # TODO : Fix AssertionError
        # self.assertEqual(dic['view'], hview)
        self.assertIn('details', dic)
        self.assertEqual(dic['details'], '1')
        # TODO : Fix AssertionError
        # self.assertNotIn('brains', dic)
        # hview vith brains
        hview.request.form['uids'] = self.oo2.UID()
        hview.request.form['facetedQuery'] = ''
        dic = view._get_generation_context(hview, pod_template)
        self.assertIn('brains', dic)
        self.assertIn('uids', dic)
        self.assertListEqual(dic['uids'], [self.oo2.UID()])
        self.assertIn('context', dic)
        self.assertEqual(dic['context'], self.os1)
        self.assertIn('view', dic)
        self.assertTrue(isinstance(dic['view'], DocumentGenerationSOHelper))
        self.assertIn('details', dic)
        self.assertEqual(dic['details'], '1')
