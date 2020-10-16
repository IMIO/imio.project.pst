# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from imio.pyutils.system import runCommand
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import z2
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Testing import ZopeTestCase as ztc
from zope.globalrequest.local import setLocal

import imio.project.pst
import os
import unittest


class PSTLayer(PloneWithPackageLayer):

    def setUpPloneSite(self, portal):
        setattr(portal, '_TESTING_SITE_', True)
        setLocal('request', portal.REQUEST)
        applyProfile(portal, 'Products.CMFPlone:plone')
        #        applyProfile(portal, 'Products.CMFPlone:plone-content')  # could be done too
        manage_addExternalMethod(portal, 'lock-unlock', '', 'imio.project.pst.robot', 'lock')
        manage_addExternalMethod(portal, 'robot_init', '', 'imio.project.pst.robot', 'robot_init')

        super(PSTLayer, self).setUpPloneSite(portal)
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.portal_setup.runAllImportStepsFromProfile('profile-imio.project.pst:demo')

    def setUpZope(self, app, configurationContext):
        ztc.utils.setupCoreSessions(app)
        super(PSTLayer, self).setUpZope(app, configurationContext)
        (stdout, stderr, st) = runCommand('%s/bin/soffice.sh restart' % os.getenv('PWD'))

    def tearDownZope(self, app):
        """Tear down Zope."""
        (stdout, stderr, st) = runCommand('%s/bin/soffice.sh stop' % os.getenv('PWD'))


PST_TESTING_PROFILE = PSTLayer(
    zcml_filename="testing.zcml",
    zcml_package=imio.project.pst,
    additional_z2_products=('Products.PasswordStrength', 'Products.DateRecurringIndex', 'imio.dashboard',
                            'imio.project.pst'),
    gs_profile_id='imio.project.pst:testing',
    name="PST_TESTS_PROFILE")

PST_TESTING_PROFILE_INTEGRATION = IntegrationTesting(
    bases=(PST_TESTING_PROFILE,), name="PST_TESTING_PROFILE_INTEGRATION")

PST_TEST_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(PST_TESTING_PROFILE,), name="PST_TESTING_PROFILE_FUNCTIONAL")

PST_ROBOT_TESTING = FunctionalTesting(
    bases=(PST_TESTING_PROFILE,
           REMOTE_LIBRARY_BUNDLE_FIXTURE,
           z2.ZSERVER_FIXTURE,),
    name="PST_ROBOT_TESTING")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = PST_TESTING_PROFILE_INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        # default setup
        self.os_fields = [
            'IDublinCore.title', 'description_rich', 'reference_number', 'categories', 'plan',
            'IAnalyticBudget.projection', 'IAnalyticBudget.analytic_budget', 'budget', 'budget_comments',
            'observation', 'comments'
        ]
        self.oo_fields = [
            'IDublinCore.title', 'description_rich', 'reference_number', 'categories', 'plan',
            'result_indicator', 'priority', 'planned_end_date', 'representative_responsible',
            'administrative_responsible', 'manager', 'extra_concerned_people',
            'IAnalyticBudget.projection', 'IAnalyticBudget.analytic_budget', 'budget', 'budget_comments',
            'ISustainableDevelopmentGoals.sdgs', 'observation', 'comments'
        ]
        self.a_fields = [
            'IDublinCore.title', 'description_rich', 'reference_number', 'categories', 'plan',
            'result_indicator', 'planned_end_date', 'planned_begin_date', 'effective_begin_date',
            'effective_end_date', 'progress', 'health_indicator', 'health_indicator_details',
            'representative_responsible', 'manager', 'responsible', 'extra_concerned_people',
            'IAnalyticBudget.projection', 'IAnalyticBudget.analytic_budget', 'budget', 'budget_comments',
            'ISustainableDevelopmentGoals.sdgs', 'observation', 'comments'
        ]
        self.os_columns = [
            u'select_row', u'pretty_link', u'review_state', u'categories', u'ModificationDate', u'history_actions'
        ]
        self.oo_columns = [
            u'select_row', u'pretty_link', u'parents', u'review_state', u'manager', u'planned_end_date', u'priority',
            u'categories', u'sdgs', u'ModificationDate', u'history_actions'
        ]
        self.a_columns = [
            u'select_row', u'pretty_link', u'parents', u'review_state', u'manager', u'responsible',
            u'planned_begin_date', u'planned_end_date', u'effective_begin_date', u'effective_end_date', u'progress',
            u'health_indicator', u'sdgs', u'ModificationDate', u'history_actions'
        ]
        self.so_bdg_states = ['ongoing', 'achieved']
        self.oo_bdg_states = ['ongoing', 'achieved']
        self.a_bdg_states = ['ongoing', 'terminated', 'to_be_scheduled']

        # tests setup
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os1 = self.pst['etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient']
        self.oo1 = self.os1['diminuer-le-temps-dattente-de-lusager-au-guichet-population-de-20-dans-les-12-mois'
                            '-a-venir']
        self.ac1 = self.oo1['engager-2-agents-pour-le-service-population']
        self.tk1 = self.ac1['ajouter-une-annonce-sur-le-site-internet']
        act_srv = [u'cellule-marches-publics', u'secretariat-communal', u'service-etat-civil', u'service-informatique',
                   u'service-proprete', u'service-population', u'service-travaux', u'service-de-lurbanisme']
        srv_obj = self.portal['contacts']['plonegroup-organization']['services']
        self.groups = dict([(srv, srv_obj[srv].UID().decode('utf8')) for srv in act_srv])

    def login(self, username):
        logout()
        login(self.portal, username)


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = PST_TEST_PROFILE_FUNCTIONAL

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.portal = self.layer['portal']
